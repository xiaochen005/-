# pages/3_视频上传.py
import streamlit as st
import sqlite3
import os
from datetime import datetime
from moviepy import VideoFileClip

DB_PATH = "./database/video_web.db"
VIDEO_SAVE_PATH = "./static/videos/"
COVER_SAVE_PATH = "./static/cover/"

# 权限校验
if not st.session_state.login_status:
    st.error("登录后才能上传视频")
    if st.button("去登录"):
        st.switch_page("pages/2_登录注册.py")
    st.stop()

st.header("📤 上传新视频")
st.divider()

# 表单
title = st.text_input("视频标题", max_chars=60)
intro = st.text_area("视频简介", max_chars=300)
category = st.selectbox("分类", ["生活","科技","游戏","影视","教程","其他"])
video_file = st.file_uploader("上传视频(mp4/mov)", type=["mp4","mov"])

# 自动生成封面函数
def create_cover(video_local_path, cover_save_name):
    clip = VideoFileClip(video_local_path)
    # 截取第1秒画面作为封面
    frame = clip.get_frame(1)
    from PIL import Image
    img = Image.fromarray(frame)
    img.save(os.path.join(COVER_SAVE_PATH, cover_save_name))
    clip.close()
    return os.path.join(COVER_SAVE_PATH, cover_save_name)

# 提交上传
if st.button("确认上传", type="primary"):
    if not title or not video_file:
        st.warning("标题和视频文件必填！")
    else:
        # 生成唯一文件名
        time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_name = f"{time_str}_{video_file.name}"
        cover_name = f"{time_str}_cover.jpg"
        full_video_path = os.path.join(VIDEO_SAVE_PATH, video_name)

        # 保存视频文件到本地
        with open(full_video_path, "wb") as f:
            f.write(video_file.read())
        
        # 自动截取封面
        cover_path = create_cover(full_video_path, cover_name)

        # 写入数据库
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cur.execute('''
        INSERT INTO video(title,intro,category,video_path,cover_path,upload_user,status,upload_time)
        VALUES (?,?,?,?,?,?,0,?)
        ''', (title, intro, category, full_video_path, cover_path, st.session_state.username, upload_time))
        conn.commit()
        conn.close()

        st.success("上传成功！等待管理员审核后即可展示")
        st.rerun()