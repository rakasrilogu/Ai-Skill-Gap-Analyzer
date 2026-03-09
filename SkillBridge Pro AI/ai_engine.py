from google import genai
import streamlit as st
import json
import re
import time
from google.genai import errors

def get_client():
    api_key = st.secrets["GEMINI_API_KEY"]
    return genai.Client(api_key=api_key)

def gemini_call(prompt):
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
                st.warning(f"⏳ Quota exceeded. Retrying in {wait} seconds...")
                time.sleep(wait)
            else:
                return None, str(e)
    return None, "Quota exhausted. Please try again later."

def parse_json(raw_text):
    raw_text = re.sub(r"```(?:json)?", "", raw_text).strip().replace("```", "").strip()
    start = raw_text.find("{")
    end = raw_text.rfind("}") + 1
    if start == -1 or end == 0:
        return None, "No JSON object found."
    try:
        return json.loads(raw_text[start:end]), None
    except json.JSONDecodeError as e:
        return None, str(e)

def analyze_resume(resume_text, job_description):
    prompt = f"""
You are an expert career advisor. Analyze the resume against the job description.
Return STRICTLY valid JSON only. No extra text, no markdown.

Format:
{{
    "compatibility_score": 85,
    "matched_skills": ["skill1", "skill2"],
    "missing_skills": ["skill3", "skill4"]
}}

Resume:
{resume_text}

Job Description:
{job_description}
"""
    raw, err = gemini_call(prompt)
    if err:
        return None, err
    return parse_json(raw)

def generate_roadmap(missing_skills):
    prompt = f"""
You are an expert career coach. Create a learning roadmap for these missing skills.
Return ONLY valid JSON.

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

def generate_questions(matched_skills, missing_skills):
    prompt = f"""
You are a senior technical interviewer. Generate exactly 5 interview questions.
Return ONLY valid JSON.

Format:
{{
    "mock_questions": ["Q1?", "Q2?", "Q3?", "Q4?", "Q5?"]
}}

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

def evaluate_answer(question, answer):
    prompt = f"""
You are a senior technical interviewer. Give structured feedback.

Question: {question}
Candidate Answer: {answer}

Format:
Score: X/10
Technical Accuracy: Good / Average / Poor
Communication Quality: Good / Average / Poor

What You Did Well:
(1-2 lines)

Ideal Answer (Key Points):
- point 1
- point 2

How To Improve:
- tip 1
- tip 2

Under 200 words.
"""
    raw, err = gemini_call(prompt)
    if err:
        return f"Could not evaluate — {err}"
    return raw
    
