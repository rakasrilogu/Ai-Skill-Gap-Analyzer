import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 30000, // 30 sec timeout (important)
});

// 🔁 Helper delay function
const delay = (ms) => new Promise((res) => setTimeout(res, ms));

/* =========================
   RESUME ANALYSIS (FIXED)
========================= */
export async function analyzeResume(resumeFile, jobDescription) {
  const form = new FormData();
  form.append('resume', resumeFile);
  form.append('job_description', jobDescription);

  const MAX_RETRIES = 3;

  for (let i = 0; i < MAX_RETRIES; i++) {
    try {
      const { data } = await api.post('/api/analyze-resume', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      return data;

    } catch (error) {
      const status = error?.response?.status;

      console.log(`Attempt ${i + 1} failed`, status);

      // Retry only for 503 (AI busy) or timeout
      if ((status === 503 || error.code === 'ECONNABORTED') && i < MAX_RETRIES - 1) {
        await delay(1500); // wait before retry
        continue;
      }

      // Final error message
      throw new Error(
        status === 503
          ? "AI is busy right now. Please try again in a few seconds."
          : "Something went wrong. Please try again."
      );
    }
  }
}

/* =========================
   ROADMAP
========================= */
export async function generateRoadmap(missingSkills) {
  const MAX_RETRIES = 2;

  for (let i = 0; i < MAX_RETRIES; i++) {
    try {
      const { data } = await api.post('/api/generate-roadmap', {
        missing_skills: missingSkills,
      });
      return data.roadmap;

    } catch (error) {
      if (i < MAX_RETRIES - 1) {
        await delay(1000);
        continue;
      }
      throw new Error("Failed to generate roadmap. Try again.");
    }
  }
}

/* =========================
   QUESTIONS
========================= */
export async function generateQuestions(matchedSkills, missingSkills) {
  const MAX_RETRIES = 2;

  for (let i = 0; i < MAX_RETRIES; i++) {
    try {
      const { data } = await api.post('/api/generate-questions', {
        matched_skills: matchedSkills,
        missing_skills: missingSkills,
      });
      return data.questions;

    } catch (error) {
      if (i < MAX_RETRIES - 1) {
        await delay(1000);
        continue;
      }
      throw new Error("Failed to generate questions.");
    }
  }
}

/* =========================
   EVALUATION
========================= */
export async function evaluateAnswer(question, answer) {
  try {
    const { data } = await api.post('/api/evaluate-answer', {
      question,
      answer,
    });
    return data.evaluation;

  } catch (error) {
    throw new Error("Failed to evaluate answer.");
  }
}

/* =========================
   REPORT
========================= */
export async function generateReport(payload) {
  try {
    const res = await api.post('/api/generate-report', payload, {
      responseType: 'blob',
    });
    return res.data;

  } catch (error) {
    throw new Error("Failed to generate report.");
  }
}

export default api;
