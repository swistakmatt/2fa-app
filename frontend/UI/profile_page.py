import streamlit as st
import asyncio
import httpx
from .styles import load_global_styles
from services.api_handler import api_handler

def profile_page(email=""):
    st.session_state.page = "profile"
    st.markdown(load_global_styles(), unsafe_allow_html=True)

    st.markdown("<div class='center-wrapper'>", unsafe_allow_html=True)
    st.markdown("<h2 class='login-title'>PANEL UŻYTKOWNIKA</h2>", unsafe_allow_html=True)

    # Check if user is authenticated
    access_token = st.session_state.get("access_token")
    if not access_token:
        st.error("Brak autoryzacji. Zaloguj się ponownie.")
        if st.button("Powrót do logowania"):
            st.session_state.page = "login"
            st.query_params.update({"page": "login"})
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        return
    
    # Fetch user data from backend
    try:
        user_data = asyncio.run(api_handler.get_profile(access_token))
        email = user_data.get("email", email)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            st.error("Sesja wygasła. Zaloguj się ponownie.")
            st.session_state.clear()
            if st.button("Powrót do logowania"):
                st.query_params.update({"page": "login"})
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            return
        else:
            st.error(f"Błąd pobierania danych: {e.response.text}")
    except Exception as e:
        st.error(f"Błąd połączenia z serwerem: {str(e)}")

    # nowy układ 2 kolumn (lewa węższa, prawa szersza)
    cols = st.columns([1.2, 3])

    # LEWA kolumna (avatar + email)
    with cols[0]:
        st.markdown("""
            <div style="text-align:center; margin-top:20px;">
                <img src="https://upload.wikimedia.org/wikipedia/commons/9/99/Sample_User_Icon.png"
                     width="110" style="border-radius:50%; margin-bottom:10px;">
                <br>
                <a href="#" style="font-size:0.9rem; color:#555;">Zmień zdjęcie profilowe</a>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.text_input("Adres email", value=email, disabled=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Wyloguj", use_container_width=True):
            st.session_state.clear()
            st.query_params.update({"page": "login"})
            st.rerun()

    # PRAWA kolumna (pola użytkownika)
    with cols[1]:
        c1, c2 = st.columns(2)
        with c1:
            first_name = st.text_input("Imię")
        with c2:
            last_name = st.text_input("Nazwisko")

        street = st.text_input("Ulica")

        c3, c4 = st.columns(2)
        with c3:
            city = st.text_input("Miasto")
        with c4:
            postal_code = st.text_input("Kod pocztowy")

        c5, c6 = st.columns(2)
        with c5:
            birth_date = st.text_input("Data urodzenia")
        with c6:
            phone = st.text_input("Telefon")

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Zmień dane użytkownika"):
            st.info("Funkcja aktualizacji dodatkowych danych będzie dostępna wkrótce")
            # TODO: Implement user data update when backend supports it

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
