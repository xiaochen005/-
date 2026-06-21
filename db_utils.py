# db_utils.py 全局数据库工具（完整含encrypt_pwd，启动自动修复数据表）
import sqlite3
import pandas as pd
import hashlib
from datetime import datetime
# 新增：导入并自动执行数据库初始化/字段补齐
import init_db
init_db.init_database()

DB_PATH = "./database/video_web.db"

# 密码MD5加密函数
def encrypt_pwd(raw_pwd: str) -> str:
    return hashlib.md5(raw_pwd.encode("utf-8")).hexdigest()

# 获取数据库连接
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    return conn

# 查询返回DataFrame
def db_query(sql: str, params=()):
    conn = get_conn()
    df = pd.read_sql(sql, conn, params=params)
    conn.close()
    return df

# 增删改执行语句
def db_execute(sql: str, params=()):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(sql, params)
    conn.commit()
    conn.close()

# 写入操作日志
def write_log(opt_type, username, desc):
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sql = "INSERT INTO operation_log(opt_type, username, opt_desc, opt_time) VALUES (?,?,?,?)"
    db_execute(sql, (opt_type, username, desc, time_now))

# 分页查询封装
def page_query(sql_base, page=1, page_size=6, params=()):
    offset = (page - 1) * page_size
    sql = sql_base + f" LIMIT {page_size} OFFSET {offset}"
    return db_query(sql, params)
