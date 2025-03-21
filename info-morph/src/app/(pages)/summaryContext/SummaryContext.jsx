"use client";

import React, { createContext, useState } from 'react';

export const SummaryContext = createContext({
  summary: '',
  setSummary: () => {},
  query: '',
  setQuery: () => {},
  audioFile: '',
  setAudioFile: () => {}
});

export const SummaryProvider = ({ children }) => {
  const [summary, setSummary] = useState('');
  const [query, setQuery] = useState('');
  const [audioFile, setAudioFile] = useState('');

  return (
    <SummaryContext.Provider value={{ summary, setSummary, query, setQuery, audioFile, setAudioFile }}>
      {children}
    </SummaryContext.Provider>
  );
};
