# main.py
import streamlit as st
from db_utils import db_query

# 全局配置必须放在最顶部
st.set_page_config(
    page_title="视频网站",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 统一初始化所有会话变量
def init_session():
    if "theme" not in st.session_state:
        st.session_state.theme = "light"
    if "login_status" not in st.session_state:
        st.session_state.login_status = False
    if "username" not in st.session_state:
        st.session_state.username = ""
    if "is_admin" not in st.session_state:
        st.session_state.is_admin = False
    if "play_video_id" not in st.session_state:
        st.session_state.play_video_id = None
    if "visit_up_name" not in st.session_state:
        st.session_state.visit_up_name = ""

init_session()

# ====================== 侧边栏区域 ======================
with st.sidebar:
    st.header("🎬 视频网站导航")
    st.divider()

    st.radio(
        "页面主题切换",
        ["light", "dark"],
        key="theme"
    )
    if st.button("应用主题"):
        st.rerun()

    st.divider()

    if st.session_state.login_status:
        st.write(f"欢迎：{st.session_state.username}")
        if st.session_state.is_admin:
            st.success("🔑 管理员账号")
        if st.button("退出登录"):
            st.session_state.login_status = False
            st.session_state.username = ""
            st.session_state.is_admin = False
            st.session_state.play_video_id = None
            st.session_state.visit_up_name = ""
            st.rerun()
    else:
        st.info("游客身份，请登录使用全部功能")

# ====================== 全局CSS样式 ======================
if st.session_state.theme == "dark":
    custom_css = """
    <style>
    .stApp {
        background-color: #0e1117;
        color: #fafafa;
    }
    .stTextInput > div > div > input {
        background-color: #262730;
        color: #fff;
    }
    .stTextArea > div > div > textarea {
        background-color: #262730;
        color: #fff;
    }
    .stSelectbox > div > div > div {
        background-color: #262730;
        color: #fff;
    }
    .stSidebar {
        background-color: #1a1c23;
    }
    </style>
    """
else:
    custom_css = """
    <style>
    .stApp {
        background-color: #ffffff;
        color: #000000;
    }
    .stSidebar {
        background-color: #f7f8fa;
    }
    </style>
    """
st.markdown(custom_css, unsafe_allow_html=True)

# ====================== 主页内容 ======================
st.title("🎬 Streamlit轻量化视频网站")
st.info("左侧切换页面，支持搜索、分类、收藏、点赞评论")
st.divider()

# 关键：只展示审核通过、未被软删除的视频 is_delete = 0
video_df = db_query("""
SELECT id, title, cover_path, category, upload_user, play_count 
FROM video 
WHERE status = 1 AND is_delete = 0 
ORDER BY id DESC
""")

if video_df.empty:
    st.warning("暂无已上架视频，前往投稿页面上传内容")
else:
    cols = st.columns(3)
    for idx, row in video_df.iterrows():
        col = cols[idx % 3]
        with col:
            st.image(row["cover_path"], use_container_width=True)
            st.subheader(row["title"])
            st.caption(f"分区：{row['category']} | UP主：{row['upload_user']}")
            st.caption(f"播放量：{row['play_count']}")
            
            if st.button("▶ 立即播放", key=f"play_key_{row['id']}"):
                st.session_state.play_video_id = row["id"]
                st.switch_page("pages/4_播放详情.py")
