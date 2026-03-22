import React, { useState, useRef, useCallback, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { generateQuestions, evaluateAnswer, generateReport } from '../utils/api';
import { useAppState } from '../hooks/useAppState';

// ── Helpers ────────────────────────────────────────────────────────────────

function extractScore(text) {
  const m = text?.match(/Score[:\s]+(\d+)\s*\/\s*10/i);
  return m ? parseInt(m[1]) : null;
}

function ScoreBadge({ score }) {
  if (score === null) return null;
  const color = score >= 7 ? '#10B981' : score >= 5 ? '#F59E0B' : '#EF4444';
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', padding: '3px 10px',
      background: `${color}18`, border: `1px solid ${color}55`,
      borderRadius: 20, fontSize: 13, fontWeight: 700, color,
    }}>{score}/10</span>
  );
}

function ScoreBar({ score, max = 10 }) {
  const color = score >= 7 ? '#10B981' : score >= 5 ? '#F59E0B' : '#EF4444';
  return (
    <div style={{ background: '#F3F4F6', borderRadius: 6, height: 8, overflow: 'hidden', flex: 1 }}>
      <div style={{ height: '100%', width: `${(score / max) * 100}%`, background: color, borderRadius: 6, transition: 'width 0.5s ease' }} />
    </div>
  );
}

// ── Voice wave ─────────────────────────────────────────────────────────────

function VoiceWave({ active }) {
  const h = [4, 8, 14, 20, 14, 24, 18, 12, 22, 16, 10, 18, 8, 14, 6];
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 3, height: 36 }}>
      {h.map((v, i) => (
        <div key={i} style={{
          width: 4, borderRadius: 4,
          background: active ? 'var(--purple)' : '#D1D5DB',
          height: active ? v : 4,
          transition: 'height 0.15s ease, background 0.3s',
          animation: active ? `wb ${0.4 + i * 0.06}s ease-in-out infinite alternate` : 'none',
        }} />
      ))}
      <style>{`
        @keyframes wb { from{transform:scaleY(0.3)} to{transform:scaleY(1.1)} }
        @keyframes pulse-red { 0%,100%{box-shadow:0 0 0 0 rgba(239,68,68,0.4)} 50%{box-shadow:0 0 0 8px rgba(239,68,68,0)} }
      `}</style>
    </div>
  );
}

// ── Speech Recognition Hook ────────────────────────────────────────────────

function useSpeech() {
  const [listening, setListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interim, setInterim] = useState('');
  const [err, setErr] = useState('');
  const [supported, setSupported] = useState(false);
  const recRef = useRef(null);
  const finalRef = useRef('');

  useEffect(() => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) { setSupported(false); return; }
    setSupported(true);
    const rec = new SR();
    rec.continuous = true; rec.interimResults = true; rec.lang = 'en-US'; rec.maxAlternatives = 1;
    rec.onstart = () => { setListening(true); setErr(''); };
    rec.onresult = (e) => {
      let fin = finalRef.current, tmp = '';
      for (let i = e.resultIndex; i < e.results.length; i++) {
        if (e.results[i].isFinal) fin += e.results[i][0].transcript + ' ';
        else tmp += e.results[i][0].transcript;
      }
      finalRef.current = fin; setTranscript(fin); setInterim(tmp);
    };
    rec.onerror = (e) => {
      const m = { 'no-speech': 'No speech detected — speak closer to mic.', 'not-allowed': 'Microphone denied — allow it in browser settings.', 'network': 'Network error.', 'audio-capture': 'No microphone found.', 'aborted': '' };
      setErr(m[e.error] ?? `Error: ${e.error}`);
      setListening(false);
    };
    rec.onend = () => { setListening(false); setInterim(''); };
    recRef.current = rec;
    return () => rec.stop();
  }, []);

  const start = useCallback(() => { setErr(''); try { recRef.current?.start(); } catch (_) {} }, []);
  const stop  = useCallback(() => { recRef.current?.stop(); setListening(false); setInterim(''); }, []);
  const clear = useCallback(() => { recRef.current?.stop(); finalRef.current = ''; setTranscript(''); setInterim(''); setListening(false); }, []);
  const setManual = useCallback((t) => { finalRef.current = t; setTranscript(t); }, []);

  return { listening, transcript, interim, err, supported, start, stop, clear, setManual };
}

