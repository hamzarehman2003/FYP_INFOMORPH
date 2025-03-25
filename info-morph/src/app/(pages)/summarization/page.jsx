"use client";

import React, { useContext, useEffect, useState } from "react";
import { SummaryContext } from "../summaryContext/SummaryContext";
import { useRouter } from "next/navigation";
import { FaRegLightbulb } from "react-icons/fa";
import axios from "axios";
import ProtectedRoute from "../../../components/Auth/ProtectedRoute";

const SummarizationPage = () => {
  const { summary, query, setSummary, setQuery } = useContext(SummaryContext);
  const router = useRouter();
  const [feedback, setFeedback] = useState("");

  useEffect(() => {
    console.log("Summarization Page: summary =", summary);
    console.log("Summarization Page: query =", query);
    if (!summary) {
      router.push("/topic-selection");
    }
  }, [summary, router]);

  const handleReportFeedback = async () => {
    if (!feedback) {
      alert("Feedback cannot be empty.");
      return;
    }
    try {
      const response = await axios.post("http://localhost:8000/feedback", {
        query,
        feedback,
      });
      alert(response.data.message);
      setFeedback(""); // Clear feedback after submission
    } catch (error) {
      console.error("Error submitting feedback:", error);
      alert("Failed to submit feedback.");
    }
  };

  const handleNewSearch = () => {
    setSummary("");
    setQuery("");
    router.push("/topic-selection");
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-100 flex flex-col items-center p-6">
        <div className="max-w-4xl w-full bg-white shadow-md rounded-lg p-8 mt-10">
          <div className="flex items-center justify-center mb-4">
            <FaRegLightbulb className="text-yellow-500 text-4xl mr-2" />
            <h1 className="text-3xl font-bold">Professional Summary</h1>
          </div>
          <div className="h-96 overflow-y-scroll mb-4">
            <p className="text-lg text-gray-700 whitespace-pre-line leading-relaxed">
              {summary}
            </p>
          </div>

          {/* Audio player for the generated audio */}
          <div className="mb-4">
            <audio controls src="http://localhost:8000/audio" className="w-full"></audio>
          </div>

          {/* Feedback Box */}
          <div className="mb-4">
            <h2 className="text-xl font-semibold mb-2">Provide Feedback:</h2>
            <textarea
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              placeholder="Write your feedback here..."
              className="w-full h-24 p-2 border rounded-lg border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onClick={handleReportFeedback}
              className="mt-2 bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 transition"
            >
              Submit Feedback
            </button>
          </div>

          <div className="flex justify-center gap-4">
            <button
              onClick={handleNewSearch}
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition"
            >
              New Search
            </button>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
};

export default SummarizationPage;
