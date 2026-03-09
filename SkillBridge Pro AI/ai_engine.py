from google import genai
import json
import re
import time
from google.genai import errors


# ── Create client safely ─────────────────────────────────────────────────────
def get_client():
    try:
        import streamlit as st
        api_key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        import os
        api_key = os.environ.get("GEMINI_API_KEY", "")
    return genai.Client(api_key=api_key)


# ── Helper: call Gemini with retry ──────────────────────────────────────────
def gemini_call(prompt):
    try:
        import streamlit as st
        show_warning = st.warning
    except Exception:
        show_warning = print

    client = get_client()
    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            return response.text.strip(), None
        except errors.ClientError as e:
            if "429" in str(e):
                wait = (attempt + 1) * 30
                show_warning(f"⏳ Quota exceeded. Retrying in {wait} seconds...")
                time.sleep(wait)
            else:
                return None, str(e)
    return None, "Quota exhausted. Please try again later."


# ── Helper: parse JSON safely ────────────────────────────────────────────────
def parse_json(raw_text):
    raw_text = re.sub(r"```(?:json)?", "", raw_text).strip().replace("```", "").strip()
    start = raw_text.find("{")
    end = raw_text.rfind("}") + 1
    if start == -1 or end == 0:
        return None, "No JSON object found in response."
    try:
        return json.loads(raw_text[start:end]), None
    except json.JSONDecodeError as e:
        return None, str(e)


# ── Resume Analysis ──────────────────────────────────────────────────────────
def analyze_resume(resume_text, job_description):
    prompt = f"""
You are an expert career advisor. Analyze the resume against the job description.
Return STRICTLY valid JSON only. No extra text, no markdown, no explanation.

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
    raw, err = gemini_call(prompt)
    if err:
        return None, err
    return parse_json(raw)


# ── Roadmap Generation ───────────────────────────────────────────────────────
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
    raw, err = gemini_call(prompt)
    if err:
        return None, err
    data, err = parse_json(raw)
    if err:
        return None, err
    return data.get("roadmap", []), None


# ── Interview Questions ──────────────────────────────────────────────────────
def generate_questions(matched_skills, missing_skills):
    prompt = f"""
You are a senior technical interviewer. Generate exactly 5 smart interview questions
based on the candidate's matched and missing skills.

Return ONLY valid JSON — no markdown, no extra text.

Format:
{{
    "mock_questions": [
        "Question 1?",
        "Question 2?",
        "Question 3?",
        "Question 4?",
        "Question 5?"
    ]
}}

Rules:
- Mix questions from matched skills (test depth) and missing skills (test awareness)
- Questions must be practical and role-specific
- No yes/no questions

Matched Skills: {json.dumps(matched_skills)}
Missing Skills: {json.dumps(missing_skills)}
"""
    raw, err = gemini_call(prompt)
    if err:
        return None, err
    data, err = parse_json(raw)
    if err:
        return None, err
    return data.get("mock_questions", []), None


# ── Answer Evaluation ────────────────────────────────────────────────────────
def evaluate_answer(question, answer):
    prompt = f"""
You are a senior technical interviewer. Give structured, honest, and motivating feedback.

Question: {question}
Candidate Answer: {answer}

Respond in this exact format:

Score: X/10
Technical Accuracy: Good / Average / Poor
Communication Quality: Good / Average / Poor

What You Did Well:
(1-2 lines)

Ideal Answer (Key Points):
- point 1
- point 2
- point 3

How To Improve:
- tip 1
- tip 2

Keep total response under 200 words. Be encouraging but honest.
"""
    raw, err = gemini_call(prompt)
    if err:
        return f"Could not evaluate — {err}"
    return raw
