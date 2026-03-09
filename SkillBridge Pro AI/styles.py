import streamlit as st

def load_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    * { font-family: 'Plus Jakarta Sans', sans-serif; }

    /* ── HIDE DEFAULT STREAMLIT PAGE NAV ── */
    [data-testid="stSidebarNav"] {
        display: none !important;
    }

    /* ── BACKGROUND ── */
    .stApp {
        background: linear-gradient(135deg, #EEF2FF 0%, #F5F0FF 40%, #EDF9FF 100%);
        min-height: 100vh;
    }

    /* ── SIDEBAR ── */
    section[data-testid="stSidebar"] {
        background: rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(108, 99, 255, 0.15) !important;
        box-shadow: 4px 0 24px rgba(108, 99, 255, 0.08) !important;
    }
    section[data-testid="stSidebar"] * {
        color: #1A1A2E !important;
    }
    section[data-testid="stSidebar"] .stRadio label {
        font-weight: 500 !important;
        color: #1A1A2E !important;
    }

    /* ── GLASS CARD ── */
    .glass {
        background: rgba(255, 255, 255, 0.55);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 48px 52px;
        border: 1px solid rgba(108, 99, 255, 0.18);
        box-shadow:
            0 8px 32px rgba(108, 99, 255, 0.10),
            0 1px 0 rgba(255,255,255,0.8) inset;
        margin-top: 30px;
    }

    /* ── HERO TITLE ── */
    .hero-title {
        font-size: 48px;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(90deg, #6C63FF, #A78BFA, #38BDF8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -1px;
        line-height: 1.1;
    }

    .hero-sub {
        text-align: center;
        font-size: 18px;
        color: #4B5563;
        margin-top: 12px;
        font-weight: 500;
    }

    /* ── FEATURE ITEMS ── */
    .glass b {
        color: #4C1D95;
        font-weight: 600;
    }

    .glass i {
        color: #6C63FF;
        font-weight: 500;
    }

    /* ── HEADINGS ── */
    h1, h2, h3, h4, h5 {
        color: #1A1A2E !important;
        font-weight: 700 !important;
    }

    /* ── LABELS & TEXT ── */
    label, p, .stMarkdown p, div[data-testid="stMarkdownContainer"] p {
        color: #374151 !important;
        font-weight: 500;
    }

    /* ── METRIC ── */
    [data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.6);
        backdrop-filter: blur(12px);
        border-radius: 16px;
        padding: 16px 24px;
        border: 1px solid rgba(108, 99, 255, 0.15);
        box-shadow: 0 4px 16px rgba(108, 99, 255, 0.08);
    }
    [data-testid="metric-container"] label {
        color: #6C63FF !important;
        font-weight: 600 !important;
    }
    [data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: #1A1A2E !important;
        font-weight: 800 !important;
        font-size: 32px !important;
    }

    /* ── BUTTONS ── */
    .stButton>button {
        background: linear-gradient(135deg, #6C63FF, #8B5CF6);
        color: white !important;
        font-weight: 600;
        border-radius: 12px;
        border: none;
        padding: 10px 24px;
        box-shadow: 0 4px 15px rgba(108, 99, 255, 0.3);
        transition: all 0.2s ease;
        letter-spacing: 0.3px;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #5A52E0, #7C3AED);
        box-shadow: 0 6px 20px rgba(108, 99, 255, 0.45);
        transform: translateY(-1px);
    }

    /* ── DOWNLOAD BUTTON ── */
    .stDownloadButton>button {
        background: linear-gradient(135deg, #059669, #10B981);
        color: white !important;
        font-weight: 600;
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 15px rgba(16, 185, 129, 0.3);
        transition: all 0.2s ease;
    }
    .stDownloadButton>button:hover {
        background: linear-gradient(135deg, #047857, #059669);
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.45);
        transform: translateY(-1px);
    }

    /* ── TEXT AREA ── */
    textarea {
        background: rgba(255, 255, 255, 0.85) !important;
        color: #1A1A2E !important;
        border-radius: 12px !important;
        border: 1.5px solid rgba(108, 99, 255, 0.2) !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 15px !important;
    }
    textarea:focus {
        border-color: #6C63FF !important;
        box-shadow: 0 0 0 3px rgba(108, 99, 255, 0.12) !important;
    }

    /* ── FILE UPLOADER ── */
    [data-testid="stFileUploader"] {
        background: rgba(255, 255, 255, 0.6);
        border-radius: 16px;
        border: 2px dashed rgba(108, 99, 255, 0.3);
        padding: 8px;
    }

    /* ── RADIO ── */
    .stRadio > div {
        background: rgba(255, 255, 255, 0.5);
        border-radius: 12px;
        padding: 8px 12px;
        border: 1px solid rgba(108, 99, 255, 0.1);
    }

    /* ── DIVIDER ── */
    hr {
        border-color: rgba(108, 99, 255, 0.15) !important;
    }

    /* ── SPINNER ── */
    .stSpinner > div {
        border-top-color: #6C63FF !important;
    }

    /* ── ALERTS ── */
    .stWarning {
        background: rgba(251, 191, 36, 0.12) !important;
        border: 1px solid rgba(251, 191, 36, 0.3) !important;
        border-radius: 12px !important;
        color: #92400E !important;
    }
    .stSuccess {
        background: rgba(16, 185, 129, 0.12) !important;
        border: 1px solid rgba(16, 185, 129, 0.3) !important;
        border-radius: 12px !important;
        color: #065F46 !important;
    }
    .stInfo {
        background: rgba(108, 99, 255, 0.08) !important;
        border: 1px solid rgba(108, 99, 255, 0.2) !important;
        border-radius: 12px !important;
        color: #3730A3 !important;
    }
    .stError {
        background: rgba(239, 68, 68, 0.08) !important;
        border: 1px solid rgba(239, 68, 68, 0.2) !important;
        border-radius: 12px !important;
        color: #991B1B !important;
    }

    /* ── ROADMAP WEEK LABEL ── */
    .violet-week {
        color: #6C63FF;
        font-weight: 700;
        font-size: 17px;
        background: rgba(108, 99, 255, 0.08);
        padding: 8px 16px;
        border-radius: 10px;
        display: inline-block;
        margin-bottom: 6px;
        border: 1px solid rgba(108, 99, 255, 0.18);
    }

    /* ── SUBHEADER ── */
    .stMarkdown h2, .stMarkdown h3 {
        color: #1A1A2E !important;
        border-bottom: 2px solid rgba(108, 99, 255, 0.15);
        padding-bottom: 6px;
    }

    /* ── CODE BLOCK ── */
    .stCode {
        border-radius: 12px !important;
    }
    </style>
    """, unsafe_allow_html=True)