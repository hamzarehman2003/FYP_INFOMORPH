"use client";

import { SummaryProvider } from '../../app/(pages)/summaryContext/SummaryContext';

const PagesLayout = ({ children }) => {
  return (
    <SummaryProvider>
      <div className="bg-[#dcebfe] min-h-screen flex justify-center">
        {children}
      </div>
    </SummaryProvider>
  );
};

export default PagesLayout;
