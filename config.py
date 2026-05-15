import os
from dotenv import load_dotenv

# 加载 .env 配置文件
load_dotenv()

# 全局请求头配置
HEADERS = {
    "user-agent": os.getenv("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36"),
    "cookie": os.getenv("COOKIE", ""),
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "zh-CN,zh;q=0.9"
}

# 数据库配置
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PWD = os.getenv("DB_PWD", "")
DB_NAME = os.getenv("DB_NAME", "test")
DB_CHARSET = os.getenv("DB_CHARSET", "utf8mb4")

# 爬虫配置
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))
REQUEST_DELAY = float(os.getenv("REQUEST_DELAY", "0.8"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
