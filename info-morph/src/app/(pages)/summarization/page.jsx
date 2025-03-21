"use client";

import React, { useContext, useEffect } from 'react';
import { SummaryContext } from '../summaryContext/SummaryContext';
import { useRouter } from 'next/navigation';
import { FaRegLightbulb } from 'react-icons/fa';
import axios from 'axios';
import ProtectedRoute from '../../../components/Auth/ProtectedRoute';

const SummarizationPage = () => {
  const { summary, query, setSummary, setQuery } = useContext(SummaryContext);
  const router = useRouter();

  useEffect(() => {
    console.log("Summarization Page: summary =", summary);
    console.log("Summarization Page: query =", query);

    if (!summary) {
      router.push('/topic-selection');
    }
  }, [summary, router]);

  const handleReportFeedback = async () => {
    const userFeedback = prompt("Please enter your feedback:");

    if (!userFeedback) {
      alert("Feedback cannot be empty.");
      return;
    }

    try {
      const response = await axios.post("http://localhost:8000/feedback", {
        query,
        feedback: userFeedback,
      });
      alert(response.data.message);
    } catch (error) {
      console.error("Error submitting feedback:", error);
      alert("Failed to submit feedback.");
    }
  };

  const handleNewSearch = () => {
    setSummary('');
    setQuery('');
    router.push('/topic-selection');
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center p-6">
      <div className="max-w-4xl w-full bg-white shadow-md rounded-lg p-8 mt-10">
        <div className="flex items-center justify-center mb-4">
          <FaRegLightbulb className="text-yellow-500 text-4xl mr-2" />
          <h1 className="text-3xl font-bold">Professional Summary</h1>
        </div>
        <div className="h-96 overflow-y-scroll">
          <p className="text-lg text-gray-700 whitespace-pre-line leading-relaxed">
            {summary}
          </p>
        </div>
        <div className="mt-6 flex justify-center gap-4">
          <button
            onClick={handleNewSearch}
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition"
          >
            New Search
          </button>
          <button
            onClick={handleReportFeedback}
            className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 transition"
          >
            Report Feedback
          </button>
        </div>
      </div>
    </div>
  );
};

const WrappedSummarizationPage = () => (
  <ProtectedRoute>
    <SummarizationPage />
  </ProtectedRoute>
);

export default WrappedSummarizationPage;
