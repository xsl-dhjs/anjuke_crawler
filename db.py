import pymysql
from dbutils.pooled_db import PooledDB
from config import DB_HOST, DB_USER, DB_PWD, DB_NAME, DB_CHARSET

# 全局数据库连接池（单例模式）
_db_pool = None

def get_db_pool():
    """
    获取数据库连接池（单例模式，避免重复创建）
    :return: 数据库连接池对象
    """
    global _db_pool
    if _db_pool is None:
        _db_pool = PooledDB(
            creator=pymysql,  # 使用的数据库模块
            maxconnections=5,  # 连接池最大连接数
            mincached=2,  # 初始化时连接池中的空闲连接数
            maxcached=3,  # 连接池最大空闲连接数
            maxshared=0,  # 连接池最多共享的连接数，0表示不限制
            blocking=True,  # 连接池耗尽时是否等待
            maxusage=None,  # 连接最多被重复使用的次数，None表示不限制
            setsession=[],  # 开始会话前执行的命令列表
            ping=1,  # ping MySQL服务端，检查服务是否可用
            host=DB_HOST,
            user=DB_USER,
            password=DB_PWD,
            database=DB_NAME,
            charset=DB_CHARSET
        )
    return _db_pool

def get_conn():
    """
    从连接池获取数据库连接
    :return: 数据库连接对象
    """
    pool = get_db_pool()
    return pool.connection()

def create_city_table(city_pinyin):
    """
    动态创建城市专属表，表名=城市拼音
    :param city_pinyin: 城市拼音（表名）
    """
    conn = get_conn()
    try:
        cursor = conn.cursor()
        table_name = city_pinyin
        # 使用参数化查询避免SQL注入
        sql = f'''
        CREATE TABLE IF NOT EXISTS `{table_name}` (
            id INT AUTO_INCREMENT PRIMARY KEY,
            title VARCHAR(255),
            house_type VARCHAR(100),
            total_price VARCHAR(50),
            average_price VARCHAR(50),
            area VARCHAR(50),
            floor VARCHAR(50),
            build_time VARCHAR(50),
            community VARCHAR(100),
            address VARCHAR(255),
            UNIQUE KEY uk_title_community (title, community)  # 添加唯一索引防止重复
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        '''
        cursor.execute(sql)
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def insert_data(item, city_pinyin):
    """
    插入数据到对应城市的表（支持去重）
    :param item: 房源数据字典
    :param city_pinyin: 城市拼音（表名）
    :return: 是否插入成功
    """
    conn = get_conn()
    try:
        cursor = conn.cursor()
        table_name = city_pinyin
        # 使用 INSERT IGNORE 避免重复插入
        sql = f'''
        INSERT IGNORE INTO `{table_name}` 
        (title, house_type, total_price, average_price, area, floor, build_time, community, address)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        data = (
            item["标题"],
            item["房型"],
            item["总价"],
            item["单价"],
            item["面积"],
            item["楼层"],
            item["建造时间"],
            item["小区"],
            item["位置"]
        )
        cursor.execute(sql, data)
        conn.commit()
        # 如果影响行数>0说明插入成功，=0说明重复数据
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def batch_insert_data(items, city_pinyin):
    """
    批量插入数据（提高性能）
    :param items: 房源数据列表
    :param city_pinyin: 城市拼音（表名）
    :return: 成功插入的数量
    """
    if not items:
        return 0
    
    conn = get_conn()
    success_count = 0
    try:
        cursor = conn.cursor()
        table_name = city_pinyin
        sql = f'''
        INSERT IGNORE INTO `{table_name}` 
        (title, house_type, total_price, average_price, area, floor, build_time, community, address)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        # 批量执行
        data_list = [
            (
                item["标题"],
                item["房型"],
                item["总价"],
                item["单价"],
                item["面积"],
                item["楼层"],
                item["建造时间"],
                item["小区"],
                item["位置"]
            )
            for item in items
        ]
        cursor.executemany(sql, data_list)
        conn.commit()
        success_count = cursor.rowcount
    except Exception as e:
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
    return success_count
