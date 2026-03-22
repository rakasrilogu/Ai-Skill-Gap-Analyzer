import React, { createContext, useContext, useState } from 'react';

const AppContext = createContext(null);

export function AppProvider({ children }) {
  const [analysisResult, setAnalysisResult] = useState(null); // { compatibility_score, matched_skills, missing_skills }
  const [roadmap, setRoadmap] = useState(null);              // array of roadmap items
  const [mockQuestions, setMockQuestions] = useState(null);  // array of strings
  const [evaluations, setEvaluations] = useState({});        // { questionIndex: { question, answer, evaluation } }

  function reset() {
    setAnalysisResult(null);
    setRoadmap(null);
    setMockQuestions(null);
    setEvaluations({});
  }

  return (
    <AppContext.Provider value={{
      analysisResult, setAnalysisResult,
      roadmap, setRoadmap,
      mockQuestions, setMockQuestions,
      evaluations, setEvaluations,
      reset,
    }}>
      {children}
    </AppContext.Provider>
  );
}

export function useAppState() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error('useAppState must be inside AppProvider');
  return ctx;
}
