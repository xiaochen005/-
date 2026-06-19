# init_db.py 数据库初始化脚本
import sqlite3
import os
from datetime import datetime

# 数据库文件路径
DB_PATH = "./database/video_web.db"

def init_database():
    # 连接数据库（不存在则自动创建）
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. 用户数据表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            register_time TEXT NOT NULL
        )
    ''')

    # 2. 视频数据表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS video (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            intro TEXT,
            category TEXT NOT NULL,
            video_path TEXT NOT NULL,
            cover_path TEXT NOT NULL,
            play_count INTEGER DEFAULT 0,
            like_count INTEGER DEFAULT 0,
            collect_count INTEGER DEFAULT 0,
            upload_user TEXT NOT NULL,
            status INTEGER DEFAULT 0,
            upload_time TEXT NOT NULL
        )
    ''')
    # status状态：0=待审核，1=已上线，2=已下架

    # 3. 评论数据表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            content TEXT NOT NULL,
            comment_time TEXT NOT NULL,
            FOREIGN KEY (video_id) REFERENCES video(id)
        )
    ''')

    # 初始化默认管理员账号（账号：admin 密码：123456）
    cursor.execute("SELECT * FROM user WHERE username='admin'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO user (username, password, is_admin, register_time) VALUES (?,?,?,?)",
            ("admin", "123456", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )

    conn.commit()
    conn.close()
    print("✅ 数据库初始化完成，默认管理员账号：admin / 123456")

if __name__ == "__main__":
    init_database()