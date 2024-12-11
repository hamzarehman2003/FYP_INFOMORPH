// frontend/components/Providers.jsx

"use client";

import React from 'react';
import { SummaryProvider } from '../../app/(pages)/summaryContext/SummaryContext';

const Providers = ({ children }) => {
  return (
    <SummaryProvider>
      {children}
    </SummaryProvider>
  );
};

export default Providers;
