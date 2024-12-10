// frontend/src/components/TopicSelection.jsx
"use client";

import React, { useState } from "react";
import PageHeading from "@/components/PageHeading"; // Ensure this component exists
import styles from "../style.module.css";
import axios from "axios";

const TopicSelectionPage = () => {
  const [query, setQuery] = useState("");
  const [inputLanguage, setInputLanguage] = useState("en");
  const [outputLanguage, setOutputLanguage] = useState("en");
  const [urls, setUrls] = useState([]);
  const [selectedUrl, setSelectedUrl] = useState("");
  const [summary, setSummary] = useState("");
  const [finalSummary, setFinalSummary] = useState(""); // New state for final summary
  const [errors, setErrors] = useState([]);
  const [loading, setLoading] = useState(false);
  const [summarizing, setSummarizing] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) {
      alert("Please enter a topic to search.");
      return;
    }
    setLoading(true);
    setErrors([]);
    setUrls([]);
    setSummary("");
    setFinalSummary(""); // Reset final summary on new search
    try {
      const response = await axios.post("http://localhost:8000/scrape", {
        query,
        num_urls: 5,
        input_language: inputLanguage,
        output_language: outputLanguage,
      });
      
      // Extract articles and final_summary from the response
      const { articles, final_summary } = response.data;
      
      // Set individual URLs for selection
      setUrls(
        articles.map((article, index) => ({
          id: index,
          title: article.title,
          url: article.url,
        }))
      );
      
      // Set the final summary
      setFinalSummary(final_summary);
    } catch (error) {
      console.error("Error fetching URLs:", error);
      setErrors([
        error.response?.data?.detail ||
          "An error occurred while fetching URLs.",
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleBeginSummarization = async () => {
    if (!selectedUrl) {
      alert("Please select a URL to summarize.");
      return;
    }
    setSummarizing(true);
    setErrors([]);
    setSummary("");
    try {
      const response = await axios.post("http://localhost:8000/summarize", {
        url: selectedUrl,
      });
      if (response.data.summary) {
        setSummary(response.data.summary);
      } else {
        setErrors([
          response.data.error || "Failed to summarize the article.",
        ]);
      }
    } catch (error) {
      console.error("Error summarizing article:", error);
      setErrors([
        error.response?.data?.detail ||
          "An error occurred during summarization.",
      ]);
    } finally {
      setSummarizing(false);
    }
  };

  const handleReportFeedback = () => {
    // Implement feedback reporting logic
    alert("Feedback submitted. Thank you!");
  };

  return (
    <div className="w-full flex flex-col items-center">
      <div className="max-w-[1440px] w-full px-5 pb-24">
        <PageHeading
          text={"Scrape and Summarize Articles"}
          className={"mt-24"}
        />

        <div className="mt-10 w-full flex flex-col items-center font-poppins">
          <div className="text-[32px] leading-[48px]">Topic Selection</div>
          <div className="text-center text-xl">
            Enter a topic you want the news from and we will return the most
            relevant URLs related to it
          </div>
        </div>

        <div className="mt-24 flex flex-col urlLink:flex-row flex-wrap items-center gap-10">
          <div className="flex flex-wrap items-center justify-center urlLink:justify-end w-full urlLink:w-auto urlLink:flex-1">
            <label className="w-[120px] font-poppins" htmlFor="topic">
              Topic
            </label>
            <input
              type="text"
              id="topic"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="max-w-[772px] w-full rounded-2xl h-[52px] pl-6"
              placeholder="Enter your topic here"
            />
          </div>
          <div className="urlLink:w-[350px] flex flex-wrap gap-5">
            <select
              className={`${styles.selectClass} py-2 px-2 rounded-lg text-[#5533FF] font-medium border border-[rgba(0,0,0,0.1)]`}
              value={inputLanguage}
              onChange={(e) => setInputLanguage(e.target.value)}
            >
              <option value="en">English</option>
              <option value="ur">Urdu</option>
              {/* Add more languages as needed */}
            </select>
            <select
              className={`${styles.selectClass} py-2 px-2 rounded-lg text-[#5533FF] font-medium border border-[rgba(0,0,0,0.1)]`}
              value={outputLanguage}
              onChange={(e) => setOutputLanguage(e.target.value)}
            >
              <option value="en">English</option>
              <option value="ur">Urdu</option>
              {/* Add more languages as needed */}
            </select>
          </div>
        </div>

        <div className="mt-10 flex justify-center">
          <button
            onClick={handleSearch}
            className="bg-[#5533FF] text-white px-6 py-3 rounded-full"
            disabled={loading}
          >
            {loading ? "Searching..." : "Search URLs"}
          </button>
        </div>

        {errors.length > 0 && (
          <div className="mt-5 text-red-500">
            {errors.map((error, index) => (
              <div key={index}>{error}</div>
            ))}
          </div>
        )}

        {urls.length > 0 && (
          <div className="mt-24 flex flex-col urlLink:flex-row flex-wrap items-center gap-10">
            <div className="flex flex-wrap justify-center urlLink:justify-end w-full urlLink:w-auto urlLink:flex-1">
              <label className="w-[195px] font-poppins" htmlFor="url">
                List of Relevant URLs
              </label>
              <div className="w-full max-w-[722px] flex justify-between items-center">
                <div className="h-full">
                  <select
                    id="url"
                    className={`px-4 py-2 text-[#5533FF] rounded-lg border border-[rgba(0,0,0,0.1)]`}
                    value={selectedUrl}
                    onChange={(e) => setSelectedUrl(e.target.value)}
                  >
                    <option value="">Pick a URL</option>
                    {urls.map((article) => (
                      <option key={article.id} value={article.url}>
                        {article.title}
                      </option>
                    ))}
                  </select>
                </div>
                <button
                  onClick={handleBeginSummarization}
                  className="active:scale-90 duration-300 ease-in-out transition-all text-lg font-poppins font-medium bg-[#DEDCFE] py-4 px-8 rounded-full"
                  disabled={summarizing}
                >
                  {summarizing ? "Summarizing..." : "Begin Summarization"}
                </button>
              </div>
            </div>
            <div className="urlLink:w-[350px] flex-wrap flex urlLink:flex-col items-end justify-end gap-[12px]" />
          </div>
        )}

        {/* Display Final Summary */}
        {finalSummary && (
          <div className="mt-24 w-full flex flex-col urlLink:flex-row flex-wrap items-center gap-10">
            <div className="flex flex-wrap justify-center urlLink:justify-end w-full urlLink:w-auto urlLink:flex-1">
              <label className="w-[120px] font-poppins" htmlFor="finalSummary">
                Final Summary
              </label>
              <textarea
                id="finalSummary"
                value={finalSummary}
                readOnly
                className="max-w-[772px] w-full rounded-2xl h-[242px] pl-4 py-2.5"
              />
            </div>
            <div className="urlLink:w-[350px] urlLink:h-[242px] flex-wrap flex urlLink:flex-col items-end justify-end gap-[12px]">
              <button
                onClick={handleReportFeedback}
                className="active:scale-90 duration-300 ease-in-out transition-all font-poppins text-lg py-4 px-8 rounded-full bg-[#DCFCFE]"
              >
                Report Feedback
              </button>
            </div>
          </div>
        )}

        {/* Display Individual Article Summary */}
        {summary && (
          <div className="mt-24 w-full flex flex-col urlLink:flex-row flex-wrap items-center gap-10">
            <div className="flex flex-wrap justify-center urlLink:justify-end w-full urlLink:w-auto urlLink:flex-1">
              <label className="w-[120px] font-poppins" htmlFor="summary">
                Article Summary
              </label>
              <textarea
                id="summary"
                value={summary}
                readOnly
                className="max-w-[772px] w-full rounded-2xl h-[242px] pl-4 py-2.5"
              />
            </div>
            <div className="urlLink:w-[350px] urlLink:h-[242px] flex-wrap flex urlLink:flex-col items-end justify-end gap-[12px]">
              <button
                onClick={handleReportFeedback}
                className="active:scale-90 duration-300 ease-in-out transition-all font-poppins text-lg py-4 px-8 rounded-full bg-[#DCFCFE]"
              >
                Report Feedback
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TopicSelectionPage;
