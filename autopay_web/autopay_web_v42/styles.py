import streamlit as st

def inject_css():
    st.markdown("""
    <style>
    :root {
        --primary-dark: #424477;
        --primary-accent: #595BAE;
        --success-soft: #6EC189;
        --accent-soft: #DFFCAC;
        --error-light: #FDE8C9;
        --error-main: #D94949;
        --error-dark: #A91D1C;
        --error-deep: #501C4C;

        --bg-main: #F7F8FC;
        --bg-card: #FFFFFF;
        --bg-chart: #F7FAFC;

        --text-main: #1F2340;
        --text-soft: #6B728A;
        --border-soft: #E7EAF3;
        --sidebar-text: #F7F8FF;
    }

    .stApp {
        background: linear-gradient(180deg, #F7F8FC 0%, #F2F5FB 100%);
    }

    header[data-testid="stHeader"] {
        display: block !important;
        visibility: visible !important;
        background: transparent !important;
        height: auto !important;
        min-height: 0 !important;
    }

    [data-testid="stToolbar"] {
        display: flex !important;
        visibility: visible !important;
        height: auto !important;
        right: .5rem !important;
    }

    [data-testid="collapsedControl"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
    }

    button[kind="header"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
    }

    .stAppViewContainer > .main {
        background: linear-gradient(180deg, #EEF2F8 0%, #F7F8FC 100%) !important;
    }

    .block-container {
        padding-top: 0.35rem !important;
        padding-bottom: 1rem !important;
        max-width: 100% !important;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--primary-dark) 0%, var(--primary-accent) 100%);
        border-right: 1px solid rgba(255,255,255,0.08);
        box-shadow: inset -1px 0 0 rgba(255,255,255,0.06);
    }

    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] small,
    [data-testid="stSidebar"] div[data-testid="stMetricLabel"],
    [data-testid="stSidebar"] div[data-testid="stMetricValue"] {
        color: var(--sidebar-text) !important;
    }

    [data-testid="stSidebar"] hr {
        border: none;
        height: 1px;
        background: rgba(255,255,255,0.12);
        margin: 14px 0;
    }

    [data-testid="stSidebar"] div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.10) !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        border-radius: 20px !important;
        padding: 12px 14px !important;
        box-shadow:
            0 6px 16px rgba(0,0,0,0.08),
            inset 0 1px 0 rgba(255,255,255,0.08) !important;
        transition: transform 0.18s ease, box-shadow 0.18s ease !important;
    }

    [data-testid="stSidebar"] div[data-testid="stMetric"]:hover {
        transform: translateY(-3px) !important;
        box-shadow:
            0 14px 24px rgba(0,0,0,0.12),
            inset 0 1px 0 rgba(255,255,255,0.10) !important;
    }

    [data-testid="stSidebar"] .stDateInput input,
    [data-testid="stSidebar"] .stTextInput input {
        background: rgba(255,255,255,0.96) !important;
        color: var(--text-main) !important;
        border: 1px solid rgba(255,255,255,0.18) !important;
        border-radius: 14px !important;
    }

    [data-testid="stSidebar"] .stDateInput input:focus,
    [data-testid="stSidebar"] .stTextInput input:focus {
        border-color: rgba(223,252,172,0.55) !important;
        box-shadow: 0 0 0 3px rgba(223,252,172,0.12) !important;
    }

    [data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background: rgba(255,255,255,0.96) !important;
        border: 1px solid rgba(255,255,255,0.18) !important;
        border-radius: 14px !important;
        color: var(--text-main) !important;
    }

    [data-testid="stSidebar"] div[data-baseweb="select"] * {
        color: var(--text-main) !important;
    }

    [data-testid="stSidebar"] .stButton button {
        background: linear-gradient(135deg, var(--primary-accent) 0%, #6a6cc9 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 16px !important;
        font-weight: 800 !important;
        box-shadow:
            0 10px 24px rgba(89,91,174,0.35),
            inset 0 1px 0 rgba(255,255,255,0.14) !important;
        transition: transform 0.18s ease, box-shadow 0.18s ease, filter 0.18s ease !important;
        animation: pulseGlow 2.8s infinite;
    }

    [data-testid="stSidebar"] .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow:
            0 16px 30px rgba(89,91,174,0.44),
            inset 0 1px 0 rgba(255,255,255,0.20) !important;
        filter: brightness(1.04) !important;
    }

    [data-testid="stSidebar"] .stSlider label,
    [data-testid="stSidebar"] .stSlider span {
        color: var(--sidebar-text) !important;
    }


    .header-box {
        position: relative;
        overflow: hidden;
        background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary-accent) 100%);
        border-radius: 24px;
        padding: 22px 26px;
        box-shadow:
            0 12px 28px rgba(66, 68, 119, 0.22),
            inset 0 1px 0 rgba(255,255,255,0.10);
        margin-bottom: 16px;
        border: 1px solid rgba(255,255,255,0.10);
        animation: fadeUp 0.55s ease-out;
    }

    .header-box::after {
        content: "";
        position: absolute;
        top: -40%;
        left: -20%;
        width: 40%;
        height: 180%;
        background: linear-gradient(90deg, rgba(255,255,255,0.00), rgba(255,255,255,0.08), rgba(255,255,255,0.00));
        transform: rotate(18deg);
        animation: shineMove 6s linear infinite;
        pointer-events: none;
    }

    .header-title {
        position: relative;
        color: white;
        font-size: 2rem;
        font-weight: 800;
        margin: 0 0 8px 0;
        line-height: 1.2;
    }

    .header-meta {
        position: relative;
        color: #F4F7FF;
        font-size: 0.98rem;
        margin: 2px 0;
        line-height: 1.45;
    }

    .header-badge {
        position: relative;
        display: inline-block;
        margin-top: 12px;
        background: rgba(223, 252, 172, 0.18);
        color: var(--accent-soft);
        border: 1px solid rgba(223, 252, 172, 0.35);
        border-radius: 12px;
        padding: 6px 10px;
        font-size: 0.85rem;
        font-weight: 700;
    }

    .section-card {
        background: linear-gradient(180deg, #FFFFFF 0%, #FCFCFF 100%);
        border: 1px solid var(--border-soft);
        border-radius: 22px;
        padding: 14px 16px 10px 16px;
        box-shadow:
            0 10px 24px rgba(31,35,64,0.06),
            0 2px 8px rgba(31,35,64,0.03);
        margin-bottom: 16px;
        animation: fadeUp 0.55s ease-out;
    }

    .chart-card {
        background: linear-gradient(180deg, #F9FBFD 0%, #F3F7FB 100%);
        border: 1px solid #E7ECF3;
        border-radius: 22px;
        padding: 12px;
        box-shadow:
            0 10px 24px rgba(31,35,64,0.06),
            inset 0 1px 0 rgba(255,255,255,0.75);
        height: 100%;
        transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
        animation: fadeUp 0.55s ease-out;
    }

    .chart-card:hover {
        transform: perspective(1000px) translateY(-6px) rotateX(2deg) scale(1.01);
        box-shadow:
            0 20px 36px rgba(31,35,64,0.12),
            0 6px 14px rgba(31,35,64,0.07),
            inset 0 1px 0 rgba(255,255,255,0.85);
        border-color: #D6DDF0;
    }

    .chart-title {
        font-size: 1rem;
        font-weight: 800;
        color: var(--text-main);
        margin: 4px 6px 0 6px;
    }

    .chart-sub {
        font-size: 0.84rem;
        color: var(--text-soft);
        margin: 0 6px 8px 6px;
    }

    div[data-testid="stMetric"] {
        background: linear-gradient(145deg, #FFFFFF 0%, #F6F8FC 100%);
        border: 1px solid var(--border-soft);
        border-radius: 20px;
        padding: 10px 14px;
        box-shadow: 0 10px 24px rgba(31,35,64,0.06);
        animation: fadeUp 0.5s ease-out;
        transition: transform 0.18s ease, box-shadow 0.18s ease;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 18px 30px rgba(31,35,64,0.10);
    }

    div[data-testid="stMetricLabel"] {
        color: #6B728A !important;
        font-weight: 700 !important;
    }

    div[data-testid="stMetricValue"] {
        color: var(--text-main) !important;
        font-weight: 800 !important;
    }

    div[data-testid="stDataFrame"] {
        background: linear-gradient(180deg, #FFFFFF 0%, #FBFCFF 100%) !important;
        border-radius: 16px !important;
        overflow: hidden !important;
        border: 1px solid #DCE3F0 !important;
        box-shadow: 0 10px 20px rgba(31,35,64,0.05);
        animation: fadeUp 0.55s ease-out;
    }

    .helper-note {
        background: linear-gradient(135deg, #F7FFE8 0%, #F1FBD8 100%);
        border: 1px solid #D8EDAA;
        color: #45603A;
        border-radius: 16px;
        padding: 10px 14px;
        margin-bottom: 10px;
        font-size: 0.93rem;
        font-weight: 600;
        animation: fadeUp 0.5s ease-out;
    }

    .login-spacer-top { height: 8vh; }
    .login-shell { max-width: 430px; margin: 0 auto; }

    .login-box {
        width: 100%;
        background: linear-gradient(180deg, #FFFFFF 0%, #FCFCFF 100%);
        border: 1px solid var(--border-soft);
        border-radius: 24px;
        padding: 24px 22px 18px 22px;
        box-shadow:
            0 18px 40px rgba(31,35,64,0.10),
            inset 0 1px 0 rgba(255,255,255,0.92);
        animation: fadeUp 0.55s ease-out;
    }

    .login-brand {
        text-align: center;
        margin-bottom: 14px;
    }

    .login-brand-title {
        font-size: 1.55rem;
        font-weight: 800;
        color: var(--text-main);
        margin-bottom: 6px;
        letter-spacing: -0.02em;
    }

    .login-brand-sub {
        font-size: 0.90rem;
        color: var(--text-soft);
        margin-bottom: 2px;
    }

    .login-divider {
        height: 1px;
        background: linear-gradient(90deg, rgba(0,0,0,0.00), rgba(89,91,174,0.22), rgba(0,0,0,0.00));
        margin: 12px 0 16px 0;
    }

    .login-card-title {
        text-align: center;
        font-size: 1rem;
        font-weight: 800;
        color: var(--text-main);
        margin-bottom: 4px;
    }

    .login-card-sub {
        text-align: center;
        font-size: 0.86rem;
        color: var(--text-soft);
        margin-bottom: 16px;
    }

    div[data-testid="stForm"] {
        border: none !important;
        background: transparent !important;
        padding: 0 !important;
        box-shadow: none !important;
    }

    div[data-testid="stForm"] input {
        border-radius: 12px !important;
        border: 1px solid #D9E1EF !important;
        background: #F8FAFD !important;
        color: var(--text-main) !important;
    }

    div[data-testid="stForm"] input:focus {
        border-color: var(--primary-accent) !important;
        box-shadow: 0 0 0 3px rgba(89,91,174,0.12) !important;
        background: #FFFFFF !important;
    }

    div[data-testid="stForm"] label {
        color: var(--text-main) !important;
        font-weight: 700 !important;
    }

    div[data-testid="stForm"] button {
        background: linear-gradient(135deg, var(--primary-dark) 0%, var(--primary-accent) 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        font-weight: 800 !important;
        min-height: 42px !important;
        box-shadow: 0 10px 24px rgba(89,91,174,0.28) !important;
    }

    div[data-testid="stForm"] button:hover {
        filter: brightness(1.04) !important;
        box-shadow: 0 14px 28px rgba(89,91,174,0.34) !important;
    }

    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(14px) scale(0.985); }
        to { opacity: 1; transform: translateY(0) scale(1); }
    }

    @keyframes pulseGlow {
        0% { box-shadow: 0 10px 24px rgba(89,91,174,0.28), inset 0 1px 0 rgba(255,255,255,0.12); }
        50% { box-shadow: 0 14px 28px rgba(89,91,174,0.40), 0 0 0 4px rgba(89,91,174,0.08), inset 0 1px 0 rgba(255,255,255,0.18); }
        100% { box-shadow: 0 10px 24px rgba(89,91,174,0.28), inset 0 1px 0 rgba(255,255,255,0.12); }
    }

    @keyframes shineMove {
        0% { transform: translateX(-120%) rotate(18deg); }
        100% { transform: translateX(420%) rotate(18deg); }
    }
    </style>
    """, unsafe_allow_html=True)
