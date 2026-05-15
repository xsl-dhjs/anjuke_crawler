import requests
import parsel
import csv
import logging
import re
import time
import os
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from config import HEADERS, REQUEST_TIMEOUT, REQUEST_DELAY, MAX_RETRIES
from db import insert_data, create_city_table, batch_insert_data
from pypinyin import lazy_pinyin

def city_to_domain(city_name):
    """
    将中文城市名转换为拼音域名
    :param city_name: 中文城市名
    :return: 拼音域名
    """
    pinyin_list = lazy_pinyin(city_name)
    return ''.join(pinyin_list).lower()

def save_to_csv(data, csv_name, headers, mode='a'):
    """
    保存数据到CSV文件（支持增量保存）
    :param data: 数据列表
    :param csv_name: CSV文件名
    :param headers: CSV表头
    :param mode: 写入模式（'w'覆盖，'a'追加）
    """
    file_exists = os.path.exists(csv_name)
    with open(csv_name, mode, newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        if not file_exists or mode == 'w':
            writer.writeheader()
        writer.writerows(data)

@retry(
    stop=stop_after_attempt(MAX_RETRIES),  # 最大重试次数
    wait=wait_exponential(multiplier=1, min=2, max=10),  # 指数退避等待
    retry=retry_if_exception_type((requests.exceptions.RequestException,)),  # 只重试网络异常
    reraise=True  # 最后一次失败后抛出异常
)
def fetch_page(url):
    """
    请求页面（带重试机制）
    :param url: 页面URL
    :return: 响应对象
    """
    resp = requests.get(url=url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()  # 检查HTTP状态码
    return resp

def parse_house_info(div):
    """
    解析单个房源信息
    :param div: 房源DOM元素
    :return: 房源信息字典
    """
    title = div.css(".property-content-title-name::text").get("").strip()
    house_type = ''.join(div.css(".property-content-info-text.property-content-info-attribute > span::text").getall()).strip()
    total_price = ''.join(div.css(".property-price-total> span::text").getall()).strip()
    average_price = div.css(".property-price-average::text").get("").strip()
    info_list = div.css(".property-content-info-text::text").getall()
    info = [i.strip() for i in info_list if i.strip()]
    xiaoqu = div.css(".property-content-info-comm-name::text").get("").strip()
    address = ''.join(div.css(".property-content-info-comm-address > span::text").getall()).strip()

    floor = "未知"
    build_time = "未知"

    if len(info) == 4:
        floor = info[2]
        build_time = info[3]
    elif len(info) == 3 and "年建造" in info[-1]:
        floor = "未知"
        build_time = info[-1]
    elif len(info) == 3 and "层" in info[-1]:
        floor = info[-1]
        build_time = "未知"

    return {
        "标题": title,
        "房型": house_type,
        "总价": total_price,
        "单价": average_price,
        "面积": info[0] if info else "未知",
        "楼层": floor,
        "建造时间": build_time,
        "小区": xiaoqu,
        "位置": address
    }

def start_crawl(num_entry, log, city_entry, count_label, stop_flag):
    """
    开始爬取房源数据
    :param num_entry: 数量输入框控件
    :param log: 日志文本控件
    :param city_entry: 城市输入框控件
    :param count_label: 计数标签控件
    :param stop_flag: 停止标志（列表类型，用于在闭包中修改）
    """
    # 获取输入参数
    city_name = city_entry.get().strip()
    num = num_entry.get().strip()

    # 验证城市名：只能是纯中文
    if not re.match(r"^[\u4e00-\u9fa5]+$", city_name):
        msg = "❌ 请输入纯中文城市名，不能是数字/符号"
        log.insert("end", msg + "\n")
        logging.error(msg)
        log.see("end")
        log.update()
        return

    # 验证城市名不为空
    if not city_name or city_name == "请输入城市中文名":
        msg = "城市名不能为空"
        log.insert("end", msg + "\n")
        logging.error(msg)
        log.see("end")
        log.update()
        return

    # 转换城市名为拼音域名
    city_domain = city_to_domain(city_name)
    create_city_table(city_domain)
    msg = f"✅ 城市域名：{city_name} → {city_domain}"
    log.insert("end", msg + "\n")
    logging.info(msg)
    log.see("end")
    log.update()

    # 验证爬取数量
    try:
        num = int(num)
        if num <= 0:
            msg = "❌ 请输入大于0的数字"
            log.insert("end", msg + "\n")
            logging.error(msg)
            log.see("end")
            log.update()
            return
    except ValueError:
        msg = "请输入要爬取的条数"
        log.insert("end", msg + "\n")
        logging.error(msg)
        log.see("end")
        log.update()
        return

    # 初始化变量
    all_data = []
    page = 1
    current_count = 0
    csv_name = f"{city_name}_房源数据.csv"
    headers_csv = ["标题", "房型", "总价", "单价", "面积", "楼层", "建造时间", "小区", "位置"]
    
    msg = f"✅ 开始爬取，目标 {num} 条"
    log.insert("end", msg + "\n")
    logging.info(msg)
    log.see("end")
    log.update()

    # 如果CSV文件已存在，先删除（避免追加旧数据）
    if os.path.exists(csv_name):
        os.remove(csv_name)

    # 爬取主循环
    while current_count < num and not stop_flag[0]:
        url = f"https://{city_domain}.anjuke.com/sale/p{page}/"
        
        try:
            # 请求页面（带重试机制）
            resp = fetch_page(url)
            selector = parsel.Selector(resp.text)
            div_list = selector.css(".property-content")
            
            # 如果页面为空，再试一次
            if not div_list:
                time.sleep(1)
                resp = fetch_page(url)
                selector = parsel.Selector(resp.text)
                div_list = selector.css(".property-content")
            
            msg = f"正在爬第 {page} 页，获取到 {len(div_list)} 条房源"
            log.insert("end", msg + "\n")
            logging.info(msg)
            log.see("end")
            log.update()
            
            # 解析当前页房源
            page_data = []
            for div in div_list:
                if len(all_data) >= num or stop_flag[0]:
                    break
                
                house_info = parse_house_info(div)
                page_data.append(house_info)
                all_data.append(house_info)
                current_count += 1
                
                # 更新计数标签
                count_label.config(text=f"已爬取：{current_count}/{num}")
                log.master.update()
                logging.info(f"已获取：{house_info['标题']}")
            
            # 增量保存到CSV（每一页保存一次）
            if page_data:
                save_to_csv(page_data, csv_name, headers_csv, mode='a')
                msg = f"✅ 第{page}页数据已保存到CSV"
                log.insert("end", msg + "\n")
                logging.info(msg)
                log.see("end")
                log.update()
            
            # 批量入库（每一页入库一次）
            if page_data:
                success_count = batch_insert_data(page_data, city_domain)
                msg = f"✅ 第{page}页数据已入库，成功{success_count}条"
                log.insert("end", msg + "\n")
                logging.info(msg)
                log.see("end")
                log.update()
            
        except Exception as e:
            msg = f"❌ 第{page}页请求失败：{e}"
            log.insert("end", msg + "\n")
            logging.error(msg)
            log.see("end")
            log.update()
        
        # 翻页并等待
        page += 1
        time.sleep(REQUEST_DELAY)
        log.master.update()

    # 最终保存（确保所有数据都已保存）
    result = all_data[:num]
    
    msg = f"✅ {city_name} 爬取完成！共{len(result)}条"
    log.insert("end", msg + "\n")
    logging.info(msg)
    log.see("end")
    log.update()
    count_label.config(text=f"已爬取：0/0")
