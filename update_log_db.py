# update_log_db.py
import sqlite3
from db_utils import encrypt_pwd

DB_PATH = "./database/video_web.db"
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# 操作日志表
cur.execute('''
CREATE TABLE IF NOT EXISTS operation_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    opt_type TEXT NOT NULL,
    username TEXT NOT NULL,
    opt_desc TEXT,
    opt_time TEXT NOT NULL
)
''')

# 给管理员密码加密（原有明文admin/123456升级加密）
cur.execute("SELECT username,password FROM user WHERE username='admin'")
row = cur.fetchone()
if row and row[1] == "123456":
    new_pwd = encrypt_pwd("123456")
    cur.execute("UPDATE user SET password=? WHERE username='admin'", (new_pwd,))
    print("管理员密码已加密，登录密码依旧123456")

conn.commit()
conn.close()
print("日志数据表创建完成")