import streamlit as st
from .styles import load_global_styles

def register_page():
    st.session_state.page = "register"

    st.markdown(load_global_styles(), unsafe_allow_html=True)

    st.markdown("<div class='center-wrapper'>", unsafe_allow_html=True)
    st.markdown("<h2 class='login-title'>REJESTRACJA</h2>", unsafe_allow_html=True)

    email = st.text_input("E-mail", placeholder="email@example.com")
    password = st.text_input("Hasło", type="password")
    repeat = st.text_input("Powtórz hasło", type="password")

    if st.button("UTWÓRZ KONTO", use_container_width=True):
        if email:
            # ZAPISUJEMY EMAIL I STRONĘ
            st.session_state.email = email
            st.session_state.page = "success_register"

            # Aktualizacja URL
            st.query_params.update({"page": "success_register", "email": email})

            st.rerun()

    st.markdown("""
    <div class='small-links'>
        <a href='?page=login' class='link-btn' target='_self'>Masz już konto? Zaloguj się!</a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
