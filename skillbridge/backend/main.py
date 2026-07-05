  from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import io
import os
from typing import Optional
from ai_engine import (
    analyze_resume,
    generate_roadmap,
    generate_questions,
    evaluate_answer,
)
from pdf_utils import extract_text_from_bytes
from report_builder import build_pdf_report

app = FastAPI(title="SkillBridge Pro AI API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RoadmapRequest(BaseModel):
    missing_skills: list[str]

class QuestionsRequest(BaseModel):
    matched_skills: list[str]
    missing_skills: list[str]

class EvaluateRequest(BaseModel):
    question: str
    answer: str

class ReportRequest(BaseModel):
    candidate_name: Optional[str] = ""
    job_role: Optional[str] = ""
    compatibility_score: int
    matched_skills: list[str]
    missing_skills: list[str]
    questions: list[str]
    evaluations: dict
    roadmap: Optional[list] = []

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/api/analyze-resume")
async def analyze_resume_endpoint(
    resume: UploadFile = File(...),
    job_description: str = Form(...),
):
    if not resume.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    contents = await resume.read()
    resume_text = extract_text_from_bytes(contents)
    if not resume_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from PDF.")
    result, err = analyze_resume(resume_text, job_description)
    if err:
        raise HTTPException(status_code=500, detail=err)
    return result

@app.post("/api/generate-roadmap")
async def generate_roadmap_endpoint(req: RoadmapRequest):
    if not req.missing_skills:
        raise HTTPException(status_code=400, detail="No missing skills provided.")
    roadmap, err = generate_roadmap(req.missing_skills)
    if err:
        raise HTTPException(status_code=500, detail=err)
    return {"roadmap": roadmap}

@app.post("/api/generate-questions")
async def generate_questions_endpoint(req: QuestionsRequest):
    questions, err = generate_questions(req.matched_skills, req.missing_skills)
    if err:
        raise HTTPException(status_code=500, detail=err)
    return {"questions": questions}

@app.post("/api/evaluate-answer")
async def evaluate_answer_endpoint(req: EvaluateRequest):
    if not req.answer.strip():
        raise HTTPException(status_code=400, detail="Answer cannot be empty.")
    evaluation = evaluate_answer(req.question, req.answer)
    return {"evaluation": evaluation}

@app.post("/api/generate-report")
async def generate_report_endpoint(req: ReportRequest):
    pdf_bytes = build_pdf_report(
        result={
            "compatibility_score": req.compatibility_score,
            "matched_skills": req.matched_skills,
            "missing_skills": req.missing_skills,
        },
        questions=req.questions,
        evaluations=req.evaluations,
        candidate_name=req.candidate_name,
        job_role=req.job_role,
        roadmap=req.roadmap,
    )
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=SkillBridge_Report.pdf"},
    )







    
