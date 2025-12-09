import streamlit as st
import asyncio
import httpx
from .styles import load_global_styles
from services.api_handler import api_handler


def profile_page(email=""):
    st.session_state.page = "profile"
    st.markdown(load_global_styles(), unsafe_allow_html=True)

    access_token = st.session_state.get("access_token")
    if not access_token:
        st.error("Brak autoryzacji. Zaloguj się ponownie.")
        return

    try:
        user_data = asyncio.run(api_handler.get_profile(access_token))
        email = user_data.get("email", email)
    except Exception:
        st.error("Sesja wygasła. Zaloguj się ponownie.")
        st.session_state.clear()
        return

    backup_generated = user_data.get("backup_generated", False)
    if not backup_generated:
        st.warning("Nie masz jeszcze kodów zapasowych. "
                   "Zaloguj się poprawnie kodem 2FA, aby je wygenerować.")
        return

    st.markdown("<div class='center-wrapper'>", unsafe_allow_html=True)
    st.markdown("<h2 class='login-title'>PANEL UŻYTKOWNIKA</h2>", unsafe_allow_html=True)

    col_icon, col_email = st.columns([1, 3])

    with col_icon:
        st.markdown(
            "<div class='profile-icon'></div>",
            unsafe_allow_html=True
        )

    with col_email:
        st.markdown(
            f"<div class='profile-email'>{email}</div>",
            unsafe_allow_html=True
        )

    if st.button("Wyloguj", use_container_width=True):
        st.session_state.clear()
        st.query_params.update({"page": "login"})
        st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("<h3>Kody zapasowe 2FA</h3>", unsafe_allow_html=True)

    count_resp = asyncio.run(api_handler.get_backup_count(access_token))
    available_count = count_resp.get("available", 0)

    st.write(f"Dostępnych: {available_count}")

    backup_codes = st.session_state.get("backup_codes", [])

    if backup_codes:
        st.write("Ostatnio wygenerowane:")
        for code in backup_codes:
            st.code(code)

    if st.button("GENERUJ NOWE KODY", use_container_width=True):
        resp = asyncio.run(api_handler.reset_backup_codes(access_token))
        st.session_state["backup_codes"] = resp.get("backup_codes", [])
        st.success("Wygenerowano nowe kody")
        st.rerun()

    if available_count == 0:
        st.warning("Nie masz żadnych kodów zapasowych. Wygeneruj nowe.")

    st.warning("Przechowuj kody offline. Nie udostępniaj ich nikomu.")

    st.markdown("</div>", unsafe_allow_html=True)
