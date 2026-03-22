import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { generateRoadmap } from '../utils/api';
import { useAppState } from '../hooks/useAppState';

const WEEK_COLORS = [
  { bg: 'rgba(108,99,255,0.08)', border: 'rgba(108,99,255,0.2)', accent: '#6C63FF', tag: 'rgba(108,99,255,0.12)', tagText: '#4C1D95' },
  { bg: 'rgba(16,185,129,0.07)', border: 'rgba(16,185,129,0.2)', accent: '#10B981', tag: 'rgba(16,185,129,0.12)', tagText: '#065F46' },
  { bg: 'rgba(245,158,11,0.07)', border: 'rgba(245,158,11,0.2)', accent: '#F59E0B', tag: 'rgba(245,158,11,0.12)', tagText: '#92400E' },
  { bg: 'rgba(239,68,68,0.06)',  border: 'rgba(239,68,68,0.18)',  accent: '#EF4444', tag: 'rgba(239,68,68,0.1)',  tagText: '#991B1B' },
];

function RoadmapCard({ item, index }) {
  const color = WEEK_COLORS[index % WEEK_COLORS.length];
  return (
    <div style={{
      background: 'white',
      border: `1.5px solid ${color.border}`,
      borderRadius: 16,
      padding: '24px 28px',
      boxShadow: '0 2px 12px rgba(0,0,0,0.04)',
      position: 'relative',
      overflow: 'hidden',
    }}>
      {/* Left accent bar */}
      <div style={{
        position: 'absolute', left: 0, top: 0, bottom: 0,
        width: 4, background: color.accent, borderRadius: '16px 0 0 16px',
      }} />

      <div style={{ paddingLeft: 8 }}>
        {/* Week badge */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
          <span style={{
            padding: '4px 12px',
            background: color.tag,
            color: color.tagText,
            borderRadius: 20,
            fontSize: 12,
            fontWeight: 700,
            letterSpacing: 0.5,
          }}>
            {item.week}
          </span>
          <span style={{
            fontWeight: 800,
            fontSize: 16,
            color: '#1A1A2E',
          }}>
            {item.skill}
          </span>
        </div>

        {/* Description */}
        <p style={{
          color: '#374151',
          fontSize: 14,
          lineHeight: 1.7,
          marginBottom: 16,
        }}>
          {item.description}
        </p>

        {/* Learn Now button */}
        <a
          href={item.learning_link}
          target="_blank"
          rel="noopener noreferrer"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: 6,
            background: `linear-gradient(135deg, ${color.accent}, ${color.accent}dd)`,
            color: 'white',
            textDecoration: 'none',
            padding: '8px 18px',
            borderRadius: 8,
            fontWeight: 600,
            fontSize: 13,
            boxShadow: `0 3px 10px ${color.border}`,
            transition: 'transform 0.15s, box-shadow 0.15s',
          }}
          onMouseOver={e => { e.currentTarget.style.transform = 'translateY(-1px)'; }}
          onMouseOut={e => { e.currentTarget.style.transform = 'translateY(0)'; }}
        >
          🔗 Learn Now
        </a>
      </div>
    </div>
  );
}

