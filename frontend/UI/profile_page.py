import streamlit as st
from .styles import load_global_styles

def profile_page(email=""):
    st.session_state.page = "profile"
    st.markdown(load_global_styles(), unsafe_allow_html=True)

    st.markdown("<div class='center-wrapper'>", unsafe_allow_html=True)
    st.markdown("<h2 class='login-title'>PANEL UŻYTKOWNIKA</h2>", unsafe_allow_html=True)

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

        st.text_input("Adres email", value=email)

    # PRAWA kolumna (pola użytkownika)
    with cols[1]:
        c1, c2 = st.columns(2)
        with c1:
            st.text_input("Imię")
        with c2:
            st.text_input("Nazwisko")

        st.text_input("Ulica")

        c3, c4 = st.columns(2)
        with c3:
            st.text_input("Miasto")
        with c4:
            st.text_input("Kod pocztowy")

        c5, c6 = st.columns(2)
        with c5:
            st.text_input("Data urodzenia")
        with c6:
            st.text_input("Telefon")

        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("Zmień dane użytkownika"):
            st.success("Dane zostały zapisane.")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
