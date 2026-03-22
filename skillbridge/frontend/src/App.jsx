import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AppProvider } from './hooks/useAppState';
import Sidebar from './components/Sidebar';
import HomePage from './pages/HomePage';
import ResumeAnalysisPage from './pages/ResumeAnalysisPage';
import RoadmapPage from './pages/RoadmapPage';
import MockInterviewPage from './pages/MockInterviewPage';

export default function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <div className="app-layout">
          <Sidebar />
          <main className="main-content">
            <Routes>
              <Route path="/"          element={<HomePage />} />
              <Route path="/analysis"  element={<ResumeAnalysisPage />} />
              <Route path="/roadmap"   element={<RoadmapPage />} />
              <Route path="/interview" element={<MockInterviewPage />} />
            </Routes>
          </main>
        </div>
      </BrowserRouter>
    </AppProvider>
  );
}
