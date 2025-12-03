import streamlit as st
import asyncio
import httpx
from .styles import load_global_styles
from services.api_handler import api_handler

def register_page():
    st.session_state.page = "register"

    st.markdown(load_global_styles(), unsafe_allow_html=True)

    st.markdown("<div class='center-wrapper'>", unsafe_allow_html=True)
    st.markdown("<h2 class='login-title'>REJESTRACJA</h2>", unsafe_allow_html=True)

    email = st.text_input("E-mail", placeholder="email@example.com")
    password = st.text_input("Hasło", type="password")
    repeat = st.text_input("Powtórz hasło", type="password")

    if st.button("UTWÓRZ KONTO", use_container_width=True):
        if not email or not password or not repeat:
            st.error("Proszę wypełnić wszystkie pola")
        elif password != repeat:
            st.error("Hasła nie są identyczne")
        elif len(password) < 8:
            st.error("Hasło musi mieć minimum 8 znaków")
        else:
            try:
                # Call backend API
                response = asyncio.run(api_handler.register(email, password))
                
                # Save email and navigate to success page
                st.session_state.email = email
                st.session_state.page = "success_register"
                
                st.query_params.update({"page": "success_register", "email": email})
                st.success(response.get("message", "Konto utworzone pomyślnie!"))
                st.rerun()
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 400:
                    st.error("Użytkownik z tym adresem email już istnieje")
                else:
                    st.error(f"Błąd rejestracji: {e.response.text}")
            except Exception as e:
                st.error(f"Błąd połączenia z serwerem: {str(e)}")

    st.markdown("""
    <div class='small-links'>
        <a href='?page=login' class='link-btn' target='_self'>Masz już konto? Zaloguj się!</a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
