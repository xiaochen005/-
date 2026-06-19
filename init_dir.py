# init_dir.py 自动创建项目目录结构
import os

# 定义项目所有目录
dir_list = [
    "database",       # 数据库文件存放目录
    "static/videos",  # 用户上传视频存储目录
    "static/cover",   # 视频封面图存储目录
    "static/css",     # 自定义样式文件目录
    "pages"           # Streamlit多页面路由目录
]

# 循环创建目录
for path in dir_list:
    os.makedirs(path, exist_ok=True)
    print(f"目录创建成功：{path}")

print("✅ 所有项目目录初始化完成！")