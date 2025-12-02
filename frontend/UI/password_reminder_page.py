import streamlit as st
from .styles import load_global_styles

def password_reminder_page():
    st.session_state.page = "reminder"

    st.markdown(load_global_styles(), unsafe_allow_html=True)

    st.markdown("<div class='center-wrapper'>", unsafe_allow_html=True)
    st.markdown("<h2 class='login-title'>RESET HASŁA</h2>", unsafe_allow_html=True)

    st.text_input("Podaj e-mail", placeholder="email@example.com")
    st.button("WYŚLIJ LINK RESETUJĄCY", use_container_width=True)

    st.markdown("""
    <div class='small-links'>
        <a href='?page=login' class='link-btn' target='_self'>Wróć do logowania</a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)
