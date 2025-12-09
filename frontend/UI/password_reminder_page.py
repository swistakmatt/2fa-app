import streamlit as st
import asyncio
import httpx
import re

from .styles import load_global_styles
from services.api_handler import api_handler

EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


def password_reminder_page():
    st.session_state.page = "reminder"

    st.markdown(load_global_styles(), unsafe_allow_html=True)

    st.markdown("<div class='center-wrapper'>", unsafe_allow_html=True)
    st.markdown("<h2 class='login-title'>RESET HASŁA</h2>", unsafe_allow_html=True)

    email = st.text_input("Podaj e-mail", placeholder="email@example.com")

    if email and not re.match(EMAIL_REGEX, email):
        st.warning("Podaj poprawny adres e-mail.")

    clicked = st.button("WYŚLIJ LINK RESETUJĄCY", use_container_width=True)

    if clicked:
        if not email:
            st.error("Podaj email.")
        elif not re.match(EMAIL_REGEX, email):
            st.error("Adres e-mail jest niepoprawny.")
        else:
            try:
                asyncio.run(api_handler.send_reset_link(email))
                st.success("Link resetujący wysłany. Sprawdź skrzynkę.")
            except Exception as e:
                st.error(f"Błąd wysyłania: {str(e)}")

    st.markdown("""
    <div class='small-links'>
        <a href='?page=login' class='link-btn' target='_self'>Wróć do logowania</a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div></div>", unsafe_allow_html=True)
