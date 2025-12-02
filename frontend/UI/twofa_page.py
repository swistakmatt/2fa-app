import streamlit as st
import streamlit.components.v1 as components
from .styles import load_global_styles

def twofa_page(email="", timer_start=90):

    # STRONA ZAWSZE = TWOFA
    st.session_state.page = "twofa"
    st.session_state.email = email

    st.markdown(load_global_styles(), unsafe_allow_html=True)

    st.markdown("<div class='center-wrapper'>", unsafe_allow_html=True)
    st.markdown("<h2 class='login-title'>WERYFIKACJA UŻYTKOWNIKA</h2>", unsafe_allow_html=True)

    # BLOK Z MAILIEM I TIMEREM
    st.markdown(f"""
        <div class='success-text'>
            Wysłano kod weryfikacyjny na:<br>
            <span style='font-weight:700; font-size:1.2rem;'>{email}</span><br>
            <span id='timer' style='color:#ff4444;'>
                Kod ważny przez: {timer_start} sekund...
            </span>
        </div>
    """, unsafe_allow_html=True)

    # INPUTY PIN
    cols = st.columns(6)
    for i in range(6):
        with cols[i]:
            st.text_input(
                "",
                max_chars=1,
                key=f"pin_{i}",
                label_visibility="collapsed"
            )

    # PRZYCISK WERYFIKACJI
    if st.button("WERYFIKUJ", use_container_width=True):
        code = "".join(st.session_state.get(f"pin_{i}", "") for i in range(6))

        if len(code) == 6:
            st.session_state.page = "profile"
            st.query_params.update({"page": "profile", "email": email})
            st.rerun()
        else:
            st.error("Kod PIN musi mieć 6 cyfr.")

    # TUTAJ CI ZNIKAŁ „WYŚLIJ KOD PONOWNIE” – PRZYWRACAM
    st.markdown(f"""
    <div class='small-links' style='margin-top:20px;'>
        <a href='?page=twofa&email={email}' class='link-btn' target='_self'>
            Wyślij kod ponownie
        </a>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # JAVASCRIPT: TIMER + AUTOFOKUS + AUTOJUMP
    components.html(f"""
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
                if (inputs.length !== 6) {{
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
    """, height=0)
