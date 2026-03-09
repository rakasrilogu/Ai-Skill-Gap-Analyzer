
from google import genai
import json

API_KEY = "AIzaSyDp8Qp8u4Gnvc3xUWqoLz0vdkRZ8Oa2mhg"
client = genai.Client(api_key=API_KEY)

def analyze_resume(resume_text, job_description):

    prompt = f"""
Return STRICTLY valid JSON only.

Format:
{{
    "compatibility_score": "",
    "matched_skills": [],
    "missing_skills": [],
    "roadmap": [
        {{
            "week": "",
            "skill": "",
            "description": "",
            "learning_link": ""
        }}
    ],
    "mock_questions": []
}}

Resume:
{resume_text}

Job Description:
{job_description}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    raw_text = response.text.strip()

    if raw_text.startswith("```"):
        raw_text = raw_text.split("```")[1]

    start = raw_text.find("{")
    end = raw_text.rfind("}") + 1
    clean_json = raw_text[start:end]

    return json.loads(clean_json)
