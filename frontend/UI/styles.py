from pathlib import Path
import base64

def load_global_styles():
    img_path = Path(__file__).parent.parent / "public" / "background.jpg"

    try:
        with open(img_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        bg_css = f"""
        .stApp {{
            background: url("data:image/jpg;base64,{b64}") no-repeat center center fixed;
            background-size: cover;
        }}
        """
    except FileNotFoundError:
        bg_css = ""

    return f"""
    <style>
    {bg_css}

    .center-wrapper {{
        display: flex;
        justify-content: center;
        align-items: center;
        height: auto;
    }}

    .stMainBlockContainer > div {{
        width: 550px;                
        min-height: 320px;           
        margin: 25vh auto 0 auto;    
        padding: 5px 40px 25px;     
        border-radius: 10px;
        background: rgba(255, 255, 255, 0.97);
        box-shadow: 0 4px 25px rgba(0,0,0,0.35);
    }}

    .login-title {{
        text-align: center;
        font-size: 301px;   /* WRACA DO TWOJEGO STANU */
        font-weight: 600;
        color: #0b2c57 !important;
    }}

    .separator {{
        text-align: center;
        margin: 9px 0 20px 0;
        font-size: 17px;
    }}

    .small-links {{
        margin-top: 20px;
        text-align: center;
        font-size: 15px;
    }}

    .small-links a {{
        color: #1f4c9c;
        text-decoration: none;
    }}

    .small-links a:hover {{
        text-decoration: underline;
    }}

    div[data-baseweb="input"] > div {{
        background-color: #e6eef8;
        font-size: 15px;
        height: 48px;
    }}

    .st-by {{
        padding-right: 0 !important;
    }}

    .stButton > button:hover {{
        background-color: #0b2c57 !important;
        color: white !important;
        border-color: #0b2c57 !important;
    }}

    a[class*='st-emotion-cache'] {{
        display: none !important;
    }}

    .success-text {{
        font-size: 0.95rem;
        line-height: 1.45rem;
        margin-bottom: 20px;
    }}

    .activate {{
        font-size: 0.95rem;
        line-height: 1.45rem;
        margin-bottom: 20px;
        color: #8B0000;
    }}

    .st-bz {{
        padding-right: 0;
    }}

    [data-testid='stMarkdownContainer']:has([class*='link-wrapper']) {{
        text-align: center !important;
    }}

    .section-title {{
        margin-top: 15px;
        font-size: 17px;
        font-weight: 600;
        color: #0b2c57;
        text-align: left;
    }}

    .pin-row {{
        display: flex !important;
        justify-content: center !important;
        gap: 12px !important;
        margin: 10px 0 20px 0;
    }}

    div[class*='st-key-pin_'] {{
        display: inline-flex !important;
        justify-content: center !important;
        align-items: center !important;

        text-align: center !important;
        font-size: 22px !important;
        height: 48px !important;
        width: 48px !important;
        border-radius: 6px !important;
        border: 1px solid #9bb7e0 !important;
        background: #e6eef8 !important;
    }}


    .btn-stack > div {{
        margin-bottom: 10px;
    }}

    .verify-block {{
        margin-bottom: 20px;
    }}

    .timer-box {{
        text-align: center;
        font-weight: 600;
        font-size: 17px;
        margin-bottom: 15px;
        color: #8B0000;
    }}

    /* PROFILE PAGE */
    .profile-icon {{
        width: 80px;
        height: 80px;
        background-image: url("https://cdn-icons-png.flaticon.com/512/847/847969.png");
        background-size: cover;
        background-position: center;
        margin: 10px auto 0 auto;
        border-radius: 50%;
        box-shadow: 0 2px 6px rgba(0,0,0,0.25);
    }}

    .profile-email {{
        font-size: 18px;
        font-weight: 600;
        color: #0b2c57 !important;
        margin-top: 22px;
        text-align: left;
    }}

    div[data-testid='stLayoutWrapper'] {{
        margin-bottom: 20px !important;
    }}

    </style>
    """
