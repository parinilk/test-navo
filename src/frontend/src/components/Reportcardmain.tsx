
import { useState, useEffect } from "react";

interface ResearchContext {
  query: string;
  timestamp: string;
  session_id: string;
}

interface ResearchResult {
  query: string;
  answer: string;
  rationale: string;
  sources: string[];
  session_id: string;
  timestamp: string;
  retrieved_products?: any[];
}

const Reportcardmain = () => {
  const [pinnedResults, setPinnedResults] = useState<string[]>([]);
  const [researchContext, setResearchContext] = useState<ResearchContext | null>(null);
  const [researchResult, setResearchResult] = useState<ResearchResult | null>(null);

  useEffect(() => {
    // Load pinned results from localStorage
    const savedPinnedResults = localStorage.getItem('pinnedResults');
    if (savedPinnedResults) {
      try {
        setPinnedResults(JSON.parse(savedPinnedResults));
      } catch (e) {
        console.error('Failed to parse pinned results:', e);
      }
    }

    // Load research context
    const savedContext = localStorage.getItem('researchContext');
    if (savedContext) {
      try {
        setResearchContext(JSON.parse(savedContext));
      } catch (e) {
        console.error('Failed to parse research context:', e);
      }
    }

    // Load original research result for additional context
    const savedResult = localStorage.getItem('researchResult');
    if (savedResult) {
      try {
        setResearchResult(JSON.parse(savedResult));
      } catch (e) {
        console.error('Failed to parse research result:', e);
      }
    }
  }, []);

  const exportReport = () => {
    // Create a comprehensive report text
    const reportContent = generateReportContent();
    
    // Create a blob and download
    const blob = new Blob([reportContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `research-report-${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  const generateReportContent = () => {
    const currentDate = new Date().toLocaleDateString();
    const title = researchContext?.query || "Research Report";
    
    return `
RESEARCH REPORT
===============

Title: ${title}
Date Created: ${currentDate}
Session ID: ${researchContext?.session_id || 'N/A'}

EXECUTIVE SUMMARY
================
${researchResult?.answer || 'No summary available'}

RESEARCH OBJECTIVE
==================
Original Query: ${researchContext?.query || 'N/A'}

Key Findings (from pinned results):
${pinnedResults.map(item => `• ${item}`).join('\n')}

DETAILED ANALYSIS
================
${researchResult?.rationale || 'No detailed analysis available'}

SOURCES
=======
${researchResult?.sources?.map(source => `• ${source}`).join('\n') || 'No sources available'}

CONCLUSION & RECOMMENDATIONS
============================
Based on the research findings and pinned insights, the following recommendations are suggested:
${pinnedResults.length > 0 ? pinnedResults.map(item => `• ${item.replace(/^Q-\d+: /, '')}`).join('\n') : 'No specific recommendations available'}

---
Report generated on ${new Date().toLocaleString()}
    `.trim();
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return new Date().toLocaleDateString();
    return new Date(dateString).toLocaleDateString();
  };

  const getReportTitle = () => {
    if (researchContext?.query) {
      // Extract a meaningful title from the query
      const words = researchContext.query.split(' ');
      if (words.length > 6) {
        return words.slice(0, 6).join(' ') + '...';
      }
      return researchContext.query;
    }
    return "Research Report";
  };

  return (
    <div className="flex-1 p-[12px] w-[1210px] h-[550px] bg-[#F3F6FA]">
      {/* Header */}
      <h1 className="text-3xl font-semibold mb-2">{getReportTitle()}</h1>
      <div className="flex items-center text-sm text-gray-600 mb-4">
        <span>Date created: {formatDate(researchContext?.timestamp)}</span>
        <span className="mx-3">|</span>
        <span>Created by: AI Research Assistant</span>
        <span className="mx-3">|</span>
        <span>Session: {researchContext?.session_id?.slice(0, 8) || 'N/A'}</span>

        <button 
          onClick={exportReport}
          className="ml-auto flex items-center gap-2 bg-[#005CCE] text-white border border-blue-500 px-3 py-2 rounded text-sm hover:bg-blue-500 hover:text-white transition-colors duration-200"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="w-4 h-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M4 16v2a2 2 0 002 2h12a2 2 0 002-2v-2M7 10l5-5m0 0l5 5m-5-5v12"
            />
          </svg>
          Export Report
        </button>
      </div>

      {/* Card content */}
      <div className="border rounded p-4 w-[1210px] h-[480px] bg-white overflow-y-auto">
        {/* Executive Summary */}
        <section className="mb-6">
          <h2 className="font-semibold text-lg mb-2">Executive Summary</h2>
          <div className="text-sm text-gray-700 leading-relaxed">
            {researchResult?.answer ? (
              <p>{researchResult.answer}</p>
            ) : (
              <p className="text-gray-500 italic">No research data available. Please complete a research query first.</p>
            )}
          </div>
        </section>

        {/* Research Objective */}
        <section className="mb-6">
          <h2 className="font-semibold text-lg mb-2">Research Objective</h2>
          <p className="text-sm font-semibold text-gray-700 mb-2">Original Query:</p>
          <div className="bg-gray-50 p-3 rounded mb-3">
            <p className="text-sm text-gray-700 italic">
              "{researchContext?.query || 'No query available'}"
            </p>
          </div>
          
          {pinnedResults.length > 0 && (
            <>
              <p className="text-sm font-semibold text-gray-700 mb-2">Key Insights (from pinned results):</p>
              <ul className="list-disc pl-6 text-sm text-gray-700">
                {pinnedResults.map((item, index) => (
                  <li key={index} className="mb-1">
                    {item.replace(/^Q-\d+: /, '')}
                  </li>
                ))}
              </ul>
            </>
          )}
        </section>

        {/* Analysis & Findings */}
        <section className="mb-6">
          <h2 className="font-semibold text-lg mb-2">Detailed Analysis & Rationale</h2>
          <div className="text-sm text-gray-700 leading-relaxed">
            {researchResult?.rationale ? (
              <p className="whitespace-pre-wrap">{researchResult.rationale}</p>
            ) : (
              <p className="text-gray-500 italic">No detailed analysis available.</p>
            )}
          </div>
        </section>

        {/* Sources */}
        {researchResult?.sources && researchResult.sources.length > 0 && (
          <section className="mb-6">
            <h2 className="font-semibold text-lg mb-2">Sources & References</h2>
            <ul className="list-disc pl-6 text-sm text-gray-700 space-y-1">
              {researchResult.sources.map((source, index) => (
                <li key={index}>{source}</li>
              ))}
            </ul>
          </section>
        )}

        {/* Conclusion */}
        <section>
          <h2 className="font-semibold text-lg mb-2">Conclusion & Recommendations</h2>
          {pinnedResults.length > 0 ? (
            <>
              <p className="text-sm font-semibold text-gray-700 mb-2">Based on the research findings and selected insights:</p>
              <ul className="list-disc pl-6 text-sm text-gray-700">
                {pinnedResults.map((item, index) => (
                  <li key={index} className="mb-1">
                    {item.replace(/^Q-\d+: /, '')}
                  </li>
                ))}
              </ul>
            </>
          ) : (
            <p className="text-sm text-gray-500 italic">
              No pinned insights available. Return to the research tabs to pin important findings for your report.
            </p>
          )}
        </section>
      </div>
    </div>
  );
};

export default Reportcardmain;