// ── Question Card ──────────────────────────────────────────────────────────

function QuestionCard({ question, index, total, evaluation, onEvaluate, evaluating }) {
  const [mode, setMode] = useState('type');
  const [typed, setTyped] = useState('');
  const [open, setOpen] = useState(true);
  const score = evaluation ? extractScore(evaluation.evaluation) : null;
  const { listening, transcript, interim, err: speechErr, supported, start, stop, clear, setManual } = useSpeech();

  const currentAns = mode === 'voice' ? transcript : typed;
  const displayVoice = transcript + interim;

  function switchMode(m) { stop(); setMode(m); }

  return (
    <div className="card-glass" style={{ marginBottom: 20 }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 14, cursor: 'pointer', marginBottom: open ? 20 : 0 }}
           onClick={() => setOpen(o => !o)}>
        <div style={{
          minWidth: 36, height: 36, borderRadius: '50%', flexShrink: 0,
          background: evaluation ? 'rgba(16,185,129,0.1)' : 'var(--purple-bg)',
          border: `2px solid ${evaluation ? '#10B981' : 'var(--purple)'}`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontWeight: 800, fontSize: 13, color: evaluation ? '#10B981' : 'var(--purple)',
        }}>{evaluation ? '✓' : index}</div>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--gray)', textTransform: 'uppercase', letterSpacing: 1, marginBottom: 4 }}>
            Question {index} of {total}
          </div>
          <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--dark)', lineHeight: 1.5 }}>{question}</div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {score !== null && <ScoreBadge score={score} />}
          <span style={{ color: 'var(--gray)', fontSize: 18 }}>{open ? '▲' : '▼'}</span>
        </div>
      </div>

      {open && (
        <>
          {!evaluation && (
            <>
              {/* Mode Toggle */}
              <div style={{ display: 'flex', gap: 8, marginBottom: 18 }}>
                {[
                  { id: 'type',  label: '✍️ Type Answer' },
                  { id: 'voice', label: `🎤 Voice Answer${!supported ? ' (Chrome/Edge only)' : ''}` },
                ].map(({ id, label }) => (
                  <button key={id} onClick={() => switchMode(id)}
                    disabled={id === 'voice' && !supported}
                    style={{
                      flex: 1, padding: '10px', borderRadius: 10, border: 'none',
                      cursor: (id === 'voice' && !supported) ? 'not-allowed' : 'pointer',
                      fontWeight: 700, fontSize: 13, fontFamily: 'inherit', transition: 'all 0.2s',
                      background: mode === id ? 'var(--purple)' : '#F3F4F6',
                      color: mode === id ? 'white' : (id === 'voice' && !supported) ? '#C4B5FD' : '#6B7280',
                    }}>{label}</button>
                ))}
              </div>

              {/* TYPE MODE */}
              {mode === 'type' && (
                <div>
                  <label className="form-label">Your Answer</label>
                  <textarea className="form-textarea"
                    placeholder="Type your detailed answer here — speak as if in a real interview..."
                    value={typed} onChange={e => setTyped(e.target.value)}
                    style={{ height: 150, fontSize: 14 }} />
                  <div style={{ fontSize: 12, color: '#9CA3AF', marginTop: 4 }}>{typed.length} characters</div>
                </div>
              )}

              {/* VOICE MODE */}
              {mode === 'voice' && (
                <div>
                  {/* Recording box */}
                  <div style={{
                    background: listening ? 'rgba(108,99,255,0.05)' : '#FAFAFA',
                    border: `2px solid ${listening ? 'var(--purple)' : '#E5E7EB'}`,
                    borderRadius: 14, padding: '20px 22px', marginBottom: 14, transition: 'all 0.3s',
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 14 }}>
                      <div>
                        <div style={{ fontWeight: 700, fontSize: 15, color: listening ? 'var(--purple)' : 'var(--dark)' }}>
                          {listening ? '🔴 Recording...' : '🎤 Voice Recording'}
                        </div>
                        <div style={{ fontSize: 12, color: '#9CA3AF', marginTop: 3 }}>
                          {listening ? 'Speak naturally — words appear below in real time' : 'Click Start to speak your answer naturally'}
                        </div>
                      </div>
                      <VoiceWave active={listening} />
                    </div>

                    {/* Live interim */}
                    {listening && interim && (
                      <div style={{
                        background: 'rgba(108,99,255,0.08)', border: '1px dashed var(--purple-border)',
                        borderRadius: 8, padding: '8px 12px', fontSize: 13, color: '#6B7280',
                        fontStyle: 'italic', marginBottom: 14,
                      }}>🗣️ {interim}</div>
                    )}

                    <div style={{ display: 'flex', gap: 10 }}>
                      {!listening ? (
                        <button onClick={start} className="btn btn-primary" style={{ flex: 1, padding: '11px' }}>
                          🎤 {transcript ? 'Continue Recording' : 'Start Recording'}
                        </button>
                      ) : (
                        <button onClick={stop} style={{
                          flex: 1, padding: '11px', borderRadius: 10, border: 'none',
                          background: '#EF4444', color: 'white', fontWeight: 700,
                          fontSize: 14, cursor: 'pointer', fontFamily: 'inherit',
                          animation: 'pulse-red 1.5s ease-in-out infinite',
                        }}>⏹ Stop Recording</button>
                      )}
                      {transcript && !listening && (
                        <button onClick={clear} className="btn btn-outline" style={{ padding: '11px 16px' }}>🗑 Clear</button>
                      )}
                    </div>
                  </div>

                  {/* Editable transcript */}
                  <div>
                    <label className="form-label" style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span>📝 Transcribed Text <span style={{ color: '#9CA3AF', fontWeight: 400 }}>(you can edit)</span></span>
                      <span style={{ fontSize: 12, color: '#9CA3AF', fontWeight: 400 }}>{transcript.length} chars</span>
                    </label>
                    <textarea className="form-textarea"
                      placeholder={listening ? 'Your speech appears here as you speak...' : 'Start recording to see your answer here...'}
                      value={displayVoice} onChange={e => setManual(e.target.value)}
                      style={{
                        height: 150, fontSize: 14,
                        borderColor: listening ? 'var(--purple)' : undefined,
                        boxShadow: listening ? '0 0 0 3px rgba(108,99,255,0.1)' : undefined,
                        transition: 'border-color 0.2s, box-shadow 0.2s',
                      }} />
                  </div>

                  {/* Tips */}
                  <div style={{
                    marginTop: 10, padding: '10px 14px',
                    background: 'rgba(245,158,11,0.07)', border: '1px solid rgba(245,158,11,0.2)',
                    borderRadius: 8, fontSize: 12, color: '#92400E',
                  }}>
                    💡 <strong>Tips:</strong> Speak naturally at normal pace · Use Chrome or Edge · Allow mic when prompted · You can edit transcript after recording
                  </div>

                  {speechErr && <div className="alert alert-error" style={{ marginTop: 10 }}>⚠️ {speechErr}</div>}
                </div>
              )}

              {/* Evaluate Button */}
              <button className="btn btn-primary btn-full" style={{ marginTop: 16 }}
                onClick={() => onEvaluate(index, question, currentAns)}
                disabled={evaluating || !currentAns.trim() || listening}>
                {evaluating ? '🤖 Evaluating with AI...' : listening ? '⏸ Stop recording first' : '🚀 Evaluate Answer'}
              </button>
            </>
          )}

          {/* Already evaluated */}
          {evaluation && (
            <>
              <div>
                <label className="form-label">📝 Your Answer</label>
                <textarea className="form-textarea" value={evaluation.answer} readOnly
                  style={{ height: 120, fontSize: 14, opacity: 0.8, background: '#FAFAFA' }} />
              </div>
              <div style={{
                marginTop: 16, background: 'var(--purple-bg)',
                border: '1.5px solid var(--purple-border)', borderRadius: 12, padding: '18px 20px',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
                  <div style={{ fontWeight: 800, color: 'var(--purple-dark)', fontSize: 15 }}>📊 AI Evaluation</div>
                  {score !== null && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8, flex: 1 }}>
                      <ScoreBadge score={score} /><ScoreBar score={score} />
                    </div>
                  )}
                </div>
                <pre style={{ whiteSpace: 'pre-wrap', fontFamily: 'inherit', fontSize: 13, color: '#374151', lineHeight: 1.8, margin: 0 }}>
                  {evaluation.evaluation}
                </pre>
              </div>
            </>
          )}
        </>
      )}
    </div>
  );
}

