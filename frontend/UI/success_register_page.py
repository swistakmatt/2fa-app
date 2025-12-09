import streamlit as st
from .styles import load_global_styles

def success_register_page(email=""):
    st.session_state.page = "success_register"

    if not email:
        email = st.session_state.get("email", "")

    st.session_state.email = email

    st.markdown(load_global_styles(), unsafe_allow_html=True)

    st.markdown("<div class='center-wrapper'>", unsafe_allow_html=True)

    st.markdown("<h2 class='login-title'>REJESTRACJA UDANA</h2>", unsafe_allow_html=True)

    st.markdown(f"""
        <div class='success-text'>
            Rejestracja użytkownika powiodła się.<br>
            Wysłano potwierdzenie na adres e-mail:<br><br>
            <span style='font-weight:700; font-size:1.2rem;'>{email}</span><br><br><br>
            <div class='activate'>Aby aktywować konto, potwierdź swój adres e-mail.</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class='small-links'>
        <a href='?page=login' class='link-btn' target='_self'>Powrót do panelu logowania</a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
