# Streamlit 轻量化B站风格视频分享站（阶段六完整版）
## 项目进度
已完成阶段1~6基础功能，拓展场景2云端外网部署：阿里云OSS存储视频，支持Streamlit Cloud免费外网访问。
### 原有基础功能（阶段1-6）
1. 用户注册登录，MD5密码加密
2. 视频上传、管理员审核/下架/删除
3. 点赞、收藏、评论、播放量统计
4. 首页分页、关键词+分类筛选缓存
5. 全局数据库工具、操作日志、系统自检
6. 深浅主题切换，统一异常捕获
### 场景2新增拓展功能
1. 阿里云OSS云端存储视频/封面，外网直链播放
2. UP主专属主页、粉丝关注/取关系统
3. 自定义颜色弹幕系统
4. 视频合集投稿管理
5. 视频举报工单，管理员后台处理违规内容

## 本地运行流程
1. 克隆仓库
git clone https://github.com/你的用户名/仓库名.git
2. 安装依赖
pip install -r requirements.txt
3. 配置OSS
复制.env.example 重命名为.env，填入阿里云OSS密钥
4. 初始化数据库（阶段六已有基础库，只需执行拓展表脚本）
python update_bilibili_func.py
python check_project.py
5. 启动项目
streamlit run main.py

## Streamlit Cloud 外网部署教程
1. 绑定GitHub账号至 share.streamlit.io
2. 创建App，选择本仓库main分支，入口文件main.py
3. 高级设置-Secrets填入OSS配置（同.env格式）
4. Deploy生成永久外网访问链接

## 存储说明
所有视频、封面文件存放阿里云OSS，仓库不存储媒体大文件，轻量化上传GitHub。
