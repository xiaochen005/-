# pages/2_登录注册.py
import streamlit as st
from db_utils import db_query, db_execute, encrypt_pwd, write_log

st.header("🔐 登录 / 注册账号")
tab_login, tab_reg = st.tabs(["账号登录",  "新用户注册"])

# 登录
with tab_login:
    uname = st.text_input("用户名", key="login_name")
    pwd = st.text_input("密码", type="password", key="login_pwd")
    if st.button("登录", type="primary"):
        if not uname or not pwd:
            st.warning("用户名和密码不能为空")
        else:
            pwd_md5 = encrypt_pwd(pwd)
            user_df = db_query("SELECT * FROM user WHERE username=? AND password=?", (uname, pwd_md5))
            if not user_df.empty:
                user_info = user_df.iloc[0]
                st.session_state.login_status = True
                st.session_state.username = uname
                st.session_state.is_admin = int(user_info["is_admin"])
                write_log("登录", uname, "用户登录网站")
                st.success("登录成功，页面自动刷新")
                st.rerun()
            else:
                st.error("用户名或密码错误")

# 注册
with tab_reg:
    reg_name = st.text_input("设置用户名", key="reg_name")
    reg_pwd = st.text_input("设置密码", type="password", key="reg_pwd")
    if st.button("注册账号"):
        if not reg_name or not reg_pwd:
            st.warning("用户名密码不可为空")
        else:
            check = db_query("SELECT id FROM user WHERE username=?", (reg_name,))
            if not check.empty:
                st.error("用户名已存在")
            else:
                pwd_md5 = encrypt_pwd(reg_pwd)
                db_execute("INSERT INTO user(username,password,is_admin,register_time) VALUES (?,?,0,datetime('now','localtime'))",
                           (reg_name, pwd_md5))
                write_log("注册", reg_name, "新用户注册账号")
                st.success("注册完成，前往登录页面登录")