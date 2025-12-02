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

    /* wrapper centrujący całą kartę na środku ekranu */
    .center-wrapper {{
        display: flex;
        justify-content: center;
        align-items: center;
        height: auto;
    }}

    /* główne białe pudełko */
    .main .block-container {{
        width: 550px;                
        min-height: 320px;           
        margin: 25vh auto 0 auto;    
        padding: 5px 40px 25px;     
        border-radius: 10px;
        background: rgba(255, 255, 255, 0.97);
        box-shadow: 0 4px 25px rgba(0,0,0,0.35);
    }}

    /* tytuł */
    .login-title {{
        text-align: center;
        font-size: 31px;
        font-weight: 600;
    }}

    /* separator 'lub' */
    .separator {{
        text-align: center;
        margin: 9px 0 20px 0;
        font-size: 17px;
    }}

    /* linki dolne */
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

    /* całe inputy */
    div[data-baseweb="input"] > div {{
        background-color: #e6eef8;
        font-size: 15px;
        height: 48px;
    }}

    .st-by {{
        padding-right: 0 !important;
    }}
    
    /* normalny hover zamiast czerwonego */
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
    .activate{{
        font-size: 0.95rem;
        line-height: 1.45rem;
        margin-bottom: 20px;
        text-decoration: underline;
    }}
    
    </style>
    """
