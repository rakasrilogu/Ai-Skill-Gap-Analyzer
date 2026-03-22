import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { RadialBarChart, RadialBar, PolarAngleAxis, ResponsiveContainer } from 'recharts';
import { analyzeResume } from '../utils/api';
import { useAppState } from '../hooks/useAppState';

function ScoreGauge({ score }) {
  const color = score >= 75 ? '#10B981' : score >= 50 ? '#6C63FF' : '#EF4444';
  const data = [{ value: score, fill: color }];
  return (
    <div style={{ textAlign: 'center' }}>
      <div style={{ width: 200, height: 200, margin: '0 auto', position: 'relative' }}>
        <ResponsiveContainer width="100%" height="100%">
          <RadialBarChart
            cx="50%" cy="50%"
            innerRadius="70%" outerRadius="100%"
            barSize={16}
            data={data}
            startAngle={90} endAngle={-270}
          >
            <PolarAngleAxis type="number" domain={[0, 100]} tick={false} />
            <RadialBar background={{ fill: '#F3F4F6' }} dataKey="value" cornerRadius={8} />
          </RadialBarChart>
        </ResponsiveContainer>
        <div style={{
          position: 'absolute', top: '50%', left: '50%',
          transform: 'translate(-50%, -50%)',
          textAlign: 'center',
        }}>
          <div style={{ fontSize: 36, fontWeight: 900, color, lineHeight: 1 }}>{score}%</div>
          <div style={{ fontSize: 11, color: '#6B7280', marginTop: 2, fontWeight: 600 }}>Match</div>
        </div>
      </div>
      <div style={{ fontSize: 14, fontWeight: 700, color: '#1A1A2E', marginTop: 8 }}>
        {score >= 75 ? '🏆 Excellent Fit!' : score >= 50 ? '✅ Good Match' : '⚡ Needs Work'}
      </div>
      <div style={{ fontSize: 12, color: '#6B7280', marginTop: 2 }}>Based on resume vs job description</div>
    </div>
  );
}

