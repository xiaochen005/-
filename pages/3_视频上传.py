# pages/3_视频上传.py 阶段六升级OSS云端投稿版（已移除moviepy）
import streamlit as st
import os
import cv2
from datetime import datetime
from PIL import Image
from db_utils import db_execute, write_log, db_query
from oss_upload import upload_file_to_oss

MAX_SIZE_MB = 200

# 登录拦截（阶段六原有逻辑保留）
if not st.session_state.login_status:
    st.error("登录后上传视频")
    if st.button("登录页面"):
        st.switch_page("pages/2_登录注册.py")
    st.stop()
current_user = st.session_state.username

st.header("📤 UP主投稿中心")
st.info(f"仅支持 mp4/mov，文件最大 {MAX_SIZE_MB}MB，资源自动上传阿里云OSS，外网可播放")

# 读取当前用户合集
group_df = db_query("SELECT id,group_name FROM collection_group WHERE upload_user=?", (current_user,))
tab_upload, tab_create_group = st.tabs(["投稿视频", "新建合集"])

# 新建合集
with tab_create_group:
    g_name = st.text_input("合集名称")
    if st.button("创建合集") and g_name.strip():
        db_execute("INSERT INTO collection_group(group_name,upload_user,create_time) VALUES (?,?,datetime('now','localtime'))",
                   (g_name, current_user))
        write_log("创建合集", current_user, f"新建合集：{g_name}")
        st.rerun()

# 投稿表单
with tab_upload:
    title = st.text_input("视频标题", max_chars=60)
    intro = st.text_area("简介", max_chars=300)
    cate_main = st.selectbox("一级分区", ["生活","科技","游戏","影视","教程","动画","其他"])
    cate_sub = st.text_input("二级子分类")
    video_file = st.file_uploader("上传视频", type=["mp4", "mov"])
    group_opt = st.selectbox("归入合集", ["无合集"] + list(group_df["group_name"]) if not group_df.empty else ["无合集"])

    # 【替换moviepy，改用opencv生成封面】
    def make_local_cover(vid_path, cover_name):
        temp_dir = "./static/tmp"
        os.makedirs(temp_dir, exist_ok=True)
        cover_path = os.path.join(temp_dir, cover_name)
        cap = cv2.VideoCapture(vid_path)
        # 读取第1秒画面，避免黑屏
        cap.set(cv2.CAP_PROP_POS_MSEC, 1000)
        ret, frame = cap.read()
        if ret:
            cv2.imwrite(cover_path, frame)
        cap.release()
        return cover_path

    if st.button("确认投稿", type="primary"):
        try:
            if not title or not video_file:
                st.warning("标题和视频必填")
                st.stop()
            file_mb = video_file.size / 1024 / 1024
            if file_mb > MAX_SIZE_MB:
                st.error(f"文件超过{MAX_SIZE_MB}MB限制")
                st.stop()

            time_tag = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_vid = f"./static/tmp/{time_tag}_{video_file.name}"
            with open(temp_vid, "wb") as f:
                f.write(video_file.read())

            # 生成封面并上传OSS
            cover_local = make_local_cover(temp_vid, f"{time_tag}_cover.jpg")
            video_oss_url = upload_file_to_oss(temp_vid, "video")
            cover_oss_url = upload_file_to_oss(cover_local, "cover")

            # 写入数据库（新增sub_category二级分类）
            up_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            db_execute("""
            INSERT INTO video(title,intro,category,sub_category,video_path,cover_path,upload_user,status,upload_time,collect_count,like_count,play_count)
            VALUES (?,?,?,?,?,?,?,0,?,0,0,0)
            """, (title, intro, cate_main, cate_sub, video_oss_url, cover_oss_url, current_user, up_time))

            # 绑定合集
            if group_opt != "无合集":
                g_id = group_df[group_df["group_name"] == group_opt]["id"].iloc[0]
                new_vid_id = db_query("SELECT id FROM video ORDER BY id DESC LIMIT 1").iloc[0]["id"]
                db_execute("INSERT INTO group_video_rel(group_id,video_id) VALUES (?,?)", (g_id, new_vid_id))

            write_log("视频上传", current_user, f"投稿视频：{title}")
            st.success("投稿成功，等待管理员审核，外网可直接播放！")
            st.rerun()
        except Exception as err:
            st.error(f"上传失败：{str(err)}")