// ── Performance Summary ────────────────────────────────────────────────────

function PerformanceSummary({ questions, evaluations }) {
  const scores = Object.values(evaluations).map(e => extractScore(e.evaluation)).filter(s => s !== null);
  const avg = scores.length ? (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1) : 0;
  const grade = avg >= 8 ? 'A' : avg >= 6 ? 'B' : avg >= 4 ? 'C' : 'D';
  const gradeColor = avg >= 8 ? '#10B981' : avg >= 6 ? '#6C63FF' : avg >= 4 ? '#F59E0B' : '#EF4444';
  return (
    <div className="card" style={{ marginBottom: 28, background: 'linear-gradient(135deg, #1A1A2E, #16213E)' }}>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 32, alignItems: 'center' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ fontSize: 64, fontWeight: 900, color: gradeColor, lineHeight: 1 }}>{grade}</div>
          <div style={{ fontSize: 12, color: '#64748B', marginTop: 4, fontWeight: 600 }}>GRADE</div>
        </div>
        <div style={{ flex: 1, display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 20 }}>
          {[
            { label: 'Avg Score', value: `${avg}/10`, color: '#8B5CF6' },
            { label: 'Evaluated', value: `${Object.keys(evaluations).length}/${questions.length}`, color: '#10B981' },
            { label: 'Top Score', value: scores.length ? `${Math.max(...scores)}/10` : 'N/A', color: '#F59E0B' },
          ].map(({ label, value, color }) => (
            <div key={label} style={{ textAlign: 'center' }}>
              <div style={{ fontSize: 28, fontWeight: 800, color }}>{value}</div>
              <div style={{ fontSize: 12, color: '#64748B', marginTop: 2, fontWeight: 500 }}>{label}</div>
            </div>
          ))}
        </div>
        <div style={{ fontSize: 11, color: '#64748B', lineHeight: 2 }}>
          <div>A = Excellent (8–10)</div><div>B = Good (6–7)</div>
          <div>C = Average (4–5)</div><div>D = Needs Work (0–3)</div>
        </div>
      </div>
    </div>
  );
}