export default function ResumeAnalysisPage() {
  const navigate = useNavigate();
  const { setAnalysisResult, setRoadmap, setMockQuestions, setEvaluations } = useAppState();

  const [resumeFile, setResumeFile] = useState(null);
  const [jobDesc, setJobDesc] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const [dragOver, setDragOver] = useState(false);

  async function handleAnalyze() {
    if (!resumeFile || !jobDesc.trim()) {
      setError('Please upload a resume PDF and paste the job description.');
      return;
    }
    setError('');
    setLoading(true);
    try {
      const data = await analyzeResume(resumeFile, jobDesc);
      setResult(data);
      setAnalysisResult(data);
      setRoadmap(null);
      setMockQuestions(null);
      setEvaluations({});
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Analysis failed. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  function handleDrop(e) {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file && file.type === 'application/pdf') setResumeFile(file);
    else setError('Please drop a valid PDF file.');
  }

  return (
    <div className="page-container">
      {/* Header */}
      <div style={{ marginBottom: 32 }}>
        <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--purple)', letterSpacing: 1.5, textTransform: 'uppercase', marginBottom: 8 }}>
          Step 1 of 4
        </div>
        <h1 style={{ fontSize: 32, fontWeight: 900, color: 'var(--dark)', letterSpacing: '-0.5px', marginBottom: 8 }}>
          📊 Resume Analysis
        </h1>
        <p style={{ color: 'var(--gray)', fontSize: 15 }}>
          Upload your resume and paste the job description to get your AI-powered compatibility score and skill gap analysis.
        </p>
      </div>

      {/* Upload Section */}
      <div className="grid-2" style={{ marginBottom: 24 }}>
        {/* PDF Upload */}
        <div>
          <label className="form-label">📄 Resume (PDF)</label>
          <div
            onDragOver={e => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleDrop}
            onClick={() => document.getElementById('resume-input').click()}
            style={{
              border: `2px dashed ${dragOver ? 'var(--purple)' : resumeFile ? '#10B981' : '#E5E7EB'}`,
              borderRadius: 12,
              padding: '32px 24px',
              textAlign: 'center',
              cursor: 'pointer',
              background: dragOver ? 'var(--purple-bg)' : resumeFile ? 'rgba(16,185,129,0.05)' : 'white',
              transition: 'all 0.2s',
            }}
          >
            <input
              id="resume-input"
              type="file"
              accept=".pdf"
              style={{ display: 'none' }}
              onChange={e => setResumeFile(e.target.files[0])}
            />
            {resumeFile ? (
              <>
                <div style={{ fontSize: 32, marginBottom: 8 }}>✅</div>
                <div style={{ fontWeight: 700, color: '#065F46', fontSize: 14 }}>{resumeFile.name}</div>
                <div style={{ color: '#6B7280', fontSize: 12, marginTop: 4 }}>
                  {(resumeFile.size / 1024).toFixed(1)} KB · Click to change
                </div>
              </>
            ) : (
              <>
                <div style={{ fontSize: 32, marginBottom: 8 }}>📄</div>
                <div style={{ fontWeight: 600, color: 'var(--dark)', fontSize: 14 }}>Drop PDF here or click to browse</div>
                <div style={{ color: '#6B7280', fontSize: 12, marginTop: 4 }}>PDF files only</div>
              </>
            )}
          </div>
        </div>

        {/* Job Description */}
        <div>
          <label className="form-label">📝 Job Description</label>
          <textarea
            className="form-textarea"
            placeholder="Paste the full job description here — requirements, responsibilities, qualifications..."
            value={jobDesc}
            onChange={e => setJobDesc(e.target.value)}
            style={{ height: 160, fontSize: 13 }}
          />
          <div style={{ fontSize: 12, color: '#9CA3AF', marginTop: 6 }}>
            {jobDesc.length} characters
          </div>
        </div>
      </div>

      {error && (
        <div className="alert alert-error" style={{ marginBottom: 20 }}>
          ⚠️ {error}
        </div>
      )}

      <button
        className="btn btn-primary btn-full"
        onClick={handleAnalyze}
        disabled={loading || !resumeFile || !jobDesc.trim()}
        style={{ fontSize: 16, padding: '14px', marginBottom: 36 }}
      >
        {loading ? '🔍 Analyzing...' : '🚀 Run AI Analysis'}
      </button>

      {loading && (
        <div className="spinner-wrap">
          <div className="spinner" />
          <div style={{ color: 'var(--gray)', fontSize: 14 }}>Gemini AI is analyzing your resume...</div>
        </div>
      )}

      {/* Results */}
      {result && !loading && (
        <>
          <div className="divider" />
          <div style={{ marginBottom: 28 }}>
            <h2 style={{ fontSize: 22, fontWeight: 800, color: 'var(--dark)', marginBottom: 4 }}>
              ✅ Analysis Complete
            </h2>
            <p style={{ color: 'var(--gray)', fontSize: 14 }}>Here's your AI-powered evaluation</p>
          </div>

          {/* Score + Skills grid */}
          <div style={{ display: 'grid', gridTemplateColumns: '220px 1fr 1fr', gap: 24, marginBottom: 28 }}>
            {/* Gauge */}
            <div className="card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <ScoreGauge score={result.compatibility_score} />
            </div>

            {/* Matched Skills */}
            <div className="card" style={{
              background: 'rgba(16,185,129,0.05)',
              border: '1px solid rgba(16,185,129,0.2)',
            }}>
              <div style={{ fontWeight: 800, color: '#065F46', fontSize: 16, marginBottom: 16 }}>
                ✅ Matched Skills
                <span className="badge badge-green" style={{ marginLeft: 8 }}>
                  {result.matched_skills?.length}
                </span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {result.matched_skills?.map((skill, i) => (
                  <div key={i} style={{
                    display: 'flex', alignItems: 'center', gap: 10,
                    padding: '8px 12px',
                    background: 'rgba(16,185,129,0.08)',
                    borderRadius: 8,
                  }}>
                    <span style={{ color: '#10B981', fontWeight: 700, fontSize: 14 }}>✔</span>
                    <span style={{ color: '#1A1A2E', fontWeight: 500, fontSize: 13 }}>{skill}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Missing Skills */}
            <div className="card" style={{
              background: 'rgba(239,68,68,0.04)',
              border: '1px solid rgba(239,68,68,0.18)',
            }}>
              <div style={{ fontWeight: 800, color: '#991B1B', fontSize: 16, marginBottom: 16 }}>
                ❌ Missing Skills
                <span className="badge badge-red" style={{ marginLeft: 8 }}>
                  {result.missing_skills?.length}
                </span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {result.missing_skills?.map((skill, i) => (
                  <div key={i} style={{
                    display: 'flex', alignItems: 'center', gap: 10,
                    padding: '8px 12px',
                    background: 'rgba(239,68,68,0.06)',
                    borderRadius: 8,
                  }}>
                    <span style={{ color: '#EF4444', fontWeight: 700, fontSize: 14 }}>✖</span>
                    <span style={{ color: '#1A1A2E', fontWeight: 500, fontSize: 13 }}>{skill}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Next steps */}
          <div className="card" style={{
            background: 'linear-gradient(135deg, var(--purple-bg), rgba(139,92,246,0.06))',
            border: '1.5px solid var(--purple-border)',
          }}>
            <div style={{ fontWeight: 700, color: 'var(--purple-dark)', fontSize: 15, marginBottom: 16 }}>
              🎯 What's Next?
            </div>
            <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
              <button className="btn btn-primary" onClick={() => navigate('/roadmap')}>
                📅 Generate Learning Roadmap →
              </button>
              <button className="btn btn-outline" onClick={() => navigate('/interview')}>
                🎤 Start Mock Interview →
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
