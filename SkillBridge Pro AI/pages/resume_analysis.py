import streamlit as st
import json
import time
import re
from ai_engine import gemini_call, parse_json
from pdf_utils import extract_text


def show_resume_analysis():

    st.markdown("<h2 style='color:#1A1A2E;'>📊 Resume Analysis</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("<label style='font-weight:600;color:#374151;font-size:15px;'>📄 Upload Resume (PDF)</label>", unsafe_allow_html=True)
        resume_file = st.file_uploader("", type=["pdf"], label_visibility="collapsed")

    with col2:
        st.markdown("<label style='font-weight:600;color:#374151;font-size:15px;'>📝 Job Description</label>", unsafe_allow_html=True)
        job_description = st.text_area("", placeholder="Paste the job description here...", height=180, label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚀 Run AI Analysis", use_container_width=True):
        if resume_file and job_description:

            resume_text = extract_text(resume_file)

            for key in ["result", "roadmap", "mock_questions", "evaluations"]:
                st.session_state.pop(key, None)

            prompt = f"""
You are an expert career advisor. Analyze the resume against the job description and return STRICTLY valid JSON only.
No extra text, no markdown, no explanation — ONLY the JSON object.

Format:
{{
    "compatibility_score": 85,
    "matched_skills": ["skill1", "skill2"],
    "missing_skills": ["skill3", "skill4"]
}}

Rules:
- compatibility_score must be an INTEGER (0-100), not a string
- matched_skills and missing_skills must be arrays of strings
- Return at least 3 matched_skills and 3 missing_skills

Resume:
{resume_text}

Job Description:
{job_description}
"""

            with st.spinner("🔍 Analyzing your resume..."):
                raw_text, err = gemini_call(prompt)
                if err:
                    st.error(f"❌ {err}")
                    return

            result, err = parse_json(raw_text)
            if err:
                st.error(f"❌ JSON Error: {err}")
                return

            st.session_state["result"] = result
            st.success("✅ Analysis Complete!")

        else:
            st.warning("⚠️ Please upload a resume and paste a job description.")

    if "result" in st.session_state:
        result = st.session_state["result"]

        st.markdown("<br>", unsafe_allow_html=True)

        raw_score = result.get("compatibility_score", "N/A")
        if isinstance(raw_score, str):
            raw_score = raw_score.replace("%", "").strip()
        score_display = f"{raw_score}%" if raw_score != "N/A" else "N/A"

        st.markdown(f"""
            <div style='background:linear-gradient(135deg,#1A1A2E,#16213E);
                        border-radius:16px;padding:28px 32px;text-align:center;margin-bottom:24px;'>
                <div style='color:#94A3B8;font-size:14px;font-weight:600;letter-spacing:1px;
                            text-transform:uppercase;margin-bottom:8px;'>Compatibility Score</div>
                <div style='color:#6EE7B7;font-size:56px;font-weight:800;line-height:1;'>{score_display}</div>
                <div style='color:#64748B;font-size:13px;margin-top:8px;'>Based on resume vs job description match</div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        matched = result.get("matched_skills", [])
        missing = result.get("missing_skills", [])
        if not isinstance(matched, list): matched = [str(matched)]
        if not isinstance(missing, list): missing = [str(missing)]

        col_a, col_b = st.columns(2, gap="large")

        with col_a:
            st.markdown("""
                <div style='background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.25);
                border-radius:16px;padding:20px 24px;'>
                <div style='font-size:16px;font-weight:700;color:#065F46;margin-bottom:12px;'>✅ Matched Skills</div>
            """, unsafe_allow_html=True)
            for skill in matched:
                st.markdown(f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:8px;'><span style='color:#10B981;font-weight:700;'>✔</span><span style='color:#1A1A2E;font-weight:500;font-size:14px;'>{skill}</span></div>", unsafe_allow_html=True)
            if not matched:
                st.markdown("<p style='color:#6B7280;font-size:13px;'>No matched skills found.</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_b:
            st.markdown("""
                <div style='background:rgba(239,68,68,0.07);border:1px solid rgba(239,68,68,0.2);
                border-radius:16px;padding:20px 24px;'>
                <div style='font-size:16px;font-weight:700;color:#991B1B;margin-bottom:12px;'>❌ Missing Skills</div>
            """, unsafe_allow_html=True)
            for skill in missing:
                st.markdown(f"<div style='display:flex;align-items:center;gap:8px;margin-bottom:8px;'><span style='color:#EF4444;font-weight:700;'>✖</span><span style='color:#1A1A2E;font-weight:500;font-size:14px;'>{skill}</span></div>", unsafe_allow_html=True)
            if not missing:
                st.markdown("<p style='color:#6B7280;font-size:13px;'>No missing skills found.</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
            <div style='background:rgba(108,99,255,0.06);border:1px solid rgba(108,99,255,0.2);
                        border-radius:12px;padding:16px 20px;text-align:center;'>
                <span style='color:#4C1D95;font-size:14px;font-weight:600;'>
                    ✅ Analysis done! &nbsp;→&nbsp; Visit
                    <b>📅 Roadmap</b> tab &nbsp;|&nbsp;
                    <b>🎤 Interview</b> tab
                </span>
            </div>
        """, unsafe_allow_html=True)
