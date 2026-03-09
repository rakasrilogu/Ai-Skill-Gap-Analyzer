import streamlit as st
import json
import time
import re
from config import client
from pdf_utils import extract_text
from google.genai import errors


def show_resume_analysis():

    st.markdown("<h2 style='color:#1A1A2E;'>📊 Resume Analysis</h2>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown(
            "<label style='font-weight:600;color:#374151;font-size:15px;'>📄 Upload Resume (PDF)</label>",
            unsafe_allow_html=True,
        )
        resume_file = st.file_uploader("", type=["pdf"], label_visibility="collapsed")

    with col2:
        st.markdown(
            "<label style='font-weight:600;color:#374151;font-size:15px;'>📝 Job Description</label>",
            unsafe_allow_html=True,
        )
        job_description = st.text_area(
            "",
            placeholder="Paste the job description here...",
            height=180,
            label_visibility="collapsed",
        )

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("🚀 Run AI Analysis", use_container_width=True):
        if resume_file and job_description:
            with st.spinner("🔍 Analyzing your resume ..."):

                resume_text = extract_text(resume_file)

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

                raw_text = None
                for attempt in range(3):
                    try:
                        response = client.models.generate_content(
                            model="gemini-2.5-flash",
                            contents=prompt,
                        )
                        raw_text = response.text.strip()
                        break
                    except errors.ClientError as e:
                        if "429" in str(e):
                            wait = (attempt + 1) * 30
                            st.warning(f"⏳ Quota exceeded. Retrying in {wait} seconds...")
                            time.sleep(wait)
                        else:
                            st.error(f"❌ API Error: {e}")
                            break

                if raw_text is None:
                    st.error("❌ Quota exhausted. Please try again later.")
                    return

                raw_text = re.sub(r"```(?:json)?", "", raw_text).strip()
                raw_text = raw_text.replace("```", "").strip()

                start = raw_text.find("{")
                end = raw_text.rfind("}") + 1
                if start == -1 or end == 0:
                    st.error("❌ AI did not return a valid JSON object. Please try again.")
                    st.code(raw_text)
                    return

                clean_json = raw_text[start:end]

                try:
                    result = json.loads(clean_json)
                    # ✅ Store in session_state — roadmap & questions cleared so they regenerate fresh
                    st.session_state["result"] = result
                    st.session_state.pop("roadmap", None)
                    st.session_state.pop("mock_questions", None)
                    st.session_state.pop("evaluations", None)
                    st.success("✅ Analysis Completed! Now visit Roadmap or Interview tabs.")
                except json.JSONDecodeError as e:
                    st.error(f"❌ JSON Parse Error: {e}")
                    st.code(clean_json)
                    return

        else:
            st.warning("⚠️ Please upload a resume and paste a job description.")

    if "result" in st.session_state:
        result = st.session_state["result"]

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Score Card ──────────────────────────────────────────────────────────
        raw_score = result.get("compatibility_score", "N/A")
        if isinstance(raw_score, str):
            raw_score = raw_score.replace("%", "").strip()
        score_display = f"{raw_score}%" if raw_score != "N/A" else "N/A"

        st.markdown(
            f"""
            <div style='background:linear-gradient(135deg,#1A1A2E,#16213E);
                        border-radius:16px;padding:28px 32px;text-align:center;margin-bottom:24px;'>
                <div style='color:#94A3B8;font-size:14px;font-weight:600;letter-spacing:1px;
                            text-transform:uppercase;margin-bottom:8px;'>
                    Compatibility Score
                </div>
                <div style='color:#6EE7B7;font-size:56px;font-weight:800;line-height:1;'>
                    {score_display}
                </div>
                <div style='color:#64748B;font-size:13px;margin-top:8px;'>
                    Based on resume vs job description match
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Matched / Missing Skills ────────────────────────────────────────────
        matched = result.get("matched_skills", [])
        missing = result.get("missing_skills", [])

        if not isinstance(matched, list):
            matched = [str(matched)]
        if not isinstance(missing, list):
            missing = [str(missing)]

        col_a, col_b = st.columns(2, gap="large")

        with col_a:
            st.markdown("""
                <div style='background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.25);
                border-radius:16px;padding:20px 24px;'>
                <div style='font-size:16px;font-weight:700;color:#065F46;margin-bottom:12px;'>✅ Matched Skills</div>
            """, unsafe_allow_html=True)
            if matched:
                for skill in matched:
                    st.markdown(f"""
                        <div style='display:flex;align-items:center;gap:8px;margin-bottom:8px;'>
                            <span style='color:#10B981;font-weight:700;'>✔</span>
                            <span style='color:#1A1A2E;font-weight:500;font-size:14px;'>{skill}</span>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("<p style='color:#6B7280;font-size:13px;'>No matched skills found.</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with col_b:
            st.markdown("""
                <div style='background:rgba(239,68,68,0.07);border:1px solid rgba(239,68,68,0.2);
                border-radius:16px;padding:20px 24px;'>
                <div style='font-size:16px;font-weight:700;color:#991B1B;margin-bottom:12px;'>❌ Missing Skills</div>
            """, unsafe_allow_html=True)
            if missing:
                for skill in missing:
                    st.markdown(f"""
                        <div style='display:flex;align-items:center;gap:8px;margin-bottom:8px;'>
                            <span style='color:#EF4444;font-weight:700;'>✖</span>
                            <span style='color:#1A1A2E;font-weight:500;font-size:14px;'>{skill}</span>
                        </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown("<p style='color:#6B7280;font-size:13px;'>No missing skills found.</p>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # ── Navigation hints ────────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
            <div style='background:rgba(108,99,255,0.06);border:1px solid rgba(108,99,255,0.2);
                        border-radius:12px;padding:16px 20px;text-align:center;'>
                <span style='color:#4C1D95;font-size:14px;font-weight:600;'>
                    ✅ Analysis done! &nbsp;→&nbsp; Visit
                    <b>📅 Roadmap</b> tab to see your learning plan &nbsp;|&nbsp;
                    <b>🎤 Interview</b> tab to practice with AI
                </span>
            </div>
        """, unsafe_allow_html=True)