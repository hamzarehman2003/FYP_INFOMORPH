// frontend/components/summaryContext/SummaryContext.jsx

"use client";

import React, { createContext, useState } from 'react';

// Create the context with default values (optional but recommended)
export const SummaryContext = createContext({
  summary: '',
  setSummary: () => {},
  query: '',
  setQuery: () => {},
});

// Create a provider component
// frontend/app/summaryContext/SummaryContext.jsx

export const SummaryProvider = ({ children }) => {
  const [summary, setSummary] = useState('');
  const [query, setQuery] = useState('');

  // Debugging
  console.log("SummaryProvider rendered with summary:", summary);
  console.log("SummaryProvider rendered with query:", query);

  return (
    <SummaryContext.Provider value={{ summary, setSummary, query, setQuery }}>
      {children}
    </SummaryContext.Provider>
  );
};

