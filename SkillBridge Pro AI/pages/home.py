import streamlit as st

def show_home():

    st.markdown("""
    <div class="glass">
        <div class="hero-title">🚀 SkillBridge Pro AI</div>
        <div class="hero-sub">AI-Powered Resume Intelligence &amp; Career Acceleration Platform</div>
    </div>
    <br>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div style="background:rgba(108,99,255,0.08);border:1px solid rgba(108,99,255,0.18);border-radius:14px;padding:18px 20px;margin-bottom:14px;">
            <span style="font-size:24px;">📄</span>
            <div style="font-weight:700;color:#1A1A2E;font-size:15px;margin-top:6px;">Resume vs Job AI Analysis</div>
            <div style="color:#6B7280;font-size:13px;margin-top:3px;">Smart match powered by Gemini</div>
        </div>
        <div style="background:rgba(108,99,255,0.08);border:1px solid rgba(108,99,255,0.18);border-radius:14px;padding:18px 20px;margin-bottom:14px;">
            <span style="font-size:24px;">🧠</span>
            <div style="font-weight:700;color:#1A1A2E;font-size:15px;margin-top:6px;">Matched &amp; Missing Skills</div>
            <div style="color:#6B7280;font-size:13px;margin-top:3px;">Gap analysis at a glance</div>
        </div>
        <div style="background:rgba(108,99,255,0.08);border:1px solid rgba(108,99,255,0.18);border-radius:14px;padding:18px 20px;margin-bottom:14px;">
            <span style="font-size:24px;">🎤</span>
            <div style="font-weight:700;color:#1A1A2E;font-size:15px;margin-top:6px;">AI Mock Interview</div>
            <div style="color:#6B7280;font-size:13px;margin-top:3px;">Voice &amp; text evaluation</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="background:rgba(108,99,255,0.08);border:1px solid rgba(108,99,255,0.18);border-radius:14px;padding:18px 20px;margin-bottom:14px;">
            <span style="font-size:24px;">📊</span>
            <div style="font-weight:700;color:#1A1A2E;font-size:15px;margin-top:6px;">Compatibility Score</div>
            <div style="color:#6B7280;font-size:13px;margin-top:3px;">Know how well you fit</div>
        </div>
        <div style="background:rgba(108,99,255,0.08);border:1px solid rgba(108,99,255,0.18);border-radius:14px;padding:18px 20px;margin-bottom:14px;">
            <span style="font-size:24px;">📅</span>
            <div style="font-weight:700;color:#1A1A2E;font-size:15px;margin-top:6px;">4-Week Learning Roadmap</div>
            <div style="color:#6B7280;font-size:13px;margin-top:3px;">Curated resources &amp; links</div>
        </div>
        <div style="background:rgba(108,99,255,0.08);border:1px solid rgba(108,99,255,0.18);border-radius:14px;padding:18px 20px;margin-bottom:14px;">
            <span style="font-size:24px;">📥</span>
            <div style="font-weight:700;color:#1A1A2E;font-size:15px;margin-top:6px;">Professional Report</div>
            <div style="color:#6B7280;font-size:13px;margin-top:3px;">Download full evaluation</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;background:linear-gradient(135deg,rgba(108,99,255,0.12),rgba(167,139,250,0.12));
    border-radius:12px;padding:14px;border:1px solid rgba(108,99,255,0.2);
    color:#4C1D95;font-weight:600;font-size:15px;margin-top:4px;">
        🎯 Use the sidebar to start your journey
    </div>
    """, unsafe_allow_html=True)