export default function RoadmapPage() {
  const navigate = useNavigate();
  const { analysisResult, roadmap, setRoadmap } = useAppState();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!analysisResult) return;
    if (roadmap) return;
    fetchRoadmap();
    // eslint-disable-next-line
  }, [analysisResult]);

  async function fetchRoadmap() {
    setLoading(true);
    setError('');
    try {
      const data = await generateRoadmap(analysisResult.missing_skills);
      setRoadmap(data);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to generate roadmap.');
    } finally {
      setLoading(false);
    }
  }

  function handleRegenerate() {
    setRoadmap(null);
    fetchRoadmap();
  }

  if (!analysisResult) {
    return (
      <div className="page-container">
        <div className="alert alert-warning">
          ⚠️ Please complete the <strong>Resume Analysis</strong> first.
          <button className="btn btn-outline btn-sm" style={{ marginLeft: 12 }} onClick={() => navigate('/analysis')}>
            Go to Analysis →
          </button>
        </div>
      </div>
    );
  }

  if (!analysisResult.missing_skills?.length) {
    return (
      <div className="page-container">
        <div className="alert alert-success">
          🏆 No missing skills found! Your profile is already a perfect match for this job.
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      {/* Header */}
      <div style={{ marginBottom: 32 }}>
        <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--purple)', letterSpacing: 1.5, textTransform: 'uppercase', marginBottom: 8 }}>
          Step 3 of 4
        </div>
        <h1 style={{ fontSize: 32, fontWeight: 900, color: 'var(--dark)', letterSpacing: '-0.5px', marginBottom: 8 }}>
          📅 Learning Roadmap
        </h1>
        <p style={{ color: 'var(--gray)', fontSize: 15 }}>
          Your personalized week-by-week plan to bridge the skill gaps and become job-ready.
        </p>
      </div>

      {/* Skills overview */}
      <div className="card" style={{
        marginBottom: 28,
        background: 'linear-gradient(135deg, var(--purple-bg), rgba(139,92,246,0.06))',
        border: '1.5px solid var(--purple-border)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16 }}>
          <div>
            <div style={{ fontWeight: 700, color: 'var(--purple-dark)', fontSize: 15, marginBottom: 8 }}>
              🎯 Skills to master — {analysisResult.missing_skills.length} total
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
              {analysisResult.missing_skills.map((skill, i) => (
                <span key={i} className="badge badge-purple">{skill}</span>
              ))}
            </div>
          </div>
          <button className="btn btn-outline btn-sm" onClick={handleRegenerate} disabled={loading}>
            🔄 Regenerate
          </button>
        </div>
      </div>

      {loading && (
        <div className="spinner-wrap">
          <div className="spinner" />
          <div style={{ color: 'var(--gray)', fontSize: 14 }}>Generating your personalized roadmap...</div>
        </div>
      )}

      {error && (
        <div className="alert alert-error" style={{ marginBottom: 20 }}>
          ⚠️ {error}
        </div>
      )}

      {roadmap && !loading && (
        <>
          {/* Timeline */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16, marginBottom: 32 }}>
            {roadmap.map((item, i) => (
              <div key={i} style={{ display: 'flex', gap: 16, alignItems: 'flex-start' }}>
                {/* Step number */}
                <div style={{
                  minWidth: 40, height: 40,
                  borderRadius: '50%',
                  background: 'var(--purple)',
                  color: 'white',
                  fontWeight: 800, fontSize: 14,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  boxShadow: '0 4px 12px rgba(108,99,255,0.3)',
                  marginTop: 4,
                  flexShrink: 0,
                }}>
                  {i + 1}
                </div>
                {/* Connector line */}
                <div style={{ flex: 1, position: 'relative' }}>
                  {i < roadmap.length - 1 && (
                    <div style={{
                      position: 'absolute',
                      left: -28, top: '100%',
                      width: 2, height: 16,
                      background: 'var(--purple-border)',
                    }} />
                  )}
                  <RoadmapCard item={item} index={i} />
                </div>
              </div>
            ))}
          </div>

          {/* Progress summary */}
          <div className="card" style={{ marginBottom: 24 }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 16 }}>
              <div>
                <div style={{ fontWeight: 800, fontSize: 16, color: 'var(--dark)', marginBottom: 4 }}>
                  📈 Your Learning Plan
                </div>
                <div style={{ color: 'var(--gray)', fontSize: 13 }}>
                  {roadmap.length} skill{roadmap.length > 1 ? 's' : ''} · Estimated {roadmap.length} week{roadmap.length > 1 ? 's' : ''} to complete
                </div>
              </div>
              <div style={{ display: 'flex', gap: 12 }}>
                <button className="btn btn-outline btn-sm" onClick={() => navigate('/interview')}>
                  🎤 Start Mock Interview →
                </button>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
