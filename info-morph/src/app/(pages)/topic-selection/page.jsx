"use client";

import React, { useState, useContext } from "react";
import PageHeading from '../../../components/Auth/PageHeading'; // Adjust path as necessary
import styles from '../style.module.css';
import axios from "axios";
import { useRouter } from 'next/navigation';
import { SummaryContext } from '../summaryContext/SummaryContext';
import ProtectedRoute from '../../../components/Auth/ProtectedRoute';
import { toast } from "react-toastify";

const TopicSelectionPage = () => {
  const [queryInput, setQueryInput] = useState("");
  const [inputLanguage, setInputLanguage] = useState("en");
  const [outputLanguage, setOutputLanguage] = useState("en");
  const [urls, setUrls] = useState([]);
  const [errors, setErrors] = useState([]);
  const [loading, setLoading] = useState(false);

  const { setSummary, setQuery } = useContext(SummaryContext);
  const router = useRouter();

  const handleSearch = async () => {
    if (!queryInput.trim()) {
      toast.error("Please enter a topic to search.");
      return;
    }
    console.log("Output Language:", outputLanguage); // Verify output language value
    setLoading(true);
    setErrors([]);
    setUrls([]);
    try {
      const token = localStorage.getItem('token'); // Get token from storage

      const response = await axios.post("http://localhost:8000/scrape", {
        query: queryInput,
        num_urls: 10,
        input_language: inputLanguage,
        output_language: outputLanguage,
      }, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      console.log("Scrape response:", response.data);

      const { articles, final_summary } = response.data;

      setUrls(
        articles.map((article, index) => ({
          id: index,
          title: article.title,
          url: article.url,
        }))
      );

      setSummary(final_summary || "No summary was generated. Please try another search term.");
      setQuery(queryInput);

      console.log(`Summary length: ${final_summary ? final_summary.split(' ').length : 0} words`);
      console.log("Context updated with summary and query");

      router.push('/summarization');

    } catch (error) {
      console.error("Error fetching URLs:", error);
      setErrors([
        error.response?.data?.detail ||
          "An error occurred while fetching URLs.",
      ]);
      toast.error(error.response?.data?.detail || "An error occurred while fetching URLs.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full flex flex-col items-center">
      <div className="max-w-[1440px] w-full px-5 pb-24">
        <div className="text-center text-xl">
          <PageHeading text={"Scrape and Summarize Articles"} className={"mt-24"} />
        </div>

        <div className="mt-10 w-full flex flex-col items-center font-poppins">
          <div className="text-[32px] leading-[48px]">Topic Selection</div>
          <div className="text-center text-xl">
            Enter a topic you want the news from and we will return the most relevant URLs related to it
          </div>
        </div>

        <div className="mt-24 flex flex-col md:flex-row flex-wrap items-center gap-10">
          <div className="flex flex-col md:flex-row gap-5">
            <div className="flex flex-wrap items-center">
              <label className="w-[120px] font-poppins" htmlFor="topic">Topic</label>
              <input
                type="text"
                id="topic"
                value={queryInput}
                onChange={(e) => setQueryInput(e.target.value)}
                className="max-w-[772px] w-full rounded-2xl h-[52px] pl-6"
                placeholder="Enter your topic here"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label className="font-poppins">Input Language</label>
              <select
                className={`${styles.selectClass} py-2 px-2 rounded-lg text-[#5533FF] font-medium border border-[rgba(0,0,0,0.1)]`}
                value={inputLanguage}
                onChange={(e) => setInputLanguage(e.target.value)}
              >
                <option value="en">English</option>
                <option value="ur">Urdu</option>
              </select>
            </div>
            <div className="flex flex-col gap-2">
              <label className="font-poppins">Output Language</label>
              <select
                className={`${styles.selectClass} py-2 px-2 rounded-lg text-[#5533FF] font-medium border border-[rgba(0,0,0,0.1)]`}
                value={outputLanguage}
                onChange={(e) => setOutputLanguage(e.target.value)}
              >
                <option value="en">English</option>
                <option value="ur">Urdu</option>
              </select>
            </div>
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
          <div className="mt-24 flex flex-col md:flex-row flex-wrap items-center gap-10">
            <div className="flex flex-wrap justify-center md:justify-end w-full md:w-auto md:flex-1">
              <label className="w-[195px] font-poppins" htmlFor="urls">Relevant URLs</label>
              <div className="w-full max-w-[722px] overflow-y-auto max-h-60">
                <ul className="list-disc list-inside">
                  {urls.map((article) => (
                    <li key={article.id}>
                      <a
                        href={article.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline"
                      >
                        {article.title}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const WrappedTopicSelectionPage = () => (
  <ProtectedRoute>
    <TopicSelectionPage />
  </ProtectedRoute>
);

export default WrappedTopicSelectionPage;
