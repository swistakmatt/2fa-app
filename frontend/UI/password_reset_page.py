import streamlit as st
import asyncio
import httpx
import re
from services.api_handler import api_handler
from .styles import load_global_styles
import time

PASSWORD_REGEX = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^\w\s]).{8,}$"

def password_reset_page(token: str):
    st.session_state.page = "reset"
    st.markdown(load_global_styles(), unsafe_allow_html=True)

    st.markdown("<div class='center-wrapper'>", unsafe_allow_html=True)
    st.markdown("<h2 class='login-title'>NOWE HASŁO</h2>", unsafe_allow_html=True)

    new_password = st.text_input("Nowe hasło", type="password")
    confirm_password = st.text_input("Powtórz hasło", type="password")

    if new_password and not re.match(PASSWORD_REGEX, new_password):
        st.warning(
            "Hasło musi mieć min. 8 znaków, jedną małą i dużą literę, cyfrę oraz znak specjalny."
        )

    if confirm_password and new_password != confirm_password:
        st.warning("Hasła nie są takie same.")

    if st.button("ZMIEŃ HASŁO", use_container_width=True):
        if not new_password or not confirm_password:
            st.error("Uzupełnij oba pola.")
            return

        if new_password != confirm_password:
            st.error("Hasła nie są takie same.")
            return

        if not re.match(PASSWORD_REGEX, new_password):
            st.error("Hasło nie spełnia minimalnych wymagań.")
            return

        try:
            asyncio.run(api_handler.reset_password(token, new_password))
            st.success("Hasło zostało zmienione. Przekierowuję...")
            st.query_params.update({"page": "login"})
            time.sleep(1.5)
            st.rerun()

        except httpx.HTTPStatusError:
            st.error("Token jest nieprawidłowy lub wygasł.")
        except Exception as e:
            st.error(f"Błąd połączenia: {str(e)}")

    st.markdown("</div></div>", unsafe_allow_html=True)
