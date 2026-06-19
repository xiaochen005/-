# check_project.py 项目上线自检工具
import os
import sqlite3
from db_utils import db_query

def check_dir():
    dirs = ["database","static/videos","static/cover","static/css","pages"]
    for d in dirs:
        if os.path.exists(d):
            print(f"✅ 目录正常：{d}")
        else:
            print(f"❌ 缺失目录：{d}")

def check_db():
    db_path = "./database/video_web.db"
    if not os.path.exists(db_path):
        print("❌ 数据库文件不存在")
        return
    print("✅ 数据库文件存在")
    tables = ["user","video","comment","collect","operation_log"]
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    for t in tables:
        cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{t}'")
        if cur.fetchone():
            print(f"✅ 数据表{t}正常")
        else:
            print(f"❌ 缺失数据表{t}")
    conn.close()

if __name__ == "__main__":
    print("===== 目录检测 =====")
    check_dir()
    print("\n===== 数据库检测 =====")
    check_db()
    print("\n自检完成，无❌即可部署上线")