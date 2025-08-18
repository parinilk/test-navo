import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import Navbarcredit from "../components/Navbarcredit";

interface WebSearchResult {
  title: string;
  snippet: string;
  url: string;
  source: string;
  position: number;
}

interface ResearchResponse {
  query: string;
  answer: string;
  rationale: string;
  sources_used: string[];
  disclaimer?: string;
  session_id: string;
  timestamp: string;
  retrieved_products?: any[];
  web_search_results?: WebSearchResult[];
  // Enhanced fields for System Prompt compliance
  confidence_score?: number;
  data_gaps?: string[];
  analysis_complexity?: string;
  regulatory_analysis?: any;
}

const ResearchResults: React.FC = () => {
  const [result, setResult] = useState<ResearchResponse | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    const savedResult = localStorage.getItem('researchResult');
    if (savedResult) {
      try {
        setResult(JSON.parse(savedResult));
      } catch (e) {
        console.error('Failed to parse research result:', e);
        navigate('/research');
      }
    } else {
      navigate('/research');
    }
  }, [navigate]);

  const handleNewQuery = () => {
    localStorage.removeItem('researchResult');
    localStorage.removeItem('researchContext');
    navigate('/research');
  };

  if (!result) {
    return (
      <>
        <Navbarcredit />
        <div className="flex">
          <Sidebar />
          <div className="flex-1 flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <Navbarcredit />
      <div className="flex">
        <Sidebar />
        <div className="flex-1 p-8 bg-[#F7F8FC] min-h-screen">
          <div className="max-w-4xl mx-auto">
            {/* Header */}
            <div className="mb-6">
              <div className="flex justify-between items-start">
                <div>
                  <h1 className="text-2xl font-bold text-gray-900 mb-2">Research Results</h1>
                  <p className="text-gray-600 italic">"{result.query}"</p>
                </div>
                <button
                  onClick={handleNewQuery}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  New Query
                </button>
              </div>
              <div className="mt-4 text-sm text-gray-500">
                Session: {result.session_id} • {new Date(result.timestamp).toLocaleString()}
              </div>
            </div>

            {/* Main Answer */}
            <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Answer</h2>
              <div className="prose max-w-none">
                <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">{result.answer}</p>
              </div>
            </div>

            {/* Rationale */}
            <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Rationale</h2>
              <div className="prose max-w-none">
                <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">{result.rationale}</p>
              </div>
            </div>

            {/* Sources */}
            <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
              <h2 className="text-xl font-semibold text-gray-900 mb-4">Sources Used</h2>
              <ul className="space-y-2">
                {result.sources_used.map((source, index) => (
                  <li key={index} className="flex items-center text-gray-700">
                    <span className="w-2 h-2 bg-green-500 rounded-full mr-3"></span>
                    {source}
                  </li>
                ))}
              </ul>
            </div>

            {/* Retrieved Products */}
            {result.retrieved_products && result.retrieved_products.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  Retrieved Products ({result.retrieved_products.length})
                </h2>
                <div className="grid gap-4">
                  {result.retrieved_products.slice(0, 5).map((product, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4">
                      <h3 className="font-medium text-gray-900 mb-2">
                        {product.product_name || 'Unknown Product'}
                      </h3>
                      <div className="grid grid-cols-2 gap-4 text-sm text-gray-600">
                        {product.brand && (
                          <div><strong>Brand:</strong> {product.brand}</div>
                        )}
                        {product.category && (
                          <div><strong>Category:</strong> {product.category}</div>
                        )}
                        {product.price && (
                          <div><strong>Price:</strong> ${product.price}</div>
                        )}
                        {product.availability && (
                          <div><strong>Availability:</strong> {product.availability}</div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Web Search Results */}
            {result.web_search_results && result.web_search_results.length > 0 && (
              <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">
                  Web Search Results ({result.web_search_results.length})
                </h2>
                <div className="space-y-4">
                  {result.web_search_results.map((webResult, index) => (
                    <div key={index} className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors hover:shadow-sm">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="font-medium mb-2">
                            <a 
                              href={webResult.url.startsWith('http') ? webResult.url : `https://${webResult.url}`}
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="text-blue-600 hover:text-blue-800 hover:underline cursor-pointer transition-colors"
                              onClick={() => {
                                // Ensure the link works
                                const url = webResult.url.startsWith('http') ? webResult.url : `https://${webResult.url}`;
                                window.open(url, '_blank', 'noopener,noreferrer');
                              }}
                            >
                              {webResult.title}
                            </a>
                          </h3>
                          <p className="text-gray-700 text-sm mb-3 leading-relaxed">
                            {webResult.snippet}
                          </p>
                          <div className="flex items-center justify-between text-xs">
                            <span className="bg-gray-100 px-3 py-1 rounded-full text-gray-600">
                              📄 {webResult.source}
                            </span>
                            <a 
                              href={webResult.url.startsWith('http') ? webResult.url : `https://${webResult.url}`}
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="text-blue-600 hover:text-blue-800 hover:underline font-medium cursor-pointer transition-colors"
                              onClick={() => {
                                // Ensure the link works
                                const url = webResult.url.startsWith('http') ? webResult.url : `https://${webResult.url}`;
                                window.open(url, '_blank', 'noopener,noreferrer');
                              }}
                            >
                              🔗 Visit Source →
                            </a>
                          </div>
                          <div className="mt-2 text-xs text-gray-400">
                            {webResult.url}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Enhanced Analysis Section */}
            {(result.confidence_score !== undefined || result.data_gaps || result.analysis_complexity || result.regulatory_analysis) && (
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 mb-6">
                <h2 className="text-lg font-semibold text-blue-800 mb-4">📊 Analysis Assessment</h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {/* Confidence Score */}
                  {result.confidence_score !== undefined && (
                    <div className="bg-white rounded-lg p-4">
                      <h3 className="font-medium text-gray-900 mb-2">Confidence Score</h3>
                      <div className="flex items-center space-x-3">
                        <div className="flex-1 bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${
                              result.confidence_score >= 0.8 ? 'bg-green-500' :
                              result.confidence_score >= 0.6 ? 'bg-yellow-500' :
                              result.confidence_score >= 0.4 ? 'bg-orange-500' : 'bg-red-500'
                            }`}
                            style={{ width: `${(result.confidence_score * 100)}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium text-gray-700">
                          {(result.confidence_score * 100).toFixed(0)}%
                        </span>
                      </div>
                      <div className="mt-1 text-xs text-gray-500">
                        {result.confidence_score >= 0.8 ? 'High Confidence' :
                         result.confidence_score >= 0.6 ? 'Medium Confidence' :
                         result.confidence_score >= 0.4 ? 'Low Confidence' : 'Very Low Confidence'}
                      </div>
                    </div>
                  )}

                  {/* Analysis Complexity */}
                  {result.analysis_complexity && (
                    <div className="bg-white rounded-lg p-4">
                      <h3 className="font-medium text-gray-900 mb-2">Analysis Complexity</h3>
                      <div className="flex items-center space-x-2">
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                          result.analysis_complexity === 'high' ? 'bg-red-100 text-red-800' :
                          result.analysis_complexity === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {result.analysis_complexity.charAt(0).toUpperCase() + result.analysis_complexity.slice(1)}
                        </span>
                        <span className="text-xs text-gray-500">
                          {result.analysis_complexity === 'high' ? '🔴 Multi-dimensional' :
                           result.analysis_complexity === 'medium' ? '🟡 Multi-faceted' :
                           '🟢 Straightforward'}
                        </span>
                      </div>
                    </div>
                  )}
                </div>

                {/* Data Gaps */}
                {result.data_gaps && result.data_gaps.length > 0 && (
                  <div className="mt-4 bg-white rounded-lg p-4">
                    <h3 className="font-medium text-gray-900 mb-3">🔍 Identified Data Gaps</h3>
                    <ul className="space-y-2">
                      {result.data_gaps.map((gap, index) => (
                        <li key={index} className="flex items-start text-sm text-gray-700">
                          <span className="w-2 h-2 bg-orange-400 rounded-full mr-3 mt-2 flex-shrink-0"></span>
                          <span>{gap}</span>
                        </li>
                      ))}
                    </ul>
                    <div className="mt-3 text-xs text-gray-500 italic">
                      💡 These gaps may affect analysis completeness. Consider obtaining additional data for more comprehensive insights.
                    </div>
                  </div>
                )}

                {/* Regulatory Analysis */}
                {result.regulatory_analysis && (
                  <div className="mt-4 bg-white rounded-lg p-4">
                    <h3 className="font-medium text-gray-900 mb-3">⚖️ Regulatory Considerations</h3>
                    <div className="text-sm text-gray-700">
                      {result.regulatory_analysis.note && (
                        <p className="mb-2">{result.regulatory_analysis.note}</p>
                      )}
                      {result.regulatory_analysis.recommendation && (
                        <p className="text-orange-700 bg-orange-50 p-2 rounded">
                          <strong>Recommendation:</strong> {result.regulatory_analysis.recommendation}
                        </p>
                      )}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Disclaimer */}
            {result.disclaimer && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
                <h2 className="text-lg font-semibold text-yellow-800 mb-2">⚠️ Disclaimer</h2>
                <p className="text-yellow-700 text-sm leading-relaxed">{result.disclaimer}</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
};

export default ResearchResults;