// ── Main Page ──────────────────────────────────────────────────────────────

export default function MockInterviewPage() {
  const navigate = useNavigate();
  const { analysisResult, roadmap, mockQuestions, setMockQuestions, evaluations, setEvaluations } = useAppState();
  const [loading, setLoading]             = useState(false);
  const [evaluatingIdx, setEvaluatingIdx] = useState(null);
  const [error, setError]                 = useState('');
  const [candidateName, setCandidateName] = useState('');
  const [jobRole, setJobRole]             = useState('');
  const [downloadLoading, setDlLoading]   = useState(false);
  const [showInfo, setShowInfo]           = useState(false);

  // ── NO useEffect auto-load — user must click the button ──

  async function fetchQuestions() {
    setLoading(true); setError('');
    try {
      const qs = await generateQuestions(analysisResult.matched_skills, analysisResult.missing_skills);
      setMockQuestions(qs);
      setEvaluations({});
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to generate questions.');
    } finally { setLoading(false); }
  }

  async function handleEvaluate(idx, question, answer) {
    setEvaluatingIdx(idx); setError('');
    try {
      const ev = await evaluateAnswer(question, answer);
      setEvaluations(prev => ({ ...prev, [idx]: { question, answer, evaluation: ev } }));
    } catch (err) {
      setError(err.response?.data?.detail || 'Evaluation failed.');
    } finally { setEvaluatingIdx(null); }
  }

  async function handleDownload() {
    setDlLoading(true);
    try {
      const blob = await generateReport({
        candidate_name: candidateName, job_role: jobRole,
        compatibility_score: analysisResult.compatibility_score,
        matched_skills: analysisResult.matched_skills,
        missing_skills: analysisResult.missing_skills,
        questions: mockQuestions,
        evaluations: Object.fromEntries(Object.entries(evaluations).map(([k, v]) => [k, v])),
        roadmap: roadmap || [],
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = `SkillBridge_Report_${Date.now()}.pdf`;
      a.click(); URL.revokeObjectURL(url);
    } catch { setError('Failed to generate PDF report.'); }
    finally { setDlLoading(false); }
  }

  if (!analysisResult) {
    return (
      <div className="page-container">
        <div className="alert alert-warning">
          ⚠️ Please complete <strong>Resume Analysis</strong> first.
          <button className="btn btn-outline btn-sm" style={{ marginLeft: 12 }} onClick={() => navigate('/analysis')}>
            Go to Analysis →
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      {/* Header */}
      <div style={{ marginBottom: 28 }}>
        <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--purple)', letterSpacing: 1.5, textTransform: 'uppercase', marginBottom: 8 }}>Step 4 of 4</div>
        <h1 style={{ fontSize: 32, fontWeight: 900, color: 'var(--dark)', letterSpacing: '-0.5px', marginBottom: 8 }}>🎤 AI Mock Interview</h1>
        <p style={{ color: 'var(--gray)', fontSize: 15 }}>Answer 5 AI-generated questions by typing or speaking naturally. Get instant AI feedback.</p>
      </div>

      {/* Browser tip */}
      <div style={{
        marginBottom: 20, padding: '11px 16px',
        background: 'rgba(16,185,129,0.07)', border: '1px solid rgba(16,185,129,0.2)',
        borderRadius: 10, fontSize: 13, color: '#065F46',
      }}>
        🌐 <strong>Voice Recognition works best in Google Chrome or Microsoft Edge.</strong> Allow microphone access when prompted.
      </div>

      {/* Stats Bar */}
      <div style={{
        display: 'flex', gap: 16, marginBottom: 24, flexWrap: 'wrap',
        padding: '16px 20px', background: 'white',
        borderRadius: 12, border: '1px solid var(--purple-border)', boxShadow: 'var(--shadow)',
      }}>
        <div>
          <div style={{ fontSize: 12, color: 'var(--gray)', fontWeight: 600 }}>Compatibility</div>
          <div style={{ fontSize: 20, fontWeight: 800, color: 'var(--purple)' }}>{analysisResult.compatibility_score}%</div>
        </div>
        <div style={{ width: 1, background: '#E5E7EB' }} />
        <div>
          <div style={{ fontSize: 12, color: 'var(--gray)', fontWeight: 600 }}>Questions</div>
          <div style={{ fontSize: 20, fontWeight: 800, color: 'var(--dark)' }}>{mockQuestions?.length || 5}</div>
        </div>
        <div style={{ width: 1, background: '#E5E7EB' }} />
        <div>
          <div style={{ fontSize: 12, color: 'var(--gray)', fontWeight: 600 }}>Answered</div>
          <div style={{ fontSize: 20, fontWeight: 800, color: '#10B981' }}>
            {Object.keys(evaluations).length}/{mockQuestions?.length || 5}
          </div>
        </div>
        {mockQuestions && (
          <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center' }}>
            <button className="btn btn-outline btn-sm"
              onClick={() => { setMockQuestions(null); setEvaluations({}); }}
              disabled={loading}>
              🔄 New Questions
            </button>
          </div>
        )}
      </div>

      {error && <div className="alert alert-error" style={{ marginBottom: 20 }}>⚠️ {error}</div>}

      {/* Empty state — before generating */}
      {!mockQuestions && !loading && (
        <div style={{
          textAlign: 'center', padding: '60px 40px',
          background: 'white', borderRadius: 16,
          border: '2px dashed var(--purple-border)',
          marginBottom: 24,
        }}>
          <div style={{ fontSize: 52, marginBottom: 16 }}>🎤</div>
          <div style={{ fontSize: 18, fontWeight: 800, color: 'var(--dark)', marginBottom: 8 }}>
            Ready for your mock interview?
          </div>
          <div style={{ color: 'var(--gray)', fontSize: 14, marginBottom: 24 }}>
            Click below to generate 5 AI-powered interview questions based on your skill profile.
            You can answer by typing or speaking naturally.
          </div>
          <button className="btn btn-primary" style={{ fontSize: 16, padding: '14px 36px' }} onClick={fetchQuestions}>
            🎤 Start Mock Interview
          </button>
        </div>
      )}

      {loading && (
        <div className="spinner-wrap">
          <div className="spinner" />
          <div style={{ color: 'var(--gray)', fontSize: 14 }}>Generating your personalized interview questions...</div>
        </div>
      )}

      {/* Performance Summary */}
      {mockQuestions && Object.keys(evaluations).length > 0 && (
        <PerformanceSummary questions={mockQuestions} evaluations={evaluations} />
      )}

      {/* Questions */}
      {mockQuestions && !loading && (
        <div style={{ marginBottom: 32 }}>
          {mockQuestions.map((q, i) => (
            <QuestionCard
              key={i} question={q} index={i + 1} total={mockQuestions.length}
              evaluation={evaluations[i + 1] || null}
              onEvaluate={handleEvaluate} evaluating={evaluatingIdx === i + 1}
            />
          ))}
        </div>
      )}

      {/* PDF Report */}
      {mockQuestions && (
        <div className="card" style={{ marginBottom: 24 }}>
          <div style={{ fontWeight: 800, fontSize: 18, color: 'var(--dark)', marginBottom: 16 }}>📥 Download PDF Report</div>
          <div style={{
            background: 'var(--purple-bg)', border: '1.5px solid var(--purple-border)',
            borderRadius: 10, padding: '12px 16px', marginBottom: 16,
            cursor: 'pointer', display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          }} onClick={() => setShowInfo(o => !o)}>
            <span style={{ fontWeight: 600, color: 'var(--purple-dark)', fontSize: 14 }}>👤 Enter your info (optional)</span>
            <span style={{ color: 'var(--purple)', fontSize: 18 }}>{showInfo ? '▲' : '▼'}</span>
          </div>
          {showInfo && (
            <div className="grid-2" style={{ marginBottom: 16 }}>
              <div>
                <label className="form-label">Your Name</label>
                <input className="form-input" placeholder="e.g. Rakasri L" value={candidateName} onChange={e => setCandidateName(e.target.value)} />
              </div>
              <div>
                <label className="form-label">Target Job Role</label>
                <input className="form-input" placeholder="e.g. Backend Developer" value={jobRole} onChange={e => setJobRole(e.target.value)} />
              </div>
            </div>
          )}
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap' }}>
            <button className="btn btn-primary" onClick={handleDownload} disabled={downloadLoading} style={{ fontSize: 15, padding: '12px 24px' }}>
              {downloadLoading ? '⏳ Generating...' : '📥 Download PDF Report'}
            </button>
            <div style={{ fontSize: 13, color: 'var(--gray)' }}>
              Includes score, skills, evaluations{roadmap ? ' & roadmap' : ''}.
            </div>
          </div>
          {Object.keys(evaluations).length < (mockQuestions?.length || 5) && (
            <div className="alert alert-warning" style={{ marginTop: 12 }}>
              ⚠️ {(mockQuestions?.length || 5) - Object.keys(evaluations).length} question(s) not yet evaluated.
            </div>
          )}
        </div>
      )}
    </div>
  );
}