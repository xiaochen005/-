# pages/6_个人中心.py
import streamlit as st
import sqlite3
import pandas as pd

DB_PATH = "./database/video_web.db"
if not st.session_state.login_status:
    st.error("请先登录")
    if st.button("前往登录"):
        st.switch_page("pages/2_登录注册.py")
    st.stop()
user = st.session_state.username

def db_query(sql, params=()):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql(sql, conn, params=params)
    conn.close()
    return df

st.header(f"👤 {user} 的个人中心")
tab1, tab2 = st.tabs(["我的上传视频", "我的收藏"])

# Tab1 我的上传
with tab1:
    my_upload = db_query("SELECT id,title,category,play_count,status,upload_time FROM video WHERE upload_user=?", (user,))
    if my_upload.empty:
        st.info("暂无上传视频")
    else:
        st.dataframe(my_upload, use_container_width=True)
        del_id = st.number_input("输入视频ID删除", min_value=1)
        if st.button("删除本人视频"):
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT video_path,cover_path FROM video WHERE id=? AND upload_user=?", (del_id, user))
            res = cur.fetchone()
            if res:
                import os
                v_p, c_p = res
                os.remove(v_p) if os.path.exists(v_p) else None
                os.remove(c_p) if os.path.exists(c_p) else None
                cur.execute("DELETE FROM video WHERE id=?", (del_id,))
                cur.execute("DELETE FROM comment WHERE video_id=?", (del_id,))
                conn.commit()
                st.success("删除成功")
            else:
                st.error("视频不存在或不属于你")
            conn.close()
            st.rerun()

# Tab2 我的收藏（阶段五新增）
with tab2:
    collect_sql = """
    SELECT v.id, v.title, v.category, v.cover_path, v.play_count 
    FROM collect c 
    LEFT JOIN video v ON c.video_id = v.id 
    WHERE c.username=? AND v.status=1
    """
    collect_df = db_query(collect_sql, (user,))
    if collect_df.empty:
        st.info("你还没有收藏任何视频，去首页收藏喜欢的视频吧")
    else:
        cols = st.columns(3)
        for idx, row in collect_df.iterrows():
            with cols[idx % 3]:
                st.image(row["cover_path"], use_container_width=True)
                st.subheader(row["title"])
                st.caption(f"{row['category']} 播放：{row['play_count']}")
                if st.button(f"播放{row['id']}", key=f"col_{row['id']}"):
                    st.session_state.play_video_id = row["id"]
                    st.switch_page("pages/4_播放详情.py")