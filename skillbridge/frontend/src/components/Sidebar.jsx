import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { useAppState } from '../hooks/useAppState';

const navItems = [
  { path: '/',          icon: '🏠', label: 'Home' },
  { path: '/analysis',  icon: '📊', label: 'Resume Analysis' },
  { path: '/roadmap',   icon: '📅', label: 'Learning Roadmap' },
  { path: '/interview', icon: '🎤', label: 'Mock Interview' },
];

export default function Sidebar() {
  const { analysisResult } = useAppState();
  const location = useLocation();

  return (
    <aside style={{
      position: 'fixed',
      top: 0, left: 0,
      width: 'var(--sidebar-w)',
      height: '100vh',
      background: 'white',
      borderRight: '1px solid var(--purple-border)',
      display: 'flex',
      flexDirection: 'column',
      zIndex: 100,
      boxShadow: '2px 0 16px rgba(108,99,255,0.06)',
    }}>
      {/* Logo */}
      <div style={{ padding: '28px 20px 20px', textAlign: 'center', borderBottom: '1px solid var(--purple-border)' }}>
        <div style={{ fontSize: 32, marginBottom: 6 }}>🎯</div>
        <div style={{ fontSize: 17, fontWeight: 800, color: 'var(--dark)', letterSpacing: '-0.5px' }}>
          SkillBridge Pro AI
        </div>
        <div style={{ fontSize: 11, color: 'var(--gray)', marginTop: 3, fontWeight: 500 }}>
          Career Acceleration Platform
        </div>
      </div>

      {/* Nav */}
      <nav style={{ flex: 1, padding: '16px 12px', overflowY: 'auto' }}>
        {navItems.map(({ path, icon, label }) => {
          const locked = (path === '/roadmap' || path === '/interview') && !analysisResult;
          return (
            <NavLink
              key={path}
              to={locked ? '#' : path}
              onClick={e => locked && e.preventDefault()}
              style={({ isActive }) => ({
                display: 'flex',
                alignItems: 'center',
                gap: 12,
                padding: '11px 14px',
                borderRadius: 10,
                marginBottom: 4,
                textDecoration: 'none',
                fontSize: 14,
                fontWeight: isActive ? 700 : 500,
                color: isActive ? 'var(--purple)' : locked ? '#C4B5FD' : 'var(--dark)',
                background: isActive ? 'var(--purple-bg)' : 'transparent',
                border: isActive ? '1.5px solid var(--purple-border)' : '1.5px solid transparent',
                cursor: locked ? 'not-allowed' : 'pointer',
                transition: 'all 0.15s',
              })}
            >
              <span style={{ fontSize: 18 }}>{icon}</span>
              <span>{label}</span>
              {locked && (
                <span style={{ marginLeft: 'auto', fontSize: 11, color: '#C4B5FD' }}>🔒</span>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* Status */}
      {analysisResult && (
        <div style={{
          margin: '0 12px 12px',
          padding: '12px 14px',
          background: 'rgba(16,185,129,0.08)',
          border: '1px solid rgba(16,185,129,0.25)',
          borderRadius: 10,
        }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: '#065F46', marginBottom: 4 }}>✅ Analysis Ready</div>
          <div style={{ fontSize: 22, fontWeight: 800, color: '#059669' }}>
            {analysisResult.compatibility_score}%
          </div>
          <div style={{ fontSize: 11, color: '#6B7280' }}>Compatibility Score</div>
        </div>
      )}

      {/* Footer */}
      <div style={{ padding: '12px 20px', borderTop: '1px solid var(--purple-border)', fontSize: 11, color: 'var(--gray)', textAlign: 'center' }}>
        Powered by Gemini 2.5 Flash
      </div>
    </aside>
  );
}
