import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({ baseURL: API_BASE });

export async function analyzeResume(resumeFile, jobDescription) {
  const form = new FormData();
  form.append('resume', resumeFile);
  form.append('job_description', jobDescription);
  const { data } = await api.post('/api/analyze-resume', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export async function generateRoadmap(missingSkills) {
  const { data } = await api.post('/api/generate-roadmap', { missing_skills: missingSkills });
  return data.roadmap;
}

export async function generateQuestions(matchedSkills, missingSkills) {
  const { data } = await api.post('/api/generate-questions', {
    matched_skills: matchedSkills,
    missing_skills: missingSkills,
  });
  return data.questions;
}

export async function evaluateAnswer(question, answer) {
  const { data } = await api.post('/api/evaluate-answer', { question, answer });
  return data.evaluation;
}

export async function generateReport(payload) {
  const res = await api.post('/api/generate-report', payload, { responseType: 'blob' });
  return res.data;
}

export default api;
