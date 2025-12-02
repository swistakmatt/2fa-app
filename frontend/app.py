import streamlit as st
from UI.login_page import login_page
from UI.register_page import register_page
from UI.password_reminder_page import password_reminder_page
from UI.success_register_page import success_register_page
from UI.twofa_page import twofa_page
from UI.profile_page import profile_page

# INICJALIZACJA
if "page" not in st.session_state:
    st.session_state.page = st.query_params.get("page", "login")

if "email" not in st.session_state:
    st.session_state.email = st.query_params.get("email", "")

page = st.session_state.page
email = st.session_state.email

# ROUTING
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

else:
    login_page()
