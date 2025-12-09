import streamlit as st
from UI.login_page import login_page
from UI.register_page import register_page
from UI.password_reminder_page import password_reminder_page
from UI.success_register_page import success_register_page
from UI.twofa_page import twofa_page
from UI.profile_page import profile_page
from UI.password_reset_page import password_reset_page
from services.api_handler import api_handler

st.session_state.page = st.query_params.get("page", st.session_state.get("page", "login"))

if "token" in st.query_params:
    st.session_state.token = st.query_params["token"]

if (
    st.query_params.get("page") == "reset"
    and "token" in st.query_params
    and st.session_state.get("token") != st.query_params.get("token")
):
    st.rerun()

email = ""

token = st.session_state.get("token")
if token:
    try:
        decoded = api_handler.get_email_from_token(token)
        email = decoded.get("email", "")
        st.session_state.email = email
    except Exception:
        email = ""
        st.session_state.email = ""

if not email:
    email = st.session_state.get("email", "")

page = st.session_state.page

if page == "login":
    login_page()

elif page == "register":
    register_page()

elif page == "reminder":
    password_reminder_page()

elif page == "success_register":
    success_register_page(email=email)

elif page == "twofa":
    twofa_page(email=email, timer_start=90)

elif page == "profile":
    profile_page(email=email)

elif page == "reset":
    password_reset_page(token=st.session_state.get("token", ""))

else:
    login_page()
