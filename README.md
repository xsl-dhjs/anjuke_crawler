# 安居客二手房房源数据爬取系统（GUI可视化版）



## 项目简介

基于 Python 开发的安居客二手房房源数据爬取工具，提供可视化 GUI 操作界面，无需编程即可使用。

### 主要功能

- ✅ **可视化操作**：简洁的 GUI 界面，支持输入城市名和爬取数量
- ✅ **多城市支持**：自动将中文城市名转换为拼音域名
- ✅ **数据存储**：支持 MySQL 数据库存储 + CSV 文件导出
- ✅ **实时日志**：实时显示爬取进度和状态信息
- ✅ **异常处理**：自动重试机制，提高稳定性

## 技术栈

| 模块       | 用途       |
| -------- | -------- |
| Python 3 | 编程语言     |
| Tkinter  | GUI 界面   |
| requests | 网络请求     |
| parsel   | HTML 解析  |
| PyMySQL  | MySQL 驱动 |
| pypinyin | 中文转拼音    |
| tenacity | 重试机制     |
| DBUtils  | 数据库连接池   |

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境

创建 `.env` 文件（可参考 `.env.example`）：

```env
# 数据库配置
DB_HOST=localhost
DB_USER=root
DB_PWD=your_password
DB_NAME=anjuke_crawler
DB_CHARSET=utf8mb4

# 请求配置
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
COOKIE=your_cookie_here
REQUEST_TIMEOUT=10
REQUEST_DELAY=0.8
MAX_RETRIES=3
```

### 3. 运行项目

```bash
python main.py
```

### 4. 使用说明

1. 在 GUI 界面输入城市中文名（如：北京、上海、广州）
2. 输入要爬取的房源数量
3. 点击「开始爬取」按钮
4. 等待爬取完成，数据将自动保存到：
   - MySQL 数据库（表名 = 城市拼音）
   - CSV 文件（格式：`{城市名}_房源数据.csv`）

## 项目结构

```
anjuke_crawler/
├── main.py          # GUI 主程序入口
├── crawler.py       # 爬取核心逻辑
├── db.py            # 数据库操作（连接池、建表、插入）
├── config.py        # 配置文件（加载 .env）
├── requirements.txt # 依赖清单
├── .env.example     # 环境变量示例
├── .env             # 环境变量配置（需自行创建）
└── crawl.log        # 运行日志（自动生成）
```

## 数据字段说明

| 字段   | 说明   | 示例           |
| ---- | ---- | ------------ |
| 标题   | 房源标题 | 望京SOHO附近精装两居 |
| 房型   | 房屋户型 | 2室1厅1卫       |
| 总价   | 房屋总价 | 320万         |
| 单价   | 房屋单价 | 42000元/㎡     |
| 面积   | 建筑面积 | 76.2㎡        |
| 楼层   | 所在楼层 | 中层/共28层      |
| 建造时间 | 建成年份 | 2015年建造      |
| 小区   | 小区名称 | 望京新城         |
| 位置   | 详细地址 | 朝阳-望京        |

## 注意事项

1. 使用前请确保已安装 MySQL 数据库并创建对应数据库
2. 建议设置合理的 `REQUEST_DELAY`（请求间隔），避免对目标网站造成压力
3. 如遇到爬取失败，可尝试更新 `COOKIE` 值
4. 本工具仅用于学习和研究目的，请遵守目标网站的 robots.txt 规则

## 许可证

MIT License

## 作者

Python 编程项目实战
