import streamlit as st
import json
from ai_engine import gemini_call, parse_json


def show_roadmap():

    st.markdown("<h2 style='color:#1A1A2E;'>📅 4-Week Learning Roadmap</h2>", unsafe_allow_html=True)

    if "result" not in st.session_state:
        st.warning("⚠️ Run Resume Analysis first.")
        return

    result = st.session_state["result"]
    missing_skills = result.get("missing_skills", [])

    if not missing_skills:
        st.success("✅ No missing skills found! Your profile is already a great match.")
        return

    if "roadmap" not in st.session_state:
        with st.spinner("🔍 Generating your personalized learning roadmap..."):
            prompt = f"""
You are an expert career coach. Create a week-by-week learning roadmap for these missing skills.
Return ONLY valid JSON — no extra text, no markdown, no explanation.

Format:
{{
    "roadmap": [
        {{
            "week": "Week 1",
            "skill": "Skill Name",
            "description": "What to learn and why",
            "learning_link": "https://example.com"
        }}
    ]
}}

Rules:
- Create one entry per missing skill
- Use REAL working links (Coursera, YouTube, MDN, official docs, freeCodeCamp)
- Be specific and practical in descriptions

Missing Skills:
{json.dumps(missing_skills)}
"""
            raw, err = gemini_call(prompt)
            if err:
                st.error(f"❌ {err}")
                return
            data, err = parse_json(raw)
            if err:
                st.error(f"❌ {err}")
                return
            st.session_state["roadmap"] = data.get("roadmap", [])

    roadmap = st.session_state.get("roadmap", [])

    if not roadmap:
        st.error("❌ Could not generate roadmap. Please try again.")
        return

    for item in roadmap:
        if not isinstance(item, dict):
            continue
        st.markdown(f"""
        <div style='
            background: rgba(255,255,255,0.6);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(108,99,255,0.18);
            border-radius: 16px;
            padding: 22px 28px;
            margin-bottom: 16px;
            box-shadow: 0 4px 16px rgba(108,99,255,0.07);
        '>
            <div style='font-size:15px;font-weight:700;color:#6C63FF;margin-bottom:8px;'>
                {item.get("week", "Week")} — {item.get("skill", "")}
            </div>
            <p style='color:#374151;font-size:15px;margin-top:12px;margin-bottom:12px;line-height:1.6;'>
                {item.get("description", "")}
            </p>
            <a href="{item.get("learning_link", "#")}" target="_blank" style='
                display: inline-flex;
                align-items: center;
                gap: 6px;
                background: linear-gradient(135deg, #6C63FF, #8B5CF6);
                color: white;
                text-decoration: none;
                padding: 8px 18px;
                border-radius: 8px;
                font-weight: 600;
                font-size: 13px;
                box-shadow: 0 3px 10px rgba(108,99,255,0.25);
            '>🔗 Learn Now</a>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Regenerate Roadmap", use_container_width=True):
        del st.session_state["roadmap"]
        st.rerun()
