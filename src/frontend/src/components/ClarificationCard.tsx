import React from 'react';

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

interface ClarificationCardProps {
  clarification: ClarificationResponse;
  onOptionSelect: (suggestedQuery: string) => void;
  onProceedAnyway: () => void;
  loading?: boolean;
}

const ClarificationCard: React.FC<ClarificationCardProps> = ({
  clarification,
  onOptionSelect,
  onProceedAnyway,
  loading = false
}) => {
  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'specification':
        return '🎯';
      case 'skin_type':
        return '👤';
      case 'budget':
        return '💰';
      case 'purpose':
        return '📋';
      case 'intent':
        return '🎯';
      default:
        return '💡';
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'specification':
        return 'bg-blue-50 border-blue-200';
      case 'skin_type':
        return 'bg-green-50 border-green-200';
      case 'budget':
        return 'bg-yellow-50 border-yellow-200';
      case 'purpose':
        return 'bg-purple-50 border-purple-200';
      case 'intent':
        return 'bg-indigo-50 border-indigo-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-3 text-gray-600">Processing your refined query...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border">
      {/* Header */}
      <div className="bg-amber-50 border-b border-amber-200 p-6 rounded-t-lg">
        <div className="flex items-start space-x-3">
          <div className="flex-shrink-0">
            <div className="w-8 h-8 bg-amber-100 rounded-full flex items-center justify-center">
              <span className="text-lg">🤔</span>
            </div>
          </div>
          <div className="flex-grow">
            <h2 className="text-lg font-semibold text-amber-800 mb-2">
              Let me help clarify your request
            </h2>
            <p className="text-amber-700 text-sm">
              Your query "<span className="font-medium">{clarification.query}</span>" could mean several things. 
              To give you the most accurate results, could you help me understand what you're looking for?
            </p>
          </div>
        </div>
      </div>

      {/* Clarification Question */}
      <div className="p-6 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900 mb-3">
          {clarification.clarification_question}
        </h3>
        
        {/* Issues detected */}
        {clarification.issues.length > 0 && (
          <div className="mb-4 p-3 bg-blue-50 rounded-lg">
            <p className="text-sm text-blue-700 font-medium mb-1">What I noticed:</p>
            <ul className="text-sm text-blue-600 space-y-1">
              {clarification.issues.map((issue, index) => (
                <li key={index} className="flex items-start space-x-2">
                  <span className="text-blue-500 mt-0.5">•</span>
                  <span>{issue}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Options */}
      <div className="p-6">
        <h4 className="text-md font-medium text-gray-900 mb-4">
          Please select the option that best matches what you're looking for:
        </h4>
        
        <div className="space-y-3">
          {clarification.options.map((option, index) => (
            <button
              key={index}
              onClick={() => onOptionSelect(option.suggested_query)}
              className={`w-full text-left p-4 rounded-lg border-2 transition-all hover:shadow-md ${getCategoryColor(option.category)} hover:border-blue-300`}
            >
              <div className="flex items-start space-x-3">
                <span className="text-lg flex-shrink-0 mt-0.5">
                  {getCategoryIcon(option.category)}
                </span>
                <div className="flex-grow min-w-0">
                  <div className="font-medium text-gray-900 mb-1">
                    {option.text}
                  </div>
                  <div className="text-sm text-gray-600 mb-2">
                    {option.description}
                  </div>
                  <div className="text-xs text-gray-500 bg-white/60 rounded px-2 py-1 inline-block">
                    Would search: "{option.suggested_query}"
                  </div>
                </div>
              </div>
            </button>
          ))}
        </div>

        {/* Fallback option */}
        {clarification.fallback_interpretation && (
          <div className="mt-6 pt-6 border-t border-gray-200">
            <div className="bg-gray-50 rounded-lg p-4">
              <h5 className="font-medium text-gray-900 mb-2">
                Or, I can proceed with my best guess:
              </h5>
              <p className="text-sm text-gray-600 mb-3">
                {clarification.fallback_interpretation}
              </p>
              <button
                onClick={onProceedAnyway}
                className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors text-sm"
              >
                Proceed with this interpretation
              </button>
            </div>
          </div>
        )}

        {/* Tips */}
        <div className="mt-6 pt-6 border-t border-gray-200">
          <div className="bg-blue-50 rounded-lg p-4">
            <h5 className="font-medium text-blue-900 mb-2 flex items-center">
              <span className="mr-2">💡</span>
              Tips for better results:
            </h5>
            <ul className="text-sm text-blue-700 space-y-1">
              <li>• Be specific about your skin type, concerns, or goals</li>
              <li>• Include your budget range if price matters</li>
              <li>• Mention if you prefer certain brands or ingredients</li>
              <li>• Specify if you want products to buy vs. general information</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ClarificationCard;
