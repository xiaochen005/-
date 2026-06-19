# pages/7_UP主主页.py
import streamlit as st
from db_utils import db_query, db_execute, write_log

st.set_page_config(layout="wide")
if "visit_up_name" not in st.session_state or st.session_state.visit_up_name == "":
    st.warning("请从视频卡片点击UP名称进入主页")
    if st.button("返回首页"):
        st.switch_page("pages/1_首页.py")
    st.stop()
up_name = st.session_state.visit_up_name
login_user = st.session_state.username if st.session_state.login_status else ""

# UP数据统计
video_all = db_query("SELECT * FROM video WHERE upload_user=?", (up_name,))
total_play = db_query("SELECT IFNULL(SUM(play_count),0) total FROM video WHERE upload_user=?", (up_name,)).iloc[0]["total"]
fan_count = db_query("SELECT COUNT(id) cnt FROM follow WHERE up_name=?", (up_name,)).iloc[0]["cnt"]

# 是否已关注
is_follow = False
if login_user:
    follow_check = db_query("SELECT id FROM follow WHERE fan_name=? AND up_name=?", (login_user, up_name))
    is_follow = not follow_check.empty

# 头部信息
st.header(f"{up_name} 的UP主主页")
c1,c2,c3 = st.columns([1,1,1])
c1.metric("投稿作品", len(video_all))
c2.metric("总播放量", total_play)
c3.metric("粉丝", fan_count)

# 关注按钮
if login_user and login_user != up_name:
    if not is_follow:
        if st.button("+ 关注UP主"):
            db_execute("INSERT INTO follow(fan_name,up_name,follow_time) VALUES (?,?,datetime('now','localtime'))",
                       (login_user, up_name))
            write_log("关注UP", login_user, f"关注{up_name}")
            st.rerun()
    else:
        if st.button("取消关注"):
            db_execute("DELETE FROM follow WHERE fan_name=? AND up_name=?", (login_user, up_name))
            write_log("取关UP", login_user, f"取关{up_name}")
            st.rerun()

tab_work, tab_group = st.tabs(["全部作品", "合集"])
# 全部作品
with tab_work:
    if video_all.empty:
        st.info("该UP暂无投稿")
    else:
        cols = st.columns(3)
        for idx, row in video_all.iterrows():
            with cols[idx % 3]:
                st.image(row["cover_path"], use_container_width=True)
                st.subheader(row["title"])
                st.caption(f"{row['category']} 播放{row['play_count']}")
                if st.button(f"播放{row['id']}", key=f"upplay_{row['id']}"):
                    st.session_state.play_video_id = row["id"]
                    st.switch_page("pages/4_播放详情.py")
# 合集
with tab_group:
    group_df = db_query("SELECT * FROM collection_group WHERE upload_user=?", (up_name,))
    if group_df.empty:
        st.info("无合集")
    else:
        for _, g in group_df.iterrows():
            st.subheader(g["group_name"])
            rel_df = db_query("SELECT v.title FROM group_video_rel gv LEFT JOIN video v ON gv.video_id=v.id WHERE gv.group_id=?", (g["id"],))
            for _, vid in rel_df.iterrows():
                st.write(f"- {vid['title']}")