import streamlit as st
from styles import load_styles
from pages.home import show_home
from pages.resume_analysis import show_resume_analysis
from pages.roadmap import show_roadmap
from pages.mock_interview import show_mock_interview

# ── PAGE CONFIG ──
st.set_page_config(page_title="SkillBridge Pro AI", page_icon="🎯", layout="wide")

# ── LOAD GLOBAL STYLES ──
load_styles()

# ── SIDEBAR ──
st.sidebar.markdown("""
    <div style='text-align:center;padding:16px 0 8px;'>
        <div style='font-size:28px;'>🎯</div>
        <div style='font-size:18px;font-weight:800;color:#1A1A2E;letter-spacing:-0.5px;'>SkillBridge Pro AI</div>
        <div style='font-size:12px;color:#6B7280;margin-top:4px;font-weight:500;'>Career Acceleration Platform</div>
    </div>
    <hr style='border-color:rgba(108,99,255,0.15);margin:12px 0;'>
""", unsafe_allow_html=True)

page = st.sidebar.radio("Navigate", [
    "Home",
    "Resume Analysis",
    "Learning Roadmap",
    "Mock Interview"
], label_visibility="collapsed")

# ── ROUTING ──
if page == "Home":
    show_home()
elif page == "Resume Analysis":
    show_resume_analysis()
elif page == "Learning Roadmap":
    show_roadmap()
elif page == "Mock Interview":
    show_mock_interview()