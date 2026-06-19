# update_bilibili_func.py
import sqlite3
from db_utils import encrypt_pwd

DB_PATH = "./database/video_web.db"
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# 1. UP主粉丝关注表
cur.execute('''
CREATE TABLE IF NOT EXISTS follow (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fan_name TEXT NOT NULL,
    up_name TEXT NOT NULL,
    follow_time TEXT NOT NULL,
    UNIQUE(fan_name, up_name)
)
''')

# 2. 弹幕表
cur.execute('''
CREATE TABLE IF NOT EXISTS danmaku (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id INTEGER NOT NULL,
    username TEXT NOT NULL,
    content TEXT NOT NULL,
    play_second REAL NOT NULL,
    color TEXT DEFAULT "#ffffff",
    send_time TEXT NOT NULL,
    FOREIGN KEY(video_id) REFERENCES video(id)
)
''')

# 3. 举报工单表
cur.execute('''
CREATE TABLE IF NOT EXISTS report (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    target_type TEXT NOT NULL,
    target_id INTEGER NOT NULL,
    reporter TEXT NOT NULL,
    report_reason TEXT NOT NULL,
    handle_status INTEGER DEFAULT 0,
    create_time TEXT NOT NULL
)
''')

# 4. 合集分组表
cur.execute('''
CREATE TABLE IF NOT EXISTS collection_group (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_name TEXT NOT NULL,
    upload_user TEXT NOT NULL,
    create_time TEXT NOT NULL
)
''')

# 合集-视频关联中间表
cur.execute('''
CREATE TABLE IF NOT EXISTS group_video_rel (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    video_id INTEGER NOT NULL,
    UNIQUE(group_id, video_id)
)
''')

# 给原有video表新增二级分类字段（不存在则新增，存在不报错）
try:
    cur.execute("ALTER TABLE video ADD COLUMN sub_category TEXT DEFAULT '综合'")
except Exception:
    pass

conn.commit()
conn.close()
print("场景2拓展数据表创建完成，原有阶段六数据保留！")