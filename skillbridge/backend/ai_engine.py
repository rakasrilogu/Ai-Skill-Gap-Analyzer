from google import genai
from google.genai import errors
import json
import re
import time
import os

# ==========================================================
# Create Gemini client ONCE
# ==========================================================
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set.")

client = genai.Client(api_key=api_key)


# ==========================================================
# Gemini Call
# ==========================================================
def gemini_call(prompt: str):
    start = time.time()

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )

            print(f"✅ Gemini Response Time: {time.time() - start:.2f} sec")

            return response.text.strip(), None

        except errors.ClientError as e:
            if "429" in str(e):
                wait = min((attempt + 1) * 2, 5)
                print(f"Rate limited. Waiting {wait}s...")
                time.sleep(wait)
            else:
                return None, str(e)

        except Exception as e:
            return None, str(e)

    return None, "Quota exhausted. Please try again later."


# ==========================================================
# JSON Parser
# ==========================================================
def parse_json(raw_text: str):
    raw_text = (
        re.sub(r"```(?:json)?", "", raw_text)
        .replace("```", "")
        .strip()
    )

    start = raw_text.find("{")
    end = raw_text.rfind("}") + 1

    if start == -1 or end == 0:
        return None, "No JSON object found."

    try:
        return json.loads(raw_text[start:end]), None

    except json.JSONDecodeError as e:
        return None, str(e)


# ==========================================================
# Resume Analysis
# ==========================================================
def analyze_resume(resume_text: str, job_description: str):

    # Reduce token count
    resume_text = resume_text[:5000]
    job_description = job_description[:2000]

    prompt = f"""
Analyze the resume against the job description.

Return ONLY valid JSON.

{{
    "compatibility_score": 0,
    "matched_skills": [],
    "missing_skills": []
}}

Rules:
- compatibility_score must be integer (0-100)
- minimum 3 matched skills
- minimum 3 missing skills

Resume:
{resume_text}

Job Description:
{job_description}
"""

    raw, err = gemini_call(prompt)

    if err:
        return None, err

    return parse_json(raw)


# ==========================================================
# Learning Roadmap
# ==========================================================
def generate_roadmap(missing_skills: list):

    prompt = f"""
Create a learning roadmap.

Return ONLY JSON.

{{
    "roadmap":[
        {{
            "week":"Week 1",
            "skill":"Skill",
            "description":"Description",
            "learning_link":"https://..."
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


# ==========================================================
# Interview Questions
# ==========================================================
def generate_questions(matched_skills: list, missing_skills: list):

    prompt = f"""
Generate exactly 5 interview questions.

Return ONLY JSON.

{{
    "mock_questions":[]
}}

Matched Skills:
{json.dumps(matched_skills)}

Missing Skills:
{json.dumps(missing_skills)}
"""

    raw, err = gemini_call(prompt)

    if err:
        return None, err

    data, err = parse_json(raw)

    if err:
        return None, err

    return data.get("mock_questions", []), None


# ==========================================================
# Answer Evaluation
# ==========================================================
def evaluate_answer(question: str, answer: str):

    prompt = f"""
Evaluate this interview answer.

Question:
{question}

Answer:
{answer}

Give:

Score: X/10

Technical Accuracy:

Communication:

Strengths:

Ideal Answer:

Improvements:

Keep under 200 words.
"""

    raw, err = gemini_call(prompt)

    if err:
        return f"Could not evaluate - {err}"

    return raw
