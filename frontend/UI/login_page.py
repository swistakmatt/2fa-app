import streamlit as st
import asyncio
import httpx
import re
from .styles import load_global_styles
from services.api_handler import api_handler

GOOGLE_LOGIN_URL = api_handler.get_google_login_url()

EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


def login_page():
    st.session_state.page = "login"
    st.markdown(load_global_styles(), unsafe_allow_html=True)

    params = st.query_params

    if params.get("activated") == "1":
        st.success("Konto zostało aktywowane. Możesz się zalogować.")
        st.query_params.pop("activated", None)
        
    if "external_redirect" in params:
        url = params["external_redirect"]
        st.query_params.clear()
        st.markdown(f"<meta http-equiv='refresh' content='0; url={url}' />", unsafe_allow_html=True)
        st.stop()

    if "google_token" in params:
        token = params["google_token"]
        st.session_state.access_token = token
        st.session_state.page = "twofa"
        st.query_params.clear()
        st.rerun()

    st.markdown("<div class='center-wrapper'>", unsafe_allow_html=True)
    st.markdown("<h2 class='login-title'>LOGOWANIE</h2>", unsafe_allow_html=True)

    email = st.text_input("E-mail", placeholder="email@example.com")
    password = st.text_input("Hasło", type="password")

    email_error = None

    if email and not re.match(EMAIL_REGEX, email):
        email_error = "Podaj poprawny adres e-mail."

    if email_error:
        st.warning(email_error)

    clicked_login = st.button("ZALOGUJ", use_container_width=True)

    if clicked_login:
        if not email or not password:
            st.error("Proszę wypełnić wszystkie pola.")
        else:
            try:
                response = asyncio.run(api_handler.login(email, password))

                if response.get("detail") == "not_activated":
                    st.error("Konto nieaktywne. Sprawdź mail i kliknij link aktywacyjny.")
                else:
                    access_token = response.get("access_token")
                    if not access_token:
                        st.error("Brak tokenu.")
                    else:
                        st.session_state.access_token = access_token
                        st.session_state.email = email
                        st.session_state.page = "twofa"
                        st.query_params.update({"page": "twofa"})
                        st.rerun()

            except httpx.HTTPStatusError:
                st.error("Nieprawidłowy email lub hasło.")
            except Exception as e:
                st.error(f"Błąd połączenia z serwerem: {str(e)}")

    st.markdown("<div class='separator'>lub</div>", unsafe_allow_html=True)

    if st.button("Continue with Google", use_container_width=True):
        st.query_params.update({"external_redirect": GOOGLE_LOGIN_URL})

    st.markdown(
        "<div class='link-wrapper'>"
        "<a href='?page=reminder' class='forgot-link'>Zapomniałeś hasła?</a>"
        "</div>",
        unsafe_allow_html=True,
    )

    st.markdown(
        "<div class='register-link-wrapper'>"
        "Nie masz konta? "
        "<a href='?page=register' class='register-link'>Zarejestruj się</a>"
        "</div>",
        unsafe_allow_html=True,
    )
