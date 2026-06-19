# update_db.py
import sqlite3
DB_PATH = "./database/video_web.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
# 新增收藏表：用户+视频唯一约束，防止重复收藏
cur.execute('''
CREATE TABLE IF NOT EXISTS collect (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    video_id INTEGER NOT NULL,
    collect_time TEXT NOT NULL,
    UNIQUE(username, video_id),
    FOREIGN KEY(video_id) REFERENCES video(id)
)
''')
conn.commit()
conn.close()
print("收藏数据表更新完成！")