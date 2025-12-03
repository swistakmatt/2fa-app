import streamlit as st
import asyncio
import httpx
from .styles import load_global_styles
from services.api_handler import api_handler

def login_page():
    st.session_state.page = "login"

    st.markdown(load_global_styles(), unsafe_allow_html=True)

    st.markdown("<div class='center-wrapper'>", unsafe_allow_html=True)
    st.markdown("<h2 class='login-title'>LOGOWANIE</h2>", unsafe_allow_html=True)

    email = st.text_input("E-mail", placeholder="email@example.com")
    password = st.text_input("Hasło", type="password")

    if st.button("ZALOGUJ", use_container_width=True):
        if not email or not password:
            st.error("Proszę wypełnić wszystkie pola")
        else:
            try:
                # Call backend API
                response = asyncio.run(api_handler.login(email, password))
                
                # Save tmp_token and email to session
                st.session_state.tmp_token = response.get("tmp_token")
                st.session_state.email = email
                st.session_state.page = "twofa"
                
                st.query_params.update({"page": "twofa", "email": email})
                st.rerun()
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 401:
                    st.error("Nieprawidłowy email lub hasło")
                else:
                    st.error(f"Błąd logowania: {e.response.text}")
            except Exception as e:
                st.error(f"Błąd połączenia z serwerem: {str(e)}")

    st.markdown("<div class='separator'>lub</div>", unsafe_allow_html=True)
    st.button("Continue with Google", use_container_width=True)

    st.markdown("""
    <div class='small-links'>
        <a href='?page=register' class='link-btn' target='_self'>Nie masz konta? Zarejestruj się!</a><br>
        <a href='?page=reminder' class='link-btn' target='_self'>Zapomniałeś hasła?</a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
