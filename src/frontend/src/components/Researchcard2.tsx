
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { config } from "../config/config";
import ClarificationCard from "./ClarificationCard";

interface ResearchContext {
  role: string;
  objective: string;
  topic: string;
}

interface ClarificationOption {
  text: string;
  description: string;
  suggested_query: string;
  category: string;
}

interface ClarificationResponse {
  query: string;
  clarification_question: string;
  options: ClarificationOption[];
  issues: string[];
  confidence: number;
  fallback_interpretation?: string;
  session_id: string;
  timestamp: string;
  response_type: string;
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
  response_type: string;
}

type QueryResponse = ResearchResponse | ClarificationResponse;

const Researchcard2 = () => {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [context, setContext] = useState<ResearchContext | null>(null);
  const [clarificationResponse, setClarificationResponse] = useState<ClarificationResponse | null>(null);
  const navigate = useNavigate();

  // Load context from previous step
  useEffect(() => {
    const savedContext = localStorage.getItem('researchContext');
    if (savedContext) {
      try {
        setContext(JSON.parse(savedContext));
      } catch (e) {
        console.error('Failed to parse research context:', e);
      }
    }
  }, []);

  // Handle research query submission
  const handleSubmitQuery = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    setError(null);
    
    try {
      // Use config for API URL
      const API_BASE_URL = config.apiUrl.replace('/api/v1', '');
      console.log('Submitting query to:', `${API_BASE_URL}/api/v1/research/query`);
      
      const response = await fetch(`${API_BASE_URL}/api/v1/research/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query,
          context: context ? {
            role: context.role,
            objective: context.objective,
            topic: context.topic
          } : undefined,
          session_id: localStorage.getItem('research_session_id') || undefined,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to submit query');
      }

      const result: QueryResponse = await response.json();
      
      // Check if it's a clarification response
      if ('response_type' in result && result.response_type === 'clarification') {
        // Show clarification options
        setClarificationResponse(result as ClarificationResponse);
        localStorage.setItem('research_session_id', result.session_id);
      } else {
        // It's a research response, store and navigate
        const researchResult = result as ResearchResponse;
        localStorage.setItem('researchResult', JSON.stringify(researchResult));
        localStorage.setItem('research_session_id', researchResult.session_id);
        navigate("/reportcard");
      }
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('Research query failed:', err);
    } finally {
      setLoading(false);
    }
  };

  // Handle clarification option selection
  const handleClarificationOption = async (suggestedQuery: string) => {
    setQuery(suggestedQuery);
    setClarificationResponse(null);
    setLoading(true);
    setError(null);
    
    try {
      const API_BASE_URL = config.apiUrl.replace('/api/v1', '');
      
      const response = await fetch(`${API_BASE_URL}/api/v1/research/query/clarified`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: suggestedQuery,
          context: context ? {
            role: context.role,
            objective: context.objective,
            topic: context.topic
          } : undefined,
          session_id: localStorage.getItem('research_session_id') || undefined,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to submit clarified query');
      }

      const result: ResearchResponse = await response.json();
      
      // Store the result and navigate
      localStorage.setItem('researchResult', JSON.stringify(result));
      localStorage.setItem('research_session_id', result.session_id);
      navigate("/reportcard");
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('Clarified query failed:', err);
    } finally {
      setLoading(false);
    }
  };

  // Handle proceeding with fallback interpretation
  const handleProceedAnyway = async () => {
    if (!clarificationResponse?.fallback_interpretation) return;
    
    setClarificationResponse(null);
    setLoading(true);
    setError(null);
    
    try {
      const API_BASE_URL = config.apiUrl.replace('/api/v1', '');
      
      const response = await fetch(`${API_BASE_URL}/api/v1/research/query/clarified`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: query, // Use original query
          context: context ? {
            role: context.role,
            objective: context.objective,
            topic: context.topic
          } : undefined,
          session_id: localStorage.getItem('research_session_id') || undefined,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to submit query');
      }

      const result: ResearchResponse = await response.json();
      
      // Store the result and navigate
      localStorage.setItem('researchResult', JSON.stringify(result));
      localStorage.setItem('research_session_id', result.session_id);
      navigate("/reportcard");
      
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      console.error('Fallback query failed:', err);
    } finally {
      setLoading(false);
    }
  };

  // Handle Enter key press
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !loading) {
      handleSubmitQuery();
    }
  };

  return (
    <div className="flex-1 w-[1210px] h-[500px] bg-[#F7F8FC]">
      <div className="mt-2 ml-60 gap-[54px] w-[720px] h-[400px] bg-[#F7F8FC] rounded-lg">
        {/* Steps Header */}
        <div className="flex items-center justify-center space-x-6">
          <div className="flex flex-col items-center">
            <div className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center">
              01
            </div>
            <p className="text-sm text-blue-600 font-medium mt-1">Context</p>
          </div>

          <div className="w-8 border-t-2 border-blue-600 mt-5" />
          <div className="flex flex-col items-center">
            <div className="w-6 h-6 rounded-full bg-blue-600 text-white flex items-center justify-center">
              02
            </div>
            <p className="text-sm text-blue-600 font-medium mt-1">Research</p>
          </div>
        </div>


        {/* Title */}
        <div className="flex justify-center pt-24 p-6">
          <div className="text-center">
            <p className="text-xl font-medium text-gray-800">
              Type your question
            </p>
            <p className="text-xl font-medium text-gray-800">
              <span className="text-blue-600 font-bold">Nova</span> handles the rest
            </p>
            {context && (
              <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
                <p className="text-sm text-blue-800">
                  <strong>Context:</strong> {context.role} researching {context.topic}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Error message */}
        {error && (
          <div className="flex justify-center mb-4">
            <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-2 rounded-lg max-w-md">
              <p className="text-sm">{error}</p>
            </div>
          </div>
        )}


        {/* Input Field with Send Icon */}
        <div className="flex justify-center">
          <div className="relative w-[500px]">
            {/* Input box */}
            <input
              type="text"
              className="w-full h-[42px] border border-[#D0D5DD] rounded-full bg-white text-sm text-[#344054] pl-4 pr-10 focus:outline-none focus:border-blue-500"
              placeholder="Ask anything"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyPress}
              disabled={loading}
            />

            {/* Send Icon (Button) */}
            <button
              type="button"
              className="absolute top-1/2 -translate-y-1/2 right-3 disabled:opacity-50"
              onClick={handleSubmitQuery}
              disabled={loading || !query.trim()}
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="18"
                height="18"
                viewBox="0 0 18 18"
                fill="none"
              >
                <path
                  d="M16.5003 8.99997C16.5003 9.071 16.4801 9.14058 16.4421 9.20059C16.4041 9.26061 16.3499 9.3086 16.2856 9.33897L2.78564 15.714C2.71821 15.7467 2.64251 15.7583 2.56837 15.7474C2.49424 15.7365 2.42509 15.7035 2.36993 15.6528C2.31477 15.6021 2.27613 15.536 2.25905 15.463C2.24197 15.3901 2.24722 15.3136 2.27414 15.2437L4.40564 9.52347C4.5314 9.18579 4.5314 8.81414 4.40564 8.47647L2.27339 2.75622C2.24634 2.6862 2.24101 2.60965 2.2581 2.53656C2.27519 2.46347 2.31391 2.39723 2.36921 2.34647C2.4245 2.2957 2.49381 2.26278 2.56809 2.25199C2.64238 2.2412 2.71819 2.25304 2.78564 2.28597L16.2856 8.66097C16.3499 8.69134 16.4041 8.73932 16.4421 8.79934C16.4801 8.85935 16.5003 8.92893 16.5003 8.99997ZM16.5003 8.99997H4.50014"
                  stroke={loading ? "#999" : "blue"}
                  strokeWidth="1.125"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            </button>
          </div>
        </div>

        {/* Loading indicator */}
        {loading && (
          <div className="flex justify-center mt-4">
            <div className="flex items-center space-x-2 text-blue-600">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
              <span className="text-sm">Processing your research query...</span>
            </div>
          </div>
        )}

        {/* Clarification Card */}
        {clarificationResponse && (
          <div className="mt-6 max-w-4xl mx-auto">
            <ClarificationCard
              clarification={clarificationResponse}
              onOptionSelect={handleClarificationOption}
              onProceedAnyway={handleProceedAnyway}
              loading={loading}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default Researchcard2;

