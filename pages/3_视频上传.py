# pages/3_视频上传.py 带自动封面截取（opencv方案，云端可用）
import streamlit as st
import os
import cv2
from datetime import datetime
from db_utils import db_execute, write_log, db_query
import oss2

MAX_SIZE_MB = 200

# OSS密钥兼容本地/云端
try:
    # Streamlit云端读取
    ACCESS_KEY_ID = st.secrets["ACCESS_KEY_ID"]
    ACCESS_KEY_SECRET = st.secrets["ACCESS_KEY_SECRET"]
    ENDPOINT = st.secrets["ENDPOINT"]
    BUCKET_NAME = st.secrets["BUCKET_NAME"]
except Exception:
    # 本地开发读取.env
    from dotenv import load_dotenv
    load_dotenv()
    ACCESS_KEY_ID = os.getenv("ACCESS_KEY_ID")
    ACCESS_KEY_SECRET = os.getenv("ACCESS_KEY_SECRET")
    ENDPOINT = os.getenv("ENDPOINT")
    BUCKET_NAME = os.getenv("BUCKET_NAME")

# OSS上传函数（内嵌，无需外部oss_upload.py）
def upload_file_to_oss(local_file_path, save_folder="video"):
    auth = oss2.Auth(ACCESS_KEY_ID, ACCESS_KEY_SECRET)
    bucket = oss2.Bucket(auth, ENDPOINT, BUCKET_NAME)
    time_tag = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.basename(local_file_path)
    oss_key = f"{save_folder}/{time_tag}_{filename}"
    bucket.put_object_from_file(oss_key, local_file_path)
    return f"https://{BUCKET_NAME}.{ENDPOINT}/{oss_key}"

# OpenCV自动截取视频封面（核心，替代moviepy）
def create_video_cover(video_temp_path, cover_save_name):
    temp_dir = "./static/tmp"
    os.makedirs(temp_dir, exist_ok=True)
    cover_full_path = os.path.join(temp_dir, cover_save_name)
    cap = cv2.VideoCapture(video_temp_path)
    # 跳至1秒画面，避免黑屏首帧
    cap.set(cv2.CAP_PROP_POS_MSEC, 1000)
    ret, frame = cap.read()
    if ret:
        cv2.imwrite(cover_full_path, frame)
    cap.release()
    return cover_full_path

# 登录拦截
if not st.session_state.login_status:
    st.error("请先登录后再上传视频")
    if st.button("前往登录页面"):
        st.switch_page("pages/2_登录注册.py")
    st.stop()
current_user = st.session_state.username

st.header("📤 UP主投稿中心")
st.info(f"仅支持 mp4/mov，单文件上限 {MAX_SIZE_MB}MB；系统自动截取视频封面，也可手动自定义封面")

# 查询当前用户合集
group_data = db_query("SELECT id,group_name FROM collection_group WHERE upload_user=?", (current_user,))
tab_upload, tab_create_group = st.tabs(["投稿视频", "新建合集"])

# 新建合集面板
with tab_create_group:
    group_name_input = st.text_input("合集名称")
    if st.button("创建合集") and group_name_input.strip():
        db_execute(
            "INSERT INTO collection_group(group_name,upload_user,create_time) VALUES (?,?,datetime('now','localtime'))",
            (group_name_input, current_user)
        )
        write_log("创建合集", current_user, f"新建合集：{group_name_input}")
        st.rerun()

# 视频投稿主面板
with tab_upload:
    title = st.text_input("视频标题", max_chars=60)
    intro = st.text_area("视频简介", max_chars=300)
    main_category = st.selectbox("一级分区", ["生活","科技","游戏","影视","教程","动画","其他"])
    sub_category = st.text_input("二级子分类（选填）")
    video_upload = st.file_uploader("上传视频文件", type=["mp4", "mov"])
    custom_cover = st.file_uploader("自定义封面图片（可选，不上传则自动截取）", type=["jpg", "png"])

    # 合集下拉
    group_list = ["无合集"]
    if not group_data.empty:
        group_list += list(group_data["group_name"])
    select_group = st.selectbox("归入合集", group_list)

    if st.button("确认投稿", type="primary"):
        try:
            # 基础校验
            if not title or not video_upload:
                st.warning("标题和视频文件为必填项")
                st.stop()
            file_size_mb = video_upload.size / 1024 / 1024
            if file_size_mb > MAX_SIZE_MB:
                st.error(f"文件超出{MAX_SIZE_MB}MB限制，请压缩后重新上传")
                st.stop()

            time_tag = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_dir = "./static/tmp"
            os.makedirs(temp_dir, exist_ok=True)
            # 临时保存视频
            temp_video_path = os.path.join(temp_dir, f"{time_tag}_{video_upload.name}")
            with open(temp_video_path, "wb") as f:
                f.write(video_upload.read())

            # 封面处理逻辑：自定义优先，无自定义则自动截取
            cover_temp_path = ""
            if custom_cover:
                cover_temp_path = os.path.join(temp_dir, f"{time_tag}_custom_cover.{custom_cover.name.split('.')[-1]}")
                with open(cover_temp_path, "wb") as f:
                    f.write(custom_cover.read())
            else:
                cover_temp_path = create_video_cover(temp_video_path, f"{time_tag}_auto_cover.jpg")

            # 上传OSS
            video_oss_url = upload_file_to_oss(temp_video_path, "video")
            cover_oss_url = upload_file_to_oss(cover_temp_path, "cover")

            # 写入视频数据库
            upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            db_execute("""
                INSERT INTO video(title,intro,category,sub_category,video_path,cover_path,upload_user,status,upload_time,collect_count,like_count,play_count)
                VALUES (?,?,?,?,?,?,?,0,?,0,0,0)
            """, (title, intro, main_category, sub_category, video_oss_url, cover_oss_url, current_user, upload_time))

            # 绑定合集关系
            if select_group != "无合集":
                group_id = group_data[group_data["group_name"] == select_group]["id"].iloc[0]
                new_video_id = db_query("SELECT id FROM video ORDER BY id DESC LIMIT 1").iloc[0]["id"]
                db_execute("INSERT INTO group_video_rel(group_id,video_id) VALUES (?,?)", (group_id, new_video_id))

            write_log("视频投稿上传", current_user, f"投稿视频：{title}")
            st.success("投稿成功！视频与封面已上传至OSS，等待管理员审核展示")
            st.rerun()
        except Exception as e:
            st.error(f"投稿失败：{str(e)}")
