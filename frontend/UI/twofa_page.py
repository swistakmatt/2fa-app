import streamlit as st
import streamlit.components.v1 as components
import asyncio
import httpx
from .styles import load_global_styles
from services.api_handler import api_handler


def run_async(coro):
    return asyncio.run(coro)


def send_2fa_code(access_token):
    try:
        run_async(api_handler.send_code(access_token))
        st.session_state["2fa_sent"] = True
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 429:
            st.warning("Kod już wysłany. Sprawdź maila i chwilę zaczekaj.")
            st.session_state["2fa_sent"] = True
        else:
            st.error(f"Błąd wysyłania kodu: {e.response.text}")
    except Exception as e:
        st.error(f"Błąd połączenia: {str(e)}")


def twofa_page(email="", timer_start=90):
    st.session_state.page = "twofa"

    if email:
        st.session_state.email = email

    st.markdown(load_global_styles(), unsafe_allow_html=True)

    st.markdown("<div class='center-wrapper'>", unsafe_allow_html=True)
    st.markdown("<h2 class='login-title'>WERYFIKACJA UŻYTKOWNIKA</h2>", unsafe_allow_html=True)

    if not st.session_state.get("2fa_sent"):
        access_token = st.session_state.get("access_token")
        if not access_token:
            st.error("Brak tokenu. Zaloguj się ponownie.")
            return
        send_2fa_code(access_token)

    st.markdown("<div id='timer' class='timer-box'></div>", unsafe_allow_html=True)

    st.markdown("<div class='verify-block'>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Kod Email</div>", unsafe_allow_html=True)

    cols = st.columns(6)
    for i, col in enumerate(cols):
        with col:
            st.text_input(
                " ",
                max_chars=1,
                key=f"pin_{i}",
                label_visibility="collapsed"
            )

    st.markdown("<div class='btn-stack'>", unsafe_allow_html=True)

    if st.button("WERYFIKUJ KODEM GŁÓWNYM", use_container_width=True):
        code = "".join(st.session_state.get(f"pin_{i}", "") for i in range(6))

        if len(code) != 6:
            st.error("Kod PIN musi mieć 6 cyfr.")
            return

        access_token = st.session_state.get("access_token")
        if not access_token:
            st.error("Brak tokenu. Zaloguj się ponownie.")
            return

        try:
            resp = run_async(api_handler.verify_2fa(access_token, code))
            backup = resp.get("backup_codes", [])
            if backup:
                st.session_state["backup_codes"] = backup

            st.success("Weryfikacja udana!")
            st.session_state.page = "profile"
            st.query_params.update({"page": "profile"})
            st.rerun()
            return

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                st.error("Nieprawidłowy kod weryfikacyjny")
            elif e.response.status_code == 401:
                st.error("Token wygasł. Zaloguj się ponownie.")
            elif e.response.status_code == 403:
                st.error("Zbyt wiele prób. Konto tymczasowo zablokowane.")
            else:
                st.error(f"Błąd weryfikacji: {e.response.text}")
        except Exception as e:
            st.error(f"Błąd połączenia: {str(e)}")

    if st.button("WYŚLIJ KOD PONOWNIE", use_container_width=True):
        st.session_state["2fa_sent"] = False
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>Kod zapasowy</div>", unsafe_allow_html=True)
    backup_code = st.text_input(" ", max_chars=6, label_visibility="collapsed")

    if st.button("WERYFIKUJ KODEM ZAPASOWYM", use_container_width=True):
        if not backup_code:
            st.error("Podaj kod zapasowy.")
            return

        access_token = st.session_state.get("access_token")
        if not access_token:
            st.error("Brak tokenu. Zaloguj się ponownie.")
            return

        try:
            run_async(api_handler.verify_backup_code(access_token, backup_code))
            st.success("Weryfikacja udana!")
            st.session_state.page = "profile"
            st.query_params.update({"page": "profile"})
            st.rerun()
            return

        except httpx.HTTPStatusError:
            st.error("Nieprawidłowy kod zapasowy")
        except Exception as e:
            st.error(f"Błąd połączenia: {str(e)}")

    st.markdown("</div>", unsafe_allow_html=True)

    components.html(
        f"""
        <script>
            let timeLeft = {timer_start};

            function updateTimer() {{
                const el = window.parent.document.getElementById("timer");
                if (!el) {{
                    setTimeout(updateTimer, 100);
                    return;
                }}
                el.innerHTML = "Kod ważny przez: " + timeLeft + " sekund...";
                timeLeft--;
                if (timeLeft >= 0) setTimeout(updateTimer, 1000);
            }}
            updateTimer();

            function initInputs() {{
                const inputs = window.parent.document.querySelectorAll("input[type='text']");
                if (inputs.length < 6) {{
                    setTimeout(initInputs, 100);
                    return;
                }}

                inputs.forEach((input, index) => {{
                    input.addEventListener("input", () => {{
                        if (input.value.length === 1 && index < 5) {{
                            inputs[index + 1].focus();
                        }}
                    }});
                    input.addEventListener("keydown", (e) => {{
                        if (e.key === "Backspace" && input.value === "" && index > 0) {{
                            inputs[index - 1].focus();
                        }}
                    }});
                }});
                inputs[0].focus();
            }}
            initInputs();
        </script>
        """,
        height=0
    )

    st.markdown("</div>", unsafe_allow_html=True)
