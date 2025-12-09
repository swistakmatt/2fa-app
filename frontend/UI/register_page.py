import streamlit as st
import asyncio
import httpx
import re
from .styles import load_global_styles
from services.api_handler import api_handler

EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
PASSWORD_REGEX = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$"


def register_page():
    st.session_state.page = "register"

    st.markdown(load_global_styles(), unsafe_allow_html=True)

    st.markdown("<div class='center-wrapper'>", unsafe_allow_html=True)
    st.markdown("<h2 class='login-title'>REJESTRACJA</h2>", unsafe_allow_html=True)

    email = st.text_input("E-mail", placeholder="email@example.com")
    password = st.text_input("Hasło", type="password")
    repeat = st.text_input("Powtórz hasło", type="password")

    if email and not re.match(EMAIL_REGEX, email):
        st.warning("Podaj poprawny adres e-mail.")

    if password and not re.match(PASSWORD_REGEX, password):
        st.warning(
            "Hasło musi mieć min. 8 znaków, jedną małą i dużą literę, cyfrę oraz znak specjalny."
        )

    if repeat and password != repeat:
        st.warning("Hasła nie są identyczne.")

    clicked = st.button("UTWÓRZ KONTO", use_container_width=True)

    if clicked:
        if not email or not password or not repeat:
            st.error("Proszę wypełnić wszystkie pola.")

        elif not re.match(EMAIL_REGEX, email):
            st.error("Adres e-mail jest niepoprawny.")

        elif not re.match(PASSWORD_REGEX, password):
            st.error(
                "Hasło nie spełnia minimalnych wymagań: min. 8 znaków, mała litera, duża litera, cyfra, znak specjalny."
            )

        elif password != repeat:
            st.error("Hasła nie są identyczne.")

        else:
            try:
                response = asyncio.run(api_handler.register(email, password))

                st.session_state.email = email
                st.session_state.backup_codes = response.get("backup_codes", [])

                st.session_state.page = "success_register"
                st.query_params.update({"page": "success_register"})
                st.success(response.get("message", "Konto utworzone pomyślnie!"))
                st.rerun()

            except httpx.HTTPStatusError as e:
                if e.response.status_code == 400:
                    st.error("Użytkownik z tym adresem email już istnieje.")
                else:
                    st.error(f"Błąd rejestracji: {e.response.text}")
            except Exception as e:
                st.error(f"Błąd połączenia z serwerem: {str(e)}")

    st.markdown(
        """
        <div class='small-links'>
            <a href='?page=login' class='link-btn' target='_self'>Masz już konto? Zaloguj się!</a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)
