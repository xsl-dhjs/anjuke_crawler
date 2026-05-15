import tkinter as tk
from tkinter import scrolledtext, messagebox
import logging
import threading
from crawler import start_crawl

# 配置日志输出到文件
logging.basicConfig(
    filename="crawl.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

# 全局变量：爬取线程
crawl_thread = None
# 线程锁，用于保护共享变量
thread_lock = threading.Lock()

def create_gui():
    """
    创建GUI界面
    :return: Tk根窗口对象
    """
    root = tk.Tk()
    root.title("全国安居客房源爬虫 - 改进版")
    root.geometry("500x400")

    # 城市输入框
    tk.Label(root, text="城市中文名：").place(x=30, y=20)
    city_entry = tk.Entry(root, fg="gray")
    city_entry.place(x=100, y=20, width=110)
    city_entry.insert(0, "请输入城市中文名")

    def clear_city_hint(event):
        """清除城市输入框提示文字"""
        if city_entry.get() == "请输入城市中文名":
            city_entry.delete(0, tk.END)
            city_entry.config(fg="black")
    city_entry.bind("<FocusIn>", clear_city_hint)

    # 数量输入框
    tk.Label(root, text="爬取数量：").place(x=220, y=20)
    num_entry = tk.Entry(root, fg="gray")
    num_entry.place(x=280, y=20, width=110)
    num_entry.insert(0, "请输入爬取数量")

    def clear_num_hint(event):
        """清除数量输入框提示文字"""
        if num_entry.get() == "请输入爬取数量":
            num_entry.delete(0, tk.END)
            num_entry.config(fg="black")
    num_entry.bind("<FocusIn>", clear_num_hint)

    # 爬取进度标签
    count_label = tk.Label(root, text="已爬取：0/0", font=("Arial", 10, "bold"))
    count_label.place(x=30, y=50)

    # 停止标志（使用列表以便在闭包中修改）
    stop_flag = [False]

    def stop_crawl():
        """停止爬取"""
        with thread_lock:
            stop_flag[0] = True
        messagebox.showinfo("提示", "已发送停止信号，请等待当前页处理完成")

    def start_crawl_thread():
        """在新线程中启动爬取任务"""
        global crawl_thread
        
        # 检查是否已有线程在运行
        with thread_lock:
            if crawl_thread and crawl_thread.is_alive():
                messagebox.showwarning("警告", "爬取任务正在进行中，请先停止或等待完成")
                return
            # 重置停止标志
            stop_flag[0] = False
        
        # 禁用开始按钮，启用停止按钮
        start_btn.config(state=tk.DISABLED)
        stop_btn.config(state=tk.NORMAL)
        
        # 定义线程任务
        def crawl_task():
            try:
                start_crawl(num_entry, log, city_entry, count_label, stop_flag)
            finally:
                # 任务完成后恢复按钮状态
                root.after(0, lambda: start_btn.config(state=tk.NORMAL))
                root.after(0, lambda: stop_btn.config(state=tk.DISABLED))
        
        # 创建并启动线程
        crawl_thread = threading.Thread(target=crawl_task, daemon=True)
        crawl_thread.start()

    # 开始按钮
    start_btn = tk.Button(
        root, text="开始爬取",
        command=start_crawl_thread,
        bg="#28a745", fg="white", width=12
    )
    start_btn.place(x=160, y=80)

    # 停止按钮
    stop_btn = tk.Button(
        root, text="停止爬取",
        command=stop_crawl,
        bg="#dc3545", fg="white", width=12,
        state=tk.DISABLED  # 初始禁用
    )
    stop_btn.place(x=280, y=80)

    # 日志标签
    tk.Label(root, text="运行日志：").place(x=30, y=120)
    
    # 日志文本框
    log = scrolledtext.ScrolledText(root, width=58, height=14)
    log.place(x=30, y=145)

    return root

if __name__ == "__main__":
    # 创建并运行GUI
    root = create_gui()
    root.mainloop()
