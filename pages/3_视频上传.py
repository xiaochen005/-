# pages/3_视频上传.py 无视频解析库，手动上传封面，修复session变量报错
import streamlit as st
import os
from datetime import datetime
from db_utils import db_execute, write_log, db_query
import oss2

MAX_SIZE_MB = 200

# OSS密钥兼容本地/云端
try:
    ACCESS_KEY_ID = st.secrets["ACCESS_KEY_ID"]
    ACCESS_KEY_SECRET = st.secrets["ACCESS_KEY_SECRET"]
    ENDPOINT = st.secrets["ENDPOINT"]
    BUCKET_NAME = st.secrets["BUCKET_NAME"]
except Exception:
    from dotenv import load_dotenv
    load_dotenv()
    ACCESS_KEY_ID = os.getenv("ACCESS_KEY_ID")
    ACCESS_KEY_SECRET = os.getenv("ACCESS_KEY_SECRET")
    ENDPOINT = os.getenv("ENDPOINT")
    BUCKET_NAME = os.getenv("BUCKET_NAME")

# OSS上传函数内嵌
def upload_file_to_oss(local_file_path, save_folder="video"):
    auth = oss2.Auth(ACCESS_KEY_ID, ACCESS_KEY_SECRET)
    bucket = oss2.Bucket(auth, ENDPOINT, BUCKET_NAME)
    time_tag = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.basename(local_file_path)
    oss_key = f"{save_folder}/{time_tag}_{filename}"
    bucket.put_object_from_file(oss_key, local_file_path)
    return f"https://{BUCKET_NAME}.{ENDPOINT}/{oss_key}"

# 修复session不存在报错：用get获取，无则默认False
login_status = st.session_state.get("login_status", False)
if not login_status:
    st.error("请先登录后再上传视频")
    if st.button("前往登录页面"):
        st.switch_page("pages/2_登录注册.py")
    st.stop()
current_user = st.session_state.get("username", "")

st.header("📤 UP主投稿中心")
st.info(f"仅支持 mp4/mov，单文件上限 {MAX_SIZE_MB}MB；必须手动上传封面图片")

# 查询用户合集
group_data = db_query("SELECT id,group_name FROM collection_group WHERE upload_user=?", (current_user,))
tab_upload, tab_create_group = st.tabs(["投稿视频", "新建合集"])

# 新建合集
with tab_create_group:
    group_name_input = st.text_input("合集名称")
    if st.button("创建合集") and group_name_input.strip():
        db_execute(
            "INSERT INTO collection_group(group_name,upload_user,create_time) VALUES (?,?,datetime('now','localtime'))",
            (group_name_input, current_user)
        )
        write_log("创建合集", current_user, f"新建合集：{group_name_input}")
        st.rerun()

# 投稿表单
with tab_upload:
    title = st.text_input("视频标题", max_chars=60)
    intro = st.text_area("视频简介", max_chars=300)
    main_category = st.selectbox("一级分区", ["生活","科技","游戏","影视","教程","动画","其他"])
    sub_category = st.text_input("二级子分类（选填）")
    video_upload = st.file_uploader("上传视频文件", type=["mp4", "mov"])
    custom_cover = st.file_uploader("上传封面图片【必填】", type=["jpg", "png"])

    group_list = ["无合集"]
    if not group_data.empty:
        group_list += list(group_data["group_name"])
    select_group = st.selectbox("归入合集", group_list)

    if st.button("确认投稿", type="primary"):
        try:
            if not title or not video_upload or not custom_cover:
                st.warning("标题、视频、封面图片均为必填项")
                st.stop()
            file_size_mb = video_upload.size / 1024 / 1024
            if file_size_mb > MAX_SIZE_MB:
                st.error(f"文件超出{MAX_SIZE_MB}MB限制")
                st.stop()

            time_tag = datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_dir = "./static/tmp"
            os.makedirs(temp_dir, exist_ok=True)

            # 临时保存视频
            temp_video_path = os.path.join(temp_dir, f"{time_tag}_{video_upload.name}")
            with open(temp_video_path, "wb") as f:
                f.write(video_upload.read())

            # 临时保存封面
            cover_temp_path = os.path.join(temp_dir, f"{time_tag}_cover.{custom_cover.name.split('.')[-1]}")
            with open(cover_temp_path, "wb") as f:
                f.write(custom_cover.read())

            # 上传OSS
            video_oss_url = upload_file_to_oss(temp_video_path, "video")
            cover_oss_url = upload_file_to_oss(cover_temp_path, "cover")

            upload_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            db_execute("""
                INSERT INTO video(title,intro,category,sub_category,video_path,cover_path,upload_user,status,upload_time,collect_count,like_count,play_count)
                VALUES (?,?,?,?,?,?,?,0,?,0,0,0)
            """, (title, intro, main_category, sub_category, video_oss_url, cover_oss_url, current_user, upload_time))

            # 绑定合集
            if select_group != "无合集":
                group_id = group_data[group_data["group_name"] == select_group]["id"].iloc[0]
                new_video_id = db_query("SELECT id FROM video ORDER BY id DESC LIMIT 1").iloc[0]["id"]
                db_execute("INSERT INTO group_video_rel(group_id,video_id) VALUES (?,?)", (group_id, new_video_id))

            write_log("视频投稿上传", current_user, f"投稿视频：{title}")
            st.success("投稿成功！视频与封面已上传OSS，等待审核")
            st.rerun()
        except Exception as e:
            st.error(f"投稿失败：{str(e)}")
