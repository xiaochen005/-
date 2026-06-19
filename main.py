# main.py
import streamlit as st

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

init_session()

# ====================== 侧边栏区域 ======================
with st.sidebar:
    st.header("🎬 视频网站导航")
    st.divider()

    # 主题选择（移除on_change，不再触发回调警告）
    st.radio(
        "页面主题切换",
        ["light", "dark"],
        key="theme"
    )
    # 手动刷新按钮，点击才切换样式
    if st.button("应用主题"):
        st.rerun()

    st.divider()

    # 用户登录区域
    if st.session_state.login_status:
        st.write(f"欢迎：{st.session_state.username}")
        if st.session_state.is_admin:
            st.success("🔑 管理员账号")
        if st.button("退出登录"):
            st.session_state.login_status = False
            st.session_state.username = ""
            st.session_state.is_admin = False
            st.session_state.play_video_id = None
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