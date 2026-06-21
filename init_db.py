# init_db.py 兼容旧表自动补字段完整版
import sqlite3
import os
from datetime import datetime

DB_PATH = "./database/video_web.db"

def init_database():
    # 自动创建database文件夹
    os.makedirs("./database", exist_ok=True)
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

    # 2. 视频基础表（旧表存在不会覆盖，后续自动补字段）
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

    # 核心逻辑：自动检测video表缺失字段并新增
    cursor.execute("PRAGMA table_info(video);")
    all_cols = [row[1] for row in cursor.fetchall()]

    # 补二级分类 sub_category
    if "sub_category" not in all_cols:
        cursor.execute("ALTER TABLE video ADD COLUMN sub_category TEXT;")
    # 补软删除标记 is_delete，默认0未删除
    if "is_delete" not in all_cols:
        cursor.execute("ALTER TABLE video ADD COLUMN is_delete INTEGER DEFAULT 0;")

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

    # 4. 弹幕表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS danmaku (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        video_id INTEGER,
        username TEXT,
        content TEXT,
        play_second REAL,
        color TEXT,
        send_time TEXT
    )
    ''')

    # 5. 收藏表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS collect (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        video_id INTEGER,
        collect_time TEXT
    )
    ''')

    # 6. 举报工单表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS report (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        target_type TEXT,
        target_id INTEGER,
        reporter TEXT,
        report_reason TEXT,
        handle_status INTEGER DEFAULT 0,
        create_time TEXT
    )
    ''')

    # 7. 操作日志表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS operation_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        opt_type TEXT,
        opt_user TEXT,
        opt_content TEXT,
        opt_time TEXT
    )
    ''')

    # 8. 合集分组表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS collection_group (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_name TEXT,
        upload_user TEXT,
        create_time TEXT
    )
    ''')

    # 9. 合集视频关联表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS group_video_rel (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER,
        video_id INTEGER
    )
    ''')

    # 初始化默认管理员账号 admin / 123456
    cursor.execute("SELECT * FROM user WHERE username='admin'")
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO user (username, password, is_admin, register_time) VALUES (?,?,?,?)",
            ("admin", "123456", 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )

    conn.commit()
    conn.close()
    print("✅ 数据库初始化完成，自动补齐sub_category、is_delete字段")

if __name__ == "__main__":
    init_database()
