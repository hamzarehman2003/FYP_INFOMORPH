"use client";

import React, { createContext, useState } from 'react';

export const SummaryContext = createContext({
  summary: '',
  setSummary: () => {},
  query: '',
  setQuery: () => {},
});

export const SummaryProvider = ({ children }) => {
  const [summary, setSummary] = useState('');
  const [query, setQuery] = useState('');

  return (
    <SummaryContext.Provider value={{ summary, setSummary, query, setQuery }}>
      {children}
    </SummaryContext.Provider>
  );
};
