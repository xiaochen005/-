# pages/4_播放详情.py 阶段六升级弹幕+举报+OSS外网播放
import streamlit as st
from datetime import datetime
from db_utils import db_query, db_execute, write_log

DB_PATH = "./database/video_web.db"
if "play_video_id" not in st.session_state or st.session_state.play_video_id is None:
    st.warning("未选中视频，请返回首页")
    if st.button("返回首页"):
        st.switch_page("pages/1_首页.py")
    st.stop()
vid = st.session_state.play_video_id
login_user = st.session_state.username if st.session_state.login_status else ""

# 播放量+1（阶段六原有逻辑保留）
db_execute("UPDATE video SET play_count=play_count+1 WHERE id=?", (vid,))
video_df = db_query("SELECT * FROM video WHERE id=?", (vid,))
if video_df.empty:
    st.error("视频不存在")
    st.stop()
video = video_df.iloc[0]
v_url = video["video_path"]
c_url = video["cover_path"]
up_user = video["upload_user"]

# 页面渲染
st.header(video["title"])
st.image(c_url, width=900, use_container_width=True)
# OSS外网视频播放器
st.video(v_url)

# 跳转UP主页按钮
if st.button(f"进入UP主页：{up_user}"):
    st.session_state.visit_up_name = up_user
    st.switch_page("pages/7_UP主主页.py")

st.write(f"一级分区：{video['category']}｜二级：{video['sub_category']}｜播放量：{video['play_count']}｜点赞：{video['like_count']}｜收藏：{video['collect_count']}")
st.text_area("简介", value=video["intro"], disabled=True)
st.divider()

# 点赞、收藏、举报三栏
col1, col2, col3 = st.columns(3)
# 点赞（阶段六原有）
with col1:
    if st.button("👍 点赞"):
        db_execute("UPDATE video SET like_count=like_count+1 WHERE id=?", (vid,))
        st.rerun()
# 收藏（阶段六原有）
with col2:
    if login_user:
        collect_df = db_query("SELECT id FROM collect WHERE username=? AND video_id=?", (login_user, vid))
        if collect_df.empty:
            if st.button("⭐ 收藏"):
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                db_execute("INSERT INTO collect(username,video_id,collect_time) VALUES (?,?,?)", (login_user, vid, now))
                db_execute("UPDATE video SET collect_count=collect_count+1 WHERE id=?", (vid,))
                st.rerun()
        else:
            if st.button("⭐ 取消收藏"):
                db_execute("DELETE FROM collect WHERE username=? AND video_id=?", (login_user, vid))
                db_execute("UPDATE video SET collect_count=collect_count-1 WHERE id=?", (vid,))
                st.rerun()
    else:
        st.info("登录后收藏")
# 新增举报功能
with col3:
    report_reason = st.text_input("举报理由")
    if st.button("提交举报") and login_user and report_reason.strip():
        db_execute("INSERT INTO report(target_type,target_id,reporter,report_reason,handle_status,create_time) VALUES ('video',?,?,?,0,datetime('now','localtime'))",
                   (vid, login_user, report_reason))
        st.success("举报已提交")
st.divider()

# 新增弹幕模块
st.subheader("弹幕")
danmaku_df = db_query("SELECT * FROM danmaku WHERE video_id=? ORDER BY play_second ASC", (vid,))
for _, dm in danmaku_df.iterrows():
    st.markdown(f"<span style='color:{dm['color']}'>{dm['play_second']}s : {dm['content']}</span>", unsafe_allow_html=True)

if login_user:
    dm_text = st.text_input("发送弹幕")
    dm_sec = st.number_input("弹幕时间点(秒)", min_value=0, value=10)
    dm_color = st.color_picker("弹幕颜色", "#ffffff")
    if st.button("发送弹幕") and dm_text.strip():
        db_execute("INSERT INTO danmaku(video_id,username,content,play_second,color,send_time) VALUES (?,?,?,?,?,datetime('now','localtime'))",
                   (vid, login_user, dm_text, dm_sec, dm_color))
        write_log("发送弹幕", login_user, f"视频{vid}弹幕：{dm_text}")
        st.rerun()

# 评论区（阶段六原有逻辑完全保留）
st.subheader("评论区")
comment_df = db_query("SELECT username,content,comment_time FROM comment WHERE video_id=? ORDER BY comment_time DESC", (vid,))
for _, row in comment_df.iterrows():
    st.markdown(f"**{row['username']}** ({row['comment_time']})：{row['content']}")
if login_user:
    comment_text = st.text_input("发表评论")
    if st.button("发布") and comment_text.strip():
        db_execute("INSERT INTO comment(video_id,username,content,comment_time) VALUES (?,?,?,datetime('now','localtime'))",
                   (vid, login_user, comment_text))
        st.rerun()