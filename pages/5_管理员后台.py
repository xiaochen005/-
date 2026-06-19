# pages/5_管理员后台.py
import streamlit as st
import sqlite3
import pandas as pd
import os
import altair as alt

DB_PATH = "./database/video_web.db"

# 权限拦截
if not st.session_state.login_status:
    st.error("请先登录账号")
    st.stop()
if not st.session_state.is_admin:
    st.error("当前账号无管理员权限，禁止访问后台")
    st.stop()

st.header("🔧 管理员运营后台")
st.divider()
tab1, tab2, tab3, tab4 = st.tabs(["视频审核管理", "评论管理", "用户管理", "数据统计看板"])

# ========== Tab1 视频审核、下架、删除 ==========
with tab1:
    conn = sqlite3.connect(DB_PATH)
    all_video = pd.read_sql("SELECT * FROM video", conn)
    conn.close()
    st.subheader("全站视频列表（0待审核 1已上线 2已下架）")
    st.dataframe(all_video[["id","title","category","upload_user","play_count","status","upload_time"]], use_container_width=True)

    st.divider()
    edit_id = st.number_input("输入操作视频ID", min_value=1, step=1)
    op_type = st.selectbox("操作类型", ["审核通过", "视频下架", "彻底删除视频"])
    if st.button("执行操作", type="primary"):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        if op_type == "审核通过":
            cur.execute("UPDATE video SET status=1 WHERE id=?", (edit_id,))
            st.success(f"视频{edit_id}已审核上线！")
        elif op_type == "视频下架":
            cur.execute("UPDATE video SET status=2 WHERE id=?", (edit_id,))
            st.warning(f"视频{edit_id}已下架，用户无法在首页查看")
        elif op_type == "彻底删除视频":
            # 查询文件路径，删除本地视频+封面
            cur.execute("SELECT video_path,cover_path FROM video WHERE id=?", (edit_id,))
            res = cur.fetchone()
            if res:
                v_path, c_path = res
                if os.path.exists(v_path):
                    os.remove(v_path)
                if os.path.exists(c_path):
                    os.remove(c_path)
            cur.execute("DELETE FROM video WHERE id=?", (edit_id,))
            cur.execute("DELETE FROM comment WHERE video_id=?", (edit_id,))
            st.error(f"视频{edit_id}及配套文件、评论已永久删除")
        conn.commit()
        conn.close()
        st.rerun()

# ========== Tab2 评论管理 ==========
with tab2:
    conn = sqlite3.connect(DB_PATH)
    comment_df = pd.read_sql("SELECT * FROM comment ORDER BY comment_time DESC", conn)
    conn.close()
    st.subheader("全站所有评论")
    st.dataframe(comment_df, use_container_width=True)
    del_cid = st.number_input("输入要删除的评论ID", min_value=1)
    if st.button("删除违规评论"):
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("DELETE FROM comment WHERE id=?", (del_cid,))
        conn.commit()
        conn.close()
        st.success("评论删除完成")
        st.rerun()

# ========== Tab3 用户管理 ==========
with tab3:
    conn = sqlite3.connect(DB_PATH)
    user_df = pd.read_sql("SELECT id,username,is_admin,register_time FROM user", conn)
    conn.close()
    st.subheader("全站用户列表")
    st.dataframe(user_df, use_container_width=True)

# ========== Tab4 可视化数据看板 ==========
with tab4:
    conn = sqlite3.connect(DB_PATH)
    total_video = pd.read_sql("SELECT COUNT(id) num FROM video", conn).iloc[0,0]
    online_video = pd.read_sql("SELECT COUNT(id) num FROM video WHERE status=1", conn).iloc[0,0]
    total_user = pd.read_sql("SELECT COUNT(id) num FROM user", conn).iloc[0,0]
    total_play = pd.read_sql("SELECT SUM(play_count) num FROM video", conn).iloc[0,0]
    conn.close()

    c1,c2,c3,c4 = st.columns(4)
    c1.metric("全部视频", total_video)
    c2.metric("已上线视频", online_video)
    c3.metric("注册用户数", total_user)
    c4.metric("总播放量", total_play if total_play else 0)

    # 分类视频统计图表
    conn = sqlite3.connect(DB_PATH)
    cate_df = pd.read_sql("SELECT category,COUNT(id) count FROM video GROUP BY category", conn)
    conn.close()
    chart = alt.Chart(cate_df).mark_bar().encode(x="category",y="count",color="category")
    st.altair_chart(chart, use_container_width=True)