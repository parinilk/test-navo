


import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Question1 from "../Questions/Question1";
import Question2 from "../Questions/Question2";
import Question3 from "../Questions/Question3";
import Question4 from "../Questions/Question4";
import Question5 from "../Questions/Question5";

interface ResearchResult {
  query: string;
  answer: string;
  rationale: string;
  sources_used: string[];  // Fixed: match backend field name
  disclaimer?: string;
  session_id: string;
  timestamp: string;
  retrieved_products?: any[];
  web_search_results?: any[];  // Added: web search results
  confidence_score?: number;   // Added: confidence score
  data_gaps?: string[];        // Added: data gaps
  analysis_complexity?: string; // Added: analysis complexity
  regulatory_analysis?: any;    // Added: regulatory analysis
}

const Reportcard = () => {
  const [activeTab, setActiveTab] = useState(1);
  const [pinnedResults, setPinnedResults] = useState<string[]>([]);
  const [editIndex, setEditIndex] = useState<number | null>(null);
  const [editText, setEditText] = useState("");
  const [editedIndices, setEditedIndices] = useState<number[]>([]);
  const [researchResult, setResearchResult] = useState<ResearchResult | null>(null);
  const navigate = useNavigate();

  // Load research result from localStorage when component mounts
  useEffect(() => {
    const savedResult = localStorage.getItem('researchResult');
    if (savedResult) {
      try {
        const result = JSON.parse(savedResult);
        setResearchResult(result);
      } catch (e) {
        console.error('Failed to parse research result:', e);
      }
    }
  }, []);

  const handlePin = (text: string) => {
    setPinnedResults((prev) => [...prev, `Q-${activeTab}: ${text}`]);
  };

  const handleUnpin = (index: number) => {
    setPinnedResults((prev) => prev.filter((_, i) => i !== index));
    setEditedIndices((prev) => prev.filter((i) => i !== index));
  };

  const handleEdit = (index: number) => {
    setEditIndex(index);
    setEditText(pinnedResults[index]);
  };

  const handleSaveEdit = () => {
    if (editIndex === null) return;

    setPinnedResults((prev) =>
      prev.map((item, i) => (i === editIndex ? editText : item))
    );

    setEditedIndices((prev) =>
      prev.includes(editIndex) ? prev : [...prev, editIndex]
    );

    setEditIndex(null);
    setEditText("");
  };

  const renderQuestion = () => {
    switch (activeTab) {
      case 1:
        return <Question1 onPin={handlePin} researchResult={researchResult} />;
      case 2:
        return <Question2 onPin={handlePin} researchResult={researchResult} />;
      case 3:
        return <Question3 onPin={handlePin} researchResult={researchResult} />;
      case 4:
        return <Question4 onPin={handlePin} researchResult={researchResult} />;
      case 5:
        return <Question5 onPin={handlePin} researchResult={researchResult} />;
      default:
        return null;
    }
  };

  return (
    <div className="flex w-full h-[500px]">
      {/* Left Panel */}
      <div className="w-1/2 p-4 border-r">
        <div className="flex gap-2 mb-4">
          {[1, 2, 3, 4, 5].map((num) => (
            <button
              key={num}
              onClick={() => setActiveTab(num)}
              className={`px-3 py-1 border rounded ${
                activeTab === num ? "bg-blue-500 text-white" : "bg-gray-100"
              }`}
            >
              Question {num}
            </button>
          ))}
        </div>
        {renderQuestion()}
      </div>

      {/* Right Panel */}
      <div className="w-1/2 h-[540px] p-4 overflow-y-auto scrollbar-hidden bg-white relative">
        <h2 className="font-semibold mb-2 text-center">Pinned Results</h2>
        {pinnedResults.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full gap-2">
            {/* Your existing SVG and empty message here */}
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="18"
              height="18"
              viewBox="0 0 18 18"
              fill="none"
            >
              <g clipPath="url(#clip0_304_3444)">
                <path
                  d="M9 12.75V16.5M11.25 7.005V5.25C11.25 5.05109 11.329 4.86032 11.4697 4.71967C11.6103 4.57902 11.8011 4.5 12 4.5C12.3978 4.5 12.7794 4.34196 13.0607 4.06066C13.342 3.77936 13.5 3.39782 13.5 3C13.5 2.60218 13.342 2.22064 13.0607 1.93934C12.7794 1.65804 12.3978 1.5 12 1.5H5.9175M1.5 1.5L16.5 16.5M6.75 6.75V8.07C6.74985 8.34906 6.67186 8.62255 6.52479 8.85972C6.37772 9.09688 6.16741 9.28832 5.9175 9.4125L4.5825 10.0875C4.33259 10.2117 4.12228 10.4031 3.97521 10.6403C3.82814 10.8774 3.75015 11.1509 3.75 11.43V12C3.75 12.1989 3.82902 12.3897 3.96967 12.5303C4.11032 12.671 4.30109 12.75 4.5 12.75H12.75"
                  stroke="black"
                  strokeWidth="1.125"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </g>
              <defs>
                <clipPath id="clip0_304_3444">
                  <rect width="18" height="18" fill="white" />
                </clipPath>
              </defs>
            </svg>
            <p className="text-gray-500 text-center">No pinned content yet.</p>
          </div>
        ) : (
          <ul className="space-y-4">
            {pinnedResults.map((item, index) => (
              <li
                key={index}
                className={`border border-gray-200 rounded p-2 shadow-sm transition-colors duration-300 ${
                  editedIndices.includes(index) ? "bg-green-100" : "bg-white"
                }`}
              >
                {editIndex === index ? (
                  <div className="flex flex-col gap-2">
                    <textarea
                      className="w-full border border-gray-300 p-2 text-sm"
                      value={editText}
                      onChange={(e) => setEditText(e.target.value)}
                    />
                    <div className="flex gap-2 justify-end">
                      <button
                        className="text-sm text-white bg-green-800 px-3 py-1 rounded"
                        onClick={handleSaveEdit}
                      >
                        Save
                      </button>
                      <button
                        className="text-sm text-gray-700 border px-3 py-1 rounded"
                        onClick={() => setEditIndex(null)}
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="flex justify-between items-start">
                    <p className="text-sm text-gray-800 w-full pr-4">{item}</p>
                    <div className="flex gap-2">
                      {/* Edit button */}
                      <button onClick={() => handleEdit(index)} title="Edit">
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          width="18"
                          height="18"
                          viewBox="0 0 18 18"
                          fill="none"
                        >
                          <path
                            d="M9 2.24999H3.75C3.35218 2.24999 2.97064 2.40802 2.68934 2.68933C2.40804 2.97063 2.25 3.35216 2.25 3.74999V14.25C2.25 14.6478 2.40804 15.0293 2.68934 15.3106C2.97064 15.592 3.35218 15.75 3.75 15.75H14.25C14.6478 15.75 15.0294 15.592 15.3107 15.3106C15.592 15.0293 15.75 14.6478 15.75 14.25V8.99999M13.7812 1.96874C14.0796 1.67037 14.4843 1.50275 14.9062 1.50275C15.3282 1.50275 15.7329 1.67037 16.0312 1.96874C16.3296 2.26711 16.4972 2.67178 16.4972 3.09374C16.4972 3.51569 16.3296 3.92037 16.0312 4.21874L9.2715 10.9792C9.09341 11.1572 8.8734 11.2874 8.63175 11.358L6.477 11.988C6.41246 12.0068 6.34405 12.0079 6.27893 11.9913C6.21381 11.9746 6.15437 11.9407 6.10683 11.8932C6.0593 11.8456 6.02542 11.7862 6.00873 11.7211C5.99205 11.6559 5.99318 11.5875 6.012 11.523L6.642 9.36824C6.71289 9.12677 6.8434 8.90703 7.0215 8.72924L13.7812 1.96874Z"
                            stroke="black"
                            strokeWidth="1.35"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                          />
                        </svg>
                      </button>

                      {/* Unpin button */}
                      <button onClick={() => handleUnpin(index)} title="Unpin">
                        <svg
                          xmlns="http://www.w3.org/2000/svg"
                          width="18"
                          height="18"
                          viewBox="0 0 18 18"
                          fill="none"
                        >
                          <g clipPath="url(#clip0_304_3444)">
                            <path
                              d="M9 12.75V16.5M11.25 7.005V5.25C11.25 5.05109 11.329 4.86032 11.4697 4.71967C11.6103 4.57902 11.8011 4.5 12 4.5C12.3978 4.5 12.7794 4.34196 13.0607 4.06066C13.342 3.77936 13.5 3.39782 13.5 3C13.5 2.60218 13.342 2.22064 13.0607 1.93934C12.7794 1.65804 12.3978 1.5 12 1.5H5.9175M1.5 1.5L16.5 16.5M6.75 6.75V8.07C6.74985 8.34906 6.67186 8.62255 6.52479 8.85972C6.37772 9.09688 6.16741 9.28832 5.9175 9.4125L4.5825 10.0875C4.33259 10.2117 4.12228 10.4031 3.97521 10.6403C3.82814 10.8774 3.75015 11.1509 3.75 11.43V12C3.75 12.1989 3.82902 12.3897 3.96967 12.5303C4.11032 12.671 4.30109 12.75 4.5 12.75H12.75"
                              stroke="black"
                              strokeWidth="1.125"
                              strokeLinecap="round"
                              strokeLinejoin="round"
                            />
                          </g>
                          <defs>
                            <clipPath id="clip0_304_3444">
                              <rect width="18" height="18" fill="white" />
                            </clipPath>
                          </defs>
                        </svg>
                      </button>
                    </div>
                  </div>
                )}
              </li>
            ))}
          </ul>
        )}

        {/* Bottom-right Action Button */}
        <button
          className="absolute bottom-4 right-4 px-4 py-2 bg-blue-600 text-white rounded shadow hover:bg-blue-700"
          onClick={() => {
            // Store pinned results for report generation
            localStorage.setItem('pinnedResults', JSON.stringify(pinnedResults));
            localStorage.setItem('researchContext', JSON.stringify({
              query: researchResult?.query || '',
              timestamp: researchResult?.timestamp || new Date().toISOString(),
              session_id: researchResult?.session_id || ''
            }));
            // Navigate to main report page
            navigate('/report');
          }}
        >
          Generate Report
        </button>
      </div>
    </div>
  );
};

export default Reportcard;
