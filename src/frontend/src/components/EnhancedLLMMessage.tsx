import React, { useState } from 'react';

interface WebSearchResult {
  title: string;
  source: string;
  snippet: string;
  url: string;
}

interface ResearchResult {
  query: string;
  answer: string;
  rationale: string;
  sources_used: string[];
  disclaimer?: string;
  session_id: string;
  timestamp: string;
  retrieved_products?: any[];
  web_search_results?: WebSearchResult[];
  confidence_score?: number;
  data_gaps?: string[];
  analysis_complexity?: string;
  regulatory_analysis?: any;
}

interface EnhancedLLMMessageProps {
  message: { sender: string; text: string };
  researchResult: ResearchResult | null;
}

const EnhancedLLMMessage: React.FC<EnhancedLLMMessageProps> = ({ message, researchResult }) => {
  const [showDetails, setShowDetails] = useState(false);

  // If no research result or not an LLM message, render normally
  if (!researchResult || message.sender !== "LLM") {
    return (
      <div className={`p-4 rounded-lg mb-4 max-w-[80%] ${
        message.sender === "User" 
          ? "bg-blue-100 ml-auto" 
          : "bg-gray-100"
      }`}>
        <div className={`font-semibold mb-2 ${
          message.sender === "User" ? "text-blue-700" : "text-gray-700"
        }`}>
          {message.sender}:
        </div>
        <div className="text-gray-800">{message.text}</div>
      </div>
    );
  }

  return (
    <div className="bg-gray-100 p-4 rounded-lg mb-4 max-w-[80%]">
      <div className="font-semibold text-gray-700 mb-2">LLM:</div>
      
      {/* Main Answer */}
      <div className="text-gray-800 mb-4">
        {message.text}
      </div>
      
      {/* Toggle Details Button */}
      <button
        onClick={() => setShowDetails(!showDetails)}
        className="text-blue-600 hover:text-blue-800 text-sm underline mb-2"
      >
        {showDetails ? "Hide Details" : "Show Full Report"}
      </button>
      
      {/* Detailed View */}
      {showDetails && (
        <div className="border-t pt-4 space-y-4">
          
          {/* Rationale */}
          {researchResult.rationale && (
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Rationale:</h4>
              <p className="text-gray-600 text-sm">{researchResult.rationale}</p>
            </div>
          )}
          
          {/* Sources Used */}
          {researchResult.sources_used && researchResult.sources_used.length > 0 && (
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Sources Used:</h4>
              <ul className="text-gray-600 text-sm space-y-1">
                {researchResult.sources_used.map((source, idx) => (
                  <li key={idx} className="flex items-center">
                    <span className="text-green-500 mr-2">✅</span>
                    {source}
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {/* Web Search Results */}
          {researchResult.web_search_results && researchResult.web_search_results.length > 0 && (
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Web Search Results:</h4>
              <div className="space-y-3">
                {researchResult.web_search_results.map((result, idx) => (
                  <div key={idx} className="bg-white p-3 rounded border">
                    <h5 className="font-medium text-gray-800 mb-1">{result.title}</h5>
                    <p className="text-gray-600 text-sm mb-1">Source: {result.source}</p>
                    {result.snippet && (
                      <p className="text-gray-500 text-xs">{result.snippet}</p>
                    )}
                    {result.url && (
                      <a 
                        href={result.url} 
                        target="_blank" 
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-800 text-xs underline"
                      >
                        View Source
                      </a>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Retrieved Products */}
          {researchResult.retrieved_products && researchResult.retrieved_products.length > 0 && (
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Retrieved Products:</h4>
              <div className="space-y-2">
                {researchResult.retrieved_products.slice(0, 3).map((product, idx) => (
                  <div key={idx} className="bg-white p-2 rounded border text-sm">
                    <div className="font-medium text-gray-800">{product.product_name || 'Unknown Product'}</div>
                    {product.brand && <div className="text-gray-600">Brand: {product.brand}</div>}
                    {product.category && <div className="text-gray-600">Category: {product.category}</div>}
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Confidence Score & Data Gaps */}
          <div className="flex gap-4">
            {researchResult.confidence_score !== undefined && (
              <div>
                <h4 className="font-semibold text-gray-700 mb-2">Confidence Score:</h4>
                <div className="flex items-center">
                  <div className="w-20 bg-gray-200 rounded-full h-2 mr-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full" 
                      style={{ width: `${researchResult.confidence_score * 100}%` }}
                    ></div>
                  </div>
                  <span className="text-sm text-gray-600">
                    {Math.round(researchResult.confidence_score * 100)}%
                  </span>
                </div>
              </div>
            )}
            
            {researchResult.data_gaps && researchResult.data_gaps.length > 0 && (
              <div>
                <h4 className="font-semibold text-gray-700 mb-2">Data Gaps:</h4>
                <ul className="text-gray-600 text-sm space-y-1">
                  {researchResult.data_gaps.map((gap, idx) => (
                    <li key={idx} className="flex items-center">
                      <span className="text-yellow-500 mr-2">⚠️</span>
                      {gap}
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
          
          {/* Analysis Complexity */}
          {researchResult.analysis_complexity && (
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Analysis Complexity:</h4>
              <span className="inline-block px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                {researchResult.analysis_complexity}
              </span>
            </div>
          )}
          
          {/* Regulatory Analysis */}
          {researchResult.regulatory_analysis && (
            <div>
              <h4 className="font-semibold text-gray-700 mb-2">Regulatory Analysis:</h4>
              <div className="bg-orange-50 border border-orange-200 rounded p-3">
                <p className="text-orange-800 text-sm">{researchResult.regulatory_analysis.note}</p>
                {researchResult.regulatory_analysis.recommendation && (
                  <p className="text-orange-700 text-sm mt-1">
                    <strong>Recommendation:</strong> {researchResult.regulatory_analysis.recommendation}
                  </p>
                )}
              </div>
            </div>
          )}
          
          {/* Disclaimer */}
          {researchResult.disclaimer && (
            <div className="bg-yellow-50 border border-yellow-200 rounded p-3">
              <h4 className="font-semibold text-yellow-800 mb-2">⚠️ Disclaimer:</h4>
              <p className="text-yellow-700 text-sm">{researchResult.disclaimer}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default EnhancedLLMMessage;
