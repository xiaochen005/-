# pages/1_首页.py
import streamlit as st
from db_utils import page_query, db_query

st.set_page_config(page_title="视频广场", layout="wide")

@st.cache_data(ttl=60)
def get_total_count(search_key="", cate="全部"):
    sql = "SELECT COUNT(id) total FROM video WHERE status=1"
    params = []
    if cate != "全部":
        sql += " AND category=?"
        params.append(cate)
    if search_key.strip():
        sql += " AND (title LIKE ? OR intro LIKE ?)"
        params.extend([f"%{search_key}%", f"%{search_key}%"])
    df = db_query(sql, params)
    return int(df.iloc[0]["total"])

# 页面头部
st.header("🏠 视频广场")
st.divider()
col_search, col_cate, col_sort = st.columns([3,1,1])
with col_search:
    search_text = st.text_input("🔍 搜索标题/简介", placeholder="输入关键词")
with col_cate:
    cate_list = ["全部", "生活", "科技", "游戏", "影视", "教程", "其他"]
    select_cate = st.selectbox("分类筛选", cate_list)
with col_sort:
    sort_opt = st.radio("排序", ["最新上传", "最热播放"])
sort_sql = "ORDER BY upload_time DESC" if sort_opt == "最新上传" else "ORDER BY play_count DESC"

# 分页控件
page_size = 6
if "page" not in st.session_state:
    st.session_state.page = 1
total = get_total_count(search_text, select_cate)
max_page = (total + page_size - 1) // page_size if total > 0 else 1

col_p1, col_p2, col_p3 = st.columns([1,1,1])
with col_p1:
    if st.button("上一页") and st.session_state.page > 1:
        st.session_state.page -= 1
        st.rerun()
with col_p2:
    st.write(f"第 {st.session_state.page} / {max_page} 页，共{total}个视频")
with col_p3:
    if st.button("下一页") and st.session_state.page < max_page:
        st.session_state.page += 1
        st.rerun()

# 分页查询视频
base_sql = f"""
SELECT id, title, intro, category, cover_path, play_count, like_count, upload_time 
FROM video WHERE status=1
"""
params = []
if select_cate != "全部":
    base_sql += " AND category=?"
    params.append(select_cate)
if search_text.strip():
    base_sql += " AND (title LIKE ? OR intro LIKE ?)"
    params.extend([f"%{search_text}%", f"%{search_text}%"])
base_sql += f" {sort_sql}"
df_video = page_query(base_sql, page=st.session_state.page, page_size=page_size, params=params)

if df_video.empty:
    st.warning("暂无匹配视频，更换筛选条件或等待新视频上传")
else:
    cols = st.columns(3)
    for idx, row in df_video.iterrows():
        with cols[idx % 3]:
            st.image(row["cover_path"], use_container_width=True)
            st.subheader(row["title"])
            st.caption(f"分类：{row['category']} | 播放：{row['play_count']}")
            brief = row["intro"][:30] + "..." if len(row["intro"]) > 30 else row["intro"]
            st.text(brief)
            if st.button(f"播放视频{row['id']}", key=f"play_{row['id']}"):
                st.session_state.play_video_id = row["id"]
                st.switch_page("pages/4_播放详情.py")