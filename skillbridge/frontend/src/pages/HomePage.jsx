import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppState } from '../hooks/useAppState';

const features = [
  { icon: '📄', title: 'Resume vs Job AI Analysis', desc: 'Smart match powered by Gemini 2.5 Flash' },
  { icon: '📊', title: 'Compatibility Score', desc: 'Know exactly how well you fit the role' },
  { icon: '🧠', title: 'Matched & Missing Skills', desc: 'Precise gap analysis at a glance' },
  { icon: '📅', title: '4-Week Learning Roadmap', desc: 'Curated resources & real learning links' },
  { icon: '🎤', title: 'AI Mock Interview', desc: 'Text-based evaluation with detailed feedback' },
  { icon: '📥', title: 'Professional PDF Report', desc: 'Download your full evaluation report' },
];

const steps = [
  { num: '01', title: 'Upload Resume', desc: 'Upload your PDF resume' },
  { num: '02', title: 'Paste Job Description', desc: 'Add the target job description' },
  { num: '03', title: 'Run AI Analysis', desc: 'Get instant compatibility score & skill gaps' },
  { num: '04', title: 'Learn & Practice', desc: 'Follow roadmap and ace the mock interview' },
];

export default function HomePage() {
  const navigate = useNavigate();
  const { analysisResult } = useAppState();

  return (
    <div className="page-container">
      {/* Hero */}
      <div style={{
        background: 'linear-gradient(135deg, #1A1A2E 0%, #16213E 50%, #0F3460 100%)',
        borderRadius: 20,
        padding: '52px 48px',
        marginBottom: 40,
        position: 'relative',
        overflow: 'hidden',
      }}>
        <div style={{
          position: 'absolute', top: -60, right: -60,
          width: 300, height: 300,
          background: 'radial-gradient(circle, rgba(108,99,255,0.3) 0%, transparent 70%)',
          borderRadius: '50%',
        }} />
        <div style={{
          position: 'absolute', bottom: -80, left: -40,
          width: 250, height: 250,
          background: 'radial-gradient(circle, rgba(139,92,246,0.2) 0%, transparent 70%)',
          borderRadius: '50%',
        }} />
        <div style={{ position: 'relative', zIndex: 1 }}>
          <div style={{ fontSize: 13, fontWeight: 700, color: '#8B5CF6', letterSpacing: 2, textTransform: 'uppercase', marginBottom: 16 }}>
            🚀 AI-Powered Career Platform
          </div>
          <h1 style={{ fontSize: 44, fontWeight: 900, color: 'white', lineHeight: 1.1, marginBottom: 16, letterSpacing: '-1px' }}>
            Bridge the Gap Between<br />
            <span style={{ background: 'linear-gradient(135deg, #6C63FF, #8B5CF6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              Your Skills & Your Dream Job
            </span>
          </h1>
          <p style={{ fontSize: 17, color: '#94A3B8', maxWidth: 560, lineHeight: 1.7, marginBottom: 32 }}>
            Upload your resume, paste a job description, and let our Gemini-powered AI analyze your fit, identify skill gaps, and guide your learning journey.
          </p>
          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
            <button className="btn btn-primary" style={{ fontSize: 15, padding: '13px 28px' }} onClick={() => navigate('/analysis')}>
              🚀 Start Analysis
            </button>
            {analysisResult && (
              <button className="btn btn-outline" style={{ color: 'white', borderColor: 'rgba(255,255,255,0.3)', fontSize: 15, padding: '13px 28px' }} onClick={() => navigate('/roadmap')}>
                📅 View Roadmap
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Stats if analysis done */}
      {analysisResult && (
        <div className="card" style={{ marginBottom: 36, background: 'linear-gradient(135deg, rgba(108,99,255,0.06), rgba(139,92,246,0.06))', border: '1px solid var(--purple-border)' }}>
          <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--purple)', letterSpacing: 1, textTransform: 'uppercase', marginBottom: 20 }}>
            📊 Your Last Analysis
          </div>
          <div className="grid-3">
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 40, fontWeight: 900, color: 'var(--purple)' }}>{analysisResult.compatibility_score}%</div>
              <div style={{ fontSize: 13, color: 'var(--gray)', fontWeight: 500 }}>Compatibility Score</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 40, fontWeight: 900, color: 'var(--green)' }}>{analysisResult.matched_skills?.length || 0}</div>
              <div style={{ fontSize: 13, color: 'var(--gray)', fontWeight: 500 }}>Matched Skills</div>
            </div>
            <div style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 40, fontWeight: 900, color: 'var(--red)' }}>{analysisResult.missing_skills?.length || 0}</div>
              <div style={{ fontSize: 13, color: 'var(--gray)', fontWeight: 500 }}>Missing Skills</div>
            </div>
          </div>
        </div>
      )}

      {/* Features Grid */}
      <div style={{ marginBottom: 40 }}>
        <h2 style={{ fontSize: 24, fontWeight: 800, color: 'var(--dark)', marginBottom: 6, letterSpacing: '-0.5px' }}>
          Everything You Need to Land the Job
        </h2>
        <p style={{ color: 'var(--gray)', fontSize: 15, marginBottom: 24 }}>
          Six powerful AI-driven tools in one platform
        </p>
        <div className="grid-3">
          {features.map((f, i) => (
            <div key={i} className="card-glass" style={{ padding: '22px 24px' }}>
              <div style={{ fontSize: 28, marginBottom: 12 }}>{f.icon}</div>
              <div style={{ fontWeight: 700, color: 'var(--dark)', fontSize: 15, marginBottom: 5 }}>{f.title}</div>
              <div style={{ color: 'var(--gray)', fontSize: 13, lineHeight: 1.5 }}>{f.desc}</div>
            </div>
          ))}
        </div>
      </div>

      {/* How it works */}
      <div className="card" style={{ marginBottom: 32 }}>
        <h2 style={{ fontSize: 20, fontWeight: 800, color: 'var(--dark)', marginBottom: 24, letterSpacing: '-0.3px' }}>
          ⚡ How It Works
        </h2>
        <div className="grid-2">
          {steps.map((s, i) => (
            <div key={i} style={{ display: 'flex', gap: 16, alignItems: 'flex-start' }}>
              <div style={{
                minWidth: 44, height: 44, borderRadius: 12,
                background: 'var(--purple-bg)',
                border: '1.5px solid var(--purple-border)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontWeight: 800, fontSize: 13, color: 'var(--purple)',
              }}>{s.num}</div>
              <div>
                <div style={{ fontWeight: 700, fontSize: 15, color: 'var(--dark)', marginBottom: 3 }}>{s.title}</div>
                <div style={{ fontSize: 13, color: 'var(--gray)', lineHeight: 1.5 }}>{s.desc}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* CTA */}
      <div style={{
        textAlign: 'center',
        background: 'linear-gradient(135deg, var(--purple-bg), rgba(139,92,246,0.08))',
        border: '1.5px solid var(--purple-border)',
        borderRadius: 16,
        padding: '32px',
      }}>
        <div style={{ fontSize: 20, fontWeight: 800, color: 'var(--purple-dark)', marginBottom: 8 }}>
          🎯 Ready to accelerate your career?
        </div>
        <div style={{ color: 'var(--gray)', marginBottom: 20, fontSize: 14 }}>
          Start with your resume — the AI will guide you through the rest.
        </div>
        <button className="btn btn-primary" style={{ fontSize: 15, padding: '13px 32px' }} onClick={() => navigate('/analysis')}>
          Get Started Free →
        </button>
      </div>
    </div>
  );
}
