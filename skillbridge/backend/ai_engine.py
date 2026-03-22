from google import genai
from google.genai import errors
import json
import re
import time
import os


def get_client():
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set.")
    return genai.Client(api_key=api_key)


def gemini_call(prompt: str):
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
                time.sleep(wait)
            else:
                return None, str(e)
        except Exception as e:
            return None, str(e)
    return None, "Quota exhausted. Please try again later."


def parse_json(raw_text: str):
    raw_text = re.sub(r"```(?:json)?", "", raw_text).strip().replace("```", "").strip()
    start = raw_text.find("{")
    end = raw_text.rfind("}") + 1
    if start == -1 or end == 0:
        return None, "No JSON object found."
    try:
        return json.loads(raw_text[start:end]), None
    except json.JSONDecodeError as e:
        return None, str(e)


def analyze_resume(resume_text: str, job_description: str):
    prompt = f"""
You are an expert career advisor. Analyze the resume against the job description.
Return STRICTLY valid JSON only. No extra text, no markdown.

Format:
{{
    "compatibility_score": 85,
    "matched_skills": ["skill1", "skill2"],
    "missing_skills": ["skill3", "skill4"]
}}

Rules:
- compatibility_score must be an INTEGER (0-100)
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


def generate_roadmap(missing_skills: list):
    prompt = f"""
You are an expert career coach. Create a week-by-week learning roadmap for these missing skills.
Return ONLY valid JSON — no extra text, no markdown.

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


def generate_questions(matched_skills: list, missing_skills: list):
    prompt = f"""
You are a senior technical interviewer. Generate exactly 5 smart interview questions
based on the candidate's matched and missing skills.

Return ONLY valid JSON — no markdown, no extra text.

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


def evaluate_answer(question: str, answer: str):
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
