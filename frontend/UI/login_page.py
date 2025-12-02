import streamlit as st
from .styles import load_global_styles

def login_page():
    st.session_state.page = "login"

    st.markdown(load_global_styles(), unsafe_allow_html=True)

    st.markdown("<div class='center-wrapper'>", unsafe_allow_html=True)
    st.markdown("<h2 class='login-title'>LOGOWANIE</h2>", unsafe_allow_html=True)

    email = st.text_input("E-mail", placeholder="email@example.com")
    password = st.text_input("Hasło", type="password")

    if st.button("ZALOGUJ", use_container_width=True):
        if email:
            st.session_state.email = email
            st.session_state.page = "twofa"

            st.query_params.update({"page": "twofa", "email": email})
            st.rerun()

    st.markdown("<div class='separator'>lub</div>", unsafe_allow_html=True)
    st.button("Continue with Google", use_container_width=True)

    st.markdown("""
    <div class='small-links'>
        <a href='?page=register' class='link-btn' target='_self'>Nie masz konta? Zarejestruj się!</a><br>
        <a href='?page=reminder' class='link-btn' target='_self'>Zapomniałeś hasła?</a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
