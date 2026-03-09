import streamlit as st
import json
import time
import re
from config import client
from google.genai import errors


def generate_roadmap(missing_skills):
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
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            raw = response.text.strip()
            raw = re.sub(r"```(?:json)?", "", raw).strip().replace("```", "").strip()
            start = raw.find("{")
            end = raw.rfind("}") + 1
            if start == -1 or end == 0:
                return None, "AI did not return valid JSON."
            data = json.loads(raw[start:end])
            return data.get("roadmap", []), None
        except errors.ClientError as e:
            if "429" in str(e):
                wait = (attempt + 1) * 30
                st.warning(f"⏳ Quota exceeded. Retrying in {wait} seconds...")
                time.sleep(wait)
            else:
                return None, str(e)
    return None, "Quota exhausted. Please try again later."


def show_roadmap():

    st.markdown("<h2 style='color:#1A1A2E;'>📅 4-Week Learning Roadmap</h2>", unsafe_allow_html=True)

    # ── Guard ───────────────────────────────────────────────────────────────
    if "result" not in st.session_state:
        st.warning("⚠️ Run Resume Analysis first.")
        return

    result = st.session_state["result"]
    missing_skills = result.get("missing_skills", [])

    if not missing_skills:
        st.success("✅ No missing skills found! Your profile is already a great match.")
        return

    # ── Generate roadmap once, cache in session_state["roadmap"] ────────────
    if "roadmap" not in st.session_state:
        with st.spinner("🔍 Generating your personalized learning roadmap..."):
            roadmap, error = generate_roadmap(missing_skills)
            if error:
                st.error(f"❌ {error}")
                return
            st.session_state["roadmap"] = roadmap

    roadmap = st.session_state.get("roadmap", [])

    if not roadmap:
        st.error("❌ Could not generate roadmap. Please try again.")
        return

    # ── Display ─────────────────────────────────────────────────────────────
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

    # ── Regenerate ──────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔄 Regenerate Roadmap", use_container_width=True):
        del st.session_state["roadmap"]
        st.rerun()