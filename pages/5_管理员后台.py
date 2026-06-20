# pages/5_管理员后台.py 完整版 含日志弹幕举报 + 回收站软删除
import streamlit as st
import os
from db_utils import db_query, db_execute, write_log

# 兜底初始化session防止属性报错
def init_admin_session():
    if "login_status" not in st.session_state:
        st.session_state.login_status = False
    if "is_admin" not in st.session_state:
        st.session_state.is_admin = False
init_admin_session()

# 权限拦截
if not st.session_state.login_status:
    st.error("请先登录账号")
    st.stop()
if not st.session_state.is_admin:
    st.error("当前账号无管理员权限，禁止访问后台")
    st.stop()

st.header("🔧 管理员运营后台")
st.divider()
# 6个Tab完整对应变量，不会丢失页面
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "视频审核管理",
    "评论管理",
    "用户管理",
    "数据统计看板",
    "日志&举报弹幕管理",
    "🗑️ 回收站（已删除视频）"
])

# ========== Tab1 视频审核 ==========
with tab1:
    all_video = db_query("SELECT * FROM video")
    st.subheader("全站视频列表（0待审核 1已上线 2已下架 | is_delete=1代表已移入回收站）")
    st.dataframe(all_video[["id","title","category","upload_user","play_count","status","is_delete","upload_time"]], use_container_width=True)
    st.divider()
    edit_id = st.number_input("输入操作视频ID", min_value=1, step=1)
    op_type = st.selectbox("操作类型", ["审核通过", "视频下架", "移入回收站(软删除)"])
    if st.button("执行操作", type="primary"):
        if op_type == "审核通过":
            db_execute("UPDATE video SET status=1 WHERE id=?", (edit_id,))
            write_log("视频审核", st.session_state.username, f"管理员审核通过视频{edit_id}")
            st.success(f"视频{edit_id}已审核上线！")
        elif op_type == "视频下架":
            db_execute("UPDATE video SET status=2 WHERE id=?", (edit_id,))
            write_log("视频下架", st.session_state.username, f"管理员下架视频{edit_id}")
            st.warning(f"视频{edit_id}已下架")
        elif op_type == "移入回收站(软删除)":
            db_execute("UPDATE video SET is_delete=1 WHERE id=?", (edit_id,))
            write_log("移入回收站", st.session_state.username, f"管理员将视频{edit_id}移入回收站")
            st.warning(f"视频{edit_id}已标记删除，首页不再展示，可在回收站恢复/永久删除")
        st.rerun()

# ========== Tab2 评论管理 ==========
with tab2:
    comment_df = db_query("SELECT * FROM comment ORDER BY comment_time DESC")
    st.subheader("全站所有评论")
    st.dataframe(comment_df, use_container_width=True)
    del_cid = st.number_input("输入要删除的评论ID", min_value=1)
    if st.button("删除违规评论"):
        db_execute("DELETE FROM comment WHERE id=?", (del_cid,))
        write_log("删除评论", st.session_state.username, f"删除评论ID：{del_cid}")
        st.success("评论删除完成")
        st.rerun()

# ========== Tab3 用户管理 ==========
with tab3:
    user_df = db_query("SELECT id,username,is_admin,register_time FROM user")
    st.subheader("全站用户列表")
    st.dataframe(user_df, use_container_width=True)

# ========== Tab4 数据统计看板 ==========
with tab4:
    total_video = db_query("SELECT COUNT(id) num FROM video").iloc[0,0]
    online_video = db_query("SELECT COUNT(id) num FROM video WHERE status=1 AND is_delete=0").iloc[0,0]
    total_user = db_query("SELECT COUNT(id) num FROM user").iloc[0,0]
    total_play = db_query("SELECT IFNULL(SUM(play_count),0) num FROM video WHERE is_delete=0").iloc[0,0]
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("全部视频(含回收站)", total_video)
    c2.metric("正常展示上线视频", online_video)
    c3.metric("注册用户数", total_user)
    c4.metric("总播放量(仅正常视频)", total_play)
    cate_df = db_query("SELECT category,COUNT(id) count FROM video WHERE is_delete=0 GROUP BY category")
    st.bar_chart(cate_df, x="category", y="count")

# ========== Tab5 日志&举报弹幕管理（你缺失的页面） ==========
with tab5:
    st.subheader("全站操作日志")
    log_df = db_query("SELECT * FROM operation_log ORDER BY opt_time DESC LIMIT 100")
    st.dataframe(log_df, use_container_width=True)
    st.divider()
    st.subheader("无效资源批量清理工具")
    if st.button("一键清理数据库不存在的视频/封面文件"):
        all_v = db_query("SELECT video_path,cover_path FROM video")
        del_count = 0
        for _, row in all_v.iterrows():
            vp, cp = row["video_path"], row["cover_path"]
            if os.path.exists(vp) is False and os.path.exists(cp):
                os.remove(cp)
                del_count += 1
        write_log("资源清理", st.session_state.username, f"清理无效封面文件{del_count}个")
        st.success(f"清理完成，删除无效封面{del_count}个")
    st.subheader("举报工单")
    report_df = db_query("SELECT * FROM report ORDER BY create_time DESC")
    st.dataframe(report_df, use_container_width=True)
    st.divider()
    st.subheader("弹幕管理")
    del_dm_id = st.number_input("删除弹幕ID", min_value=1)
    if st.button("删除违规弹幕"):
        db_execute("DELETE FROM danmaku WHERE id=?", (del_dm_id,))
        write_log("删除弹幕", st.session_state.username, f"删除弹幕{del_dm_id}")
        st.rerun()

# ========== Tab6 回收站（你缺失的页面） ==========
with tab6:
    st.subheader("🗑️ 回收站 已删除视频列表（is_delete=1）")
    recycle_video = db_query("SELECT * FROM video WHERE is_delete=1 ORDER BY id DESC")
    if recycle_video.empty:
        st.info("回收站暂无已删除视频")
    else:
        st.dataframe(recycle_video[["id","title","category","upload_user","status","upload_time"]], use_container_width=True)
        st.divider()
        rec_id = st.number_input("输入回收站视频ID操作", min_value=1)
        rec_opt = st.selectbox("操作", ["恢复视频", "永久彻底删除视频"])
        if st.button("执行回收站操作", type="primary"):
            if rec_opt == "恢复视频":
                db_execute("UPDATE video SET is_delete=0 WHERE id=?", (rec_id,))
                write_log("恢复视频", st.session_state.username, f"管理员恢复回收站视频{rec_id}")
                st.success(f"视频{rec_id}已恢复，首页可正常展示")
            elif rec_opt == "永久彻底删除视频":
                vid = rec_id
                db_execute("DELETE FROM danmaku WHERE video_id=?", (vid,))
                db_execute("DELETE FROM comment WHERE video_id=?", (vid,))
                db_execute("DELETE FROM collect WHERE video_id=?", (vid,))
                db_execute("DELETE FROM report WHERE target_type='video' AND target_id=?", (vid,))
                db_execute("DELETE FROM video WHERE id=?", (vid,))
                write_log("永久删除视频", st.session_state.username, f"彻底删除视频{vid}及全部关联数据")
                st.error(f"视频{vid}已永久清除，数据不可恢复！")
            st.rerun()
