

import { useEffect, useRef, useState } from "react";
import config from "../config/config";
import { sessionDataManager } from "../utils/sessionDataManager";
import { conversationStateManager } from "../utils/conversationStateManager";
import FormattedLLMText from "../components/FormattedLLMText";

interface Message {
  sender: "User" | "LLM";
  text: string;
}

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
  sources_used: string[];  // Fixed: match backend field name
  disclaimer?: string;
  session_id: string;
  timestamp: string;
  retrieved_products?: any[];
  web_search_results?: WebSearchResult[];  // Added: web search results
  analysis_complexity?: string;            // Added: analysis complexity
  regulatory_analysis?: any;               // Added: regulatory analysis
}

const Question1 = ({ onPin, researchResult }: { onPin: (text: string) => void; researchResult: ResearchResult | null }) => {
  // Initialize conversation state for Question 1
  const [messages, setMessages] = useState<Message[]>(() => {
    // Initialize with research result if available, otherwise get from conversation state
    if (researchResult) {
      conversationStateManager.initializeQuestion(1, researchResult);
      return conversationStateManager.getMessages(1);
    }
    return conversationStateManager.getMessages(1);
  });
  const [selectedText, setSelectedText] = useState("");
  const [showPin, setShowPin] = useState(false);
  const [pinPosition, setPinPosition] = useState({ x: 0, y: 0 });
  const [inputText, setInputText] = useState("");
  const [editIndex, setEditIndex] = useState<number | null>(null);
  const [editText, setEditText] = useState("");
  const [showConfirm, setShowConfirm] = useState(false);
  const [showDetails, setShowDetails] = useState(false);  // Added: toggle for detailed view
  const [currentResearchResult, setCurrentResearchResult] = useState<ResearchResult | null>(researchResult);

  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  // Update messages when researchResult changes
  useEffect(() => {
    if (researchResult) {
      conversationStateManager.initializeQuestion(1, researchResult);
      setMessages(conversationStateManager.getMessages(1));
      setCurrentResearchResult(researchResult);
    }
  }, [researchResult]);

  // Get the latest research result from session data
  useEffect(() => {
    const latestResult = sessionDataManager.getQuestionResult(1);
    if (latestResult) {
      setCurrentResearchResult(latestResult);
    }
  }, [messages]); // Update when messages change (new queries)

  // --- scroll to bottom whenever messages change ---
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  useEffect(() => {
    const handleMouseUp = () => {
      const selection = window.getSelection();
      const text = selection?.toString();
      if (text && text.trim() !== "" && selection) {
        const range = selection.getRangeAt(0);
        const rect = range.getBoundingClientRect();
        setSelectedText(text);
        setShowPin(true);
        setPinPosition({ x: rect.left, y: rect.top });
      } else {
        setShowPin(false);
      }
    };

    document.addEventListener("mouseup", handleMouseUp);
    return () => document.removeEventListener("mouseup", handleMouseUp);
  }, []);

  const handlePinClick = () => {
    onPin(selectedText);
    setShowPin(false);
    setSelectedText("");
    window.getSelection()?.removeAllRanges();
  };

  // Enhanced message rendering with detailed view
  const renderLLMMessage = (message: Message) => {
    if (message.sender === "LLM" && currentResearchResult) {
      return (
        <div className="bg-gray-100 p-4 rounded-lg mb-4 max-w-[80%]">
          <div className="font-semibold text-gray-700 mb-2">LLM:</div>
          
          {/* Main Answer */}
          <div className="mb-4">
            <FormattedLLMText text={message.text} />
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
              {currentResearchResult.rationale && (
                <div>
                  <h4 className="font-semibold text-gray-700 mb-2">Rationale:</h4>
                  <p className="text-gray-600 text-sm">{currentResearchResult.rationale}</p>
                </div>
              )}
              
              {/* Sources Used */}
              {currentResearchResult.sources_used && currentResearchResult.sources_used.length > 0 && (
                <div>
                  <h4 className="font-semibold text-gray-700 mb-2">Sources Used:</h4>
                  <ul className="text-gray-600 text-sm space-y-1">
                    {currentResearchResult.sources_used.map((source, idx) => (
                      <li key={idx} className="flex items-center">
                        <span className="text-green-500 mr-2">✅</span>
                        {source}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              {/* Web Search Results */}
              {currentResearchResult.web_search_results && currentResearchResult.web_search_results.length > 0 && (
                <div>
                  <h4 className="font-semibold text-gray-700 mb-2">Web Search Results:</h4>
                  <div className="space-y-3">
                    {currentResearchResult.web_search_results.map((result, idx) => (
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
              {currentResearchResult.retrieved_products && currentResearchResult.retrieved_products.length > 0 && (
                <div>
                  <h4 className="font-semibold text-gray-700 mb-2">
                    Retrieved Products ({currentResearchResult.retrieved_products.length}):
                  </h4>
                  <div className="space-y-3">
                    {currentResearchResult.retrieved_products.slice(0, 5).map((product, idx) => (
                      <div key={idx} className="bg-white p-3 rounded border">
                        <h5 className="font-medium text-gray-800 mb-1">
                          {product.product_name || 'Unknown Product'}
                        </h5>
                        <div className="grid grid-cols-2 gap-2 text-sm text-gray-600">
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
                        {product.similarity_score && (
                          <div className="mt-2 text-xs text-gray-500">
                            Similarity Score: {(product.similarity_score * 100).toFixed(1)}%
                          </div>
                        )}
                      </div>
                    ))}
                    {currentResearchResult.retrieved_products.length > 5 && (
                      <p className="text-sm text-gray-500 italic">
                        ... and {currentResearchResult.retrieved_products.length - 5} more products
                      </p>
                    )}
                  </div>
                </div>
              )}
              
              {/* Confidence Score & Data Gaps */}
              <div className="flex gap-4">
              </div>
              
              {/* Disclaimer */}
              {currentResearchResult.disclaimer && (
                <div className="bg-yellow-50 border border-yellow-200 rounded p-3">
                  <h4 className="font-semibold text-yellow-800 mb-2">⚠️ Disclaimer:</h4>
                  <p className="text-yellow-700 text-sm">{currentResearchResult.disclaimer}</p>
                </div>
              )}
            </div>
          )}
        </div>
      );
    }
    
    // Default message rendering
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
        <div className="text-gray-800">
          {message.sender === "LLM" ? (
            <FormattedLLMText text={message.text} />
          ) : (
            message.text
          )}
        </div>
      </div>
    );
  };

  const handleSend = async () => {
    if (inputText.trim() === "") return;
    
    const userMessage: Message = { sender: "User", text: inputText.trim() };
    setMessages((prev) => [...prev, userMessage]);
    setInputText("");
    
    // Show loading state
    const loadingMessage: Message = { sender: "LLM", text: "Thinking..." };
    setMessages((prev) => [...prev, loadingMessage]);
    
    try {
      // Get session ID from session data manager
      const sessionId = sessionDataManager.getCurrentSessionId();
      
      console.log('🔍 Sending query with session ID:', sessionId);
      
      // Use the research API to get a real response
      const API_BASE_URL = config.apiUrl.replace('/api/v1', '');
      const response = await fetch(`${API_BASE_URL}/api/v1/research/query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: inputText.trim(),
          context: researchResult ? {
            previous_query: researchResult.query,
            session_id: researchResult.session_id
          } : undefined,
          session_id: sessionId,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const result = await response.json();
      
      // Store research result in session data for comprehensive report generation
      if (result.response_type === 'research') {
        sessionDataManager.addQuestionResult(1, result);
        console.log('✅ Stored Question 1 result in session data');
      }
      
      // Replace loading message with actual response
      const newMessages = messages.slice(0, -1).concat([{ sender: "LLM", text: result.answer }]);
      setMessages(newMessages);
      conversationStateManager.updateMessages(1, newMessages);
      
    } catch (error) {
      console.error('Error getting LLM response:', error);
      // Replace loading message with error message
      const errorMessages = messages.slice(0, -1).concat([{ 
        sender: "LLM", 
        text: "Sorry, I couldn't process your question right now. Please try again." 
      }]);
      setMessages(errorMessages);
      conversationStateManager.updateMessages(1, errorMessages);
    }
  };

  const handleEditClick = (index: number) => {
    setEditIndex(index);
    setEditText(messages[index].text);
  };

  const handleSaveEdit = () => {
    setShowConfirm(true);
  };

  const confirmSave = async () => {
    if (editIndex === null) return;
    
    const updated = [...messages];
    updated[editIndex].text = editText;
    
    // If we're editing a user message, we need to regenerate subsequent responses
    if (messages[editIndex].sender === "User") {
      // Remove all messages after the edited one
      const messagesUpToEdit = updated.slice(0, editIndex + 1);
      setMessages(messagesUpToEdit);
      conversationStateManager.updateMessages(1, messagesUpToEdit);
      
      // Add loading message
      const loadingMessage: Message = { sender: "LLM", text: "Regenerating response..." };
      const messagesWithLoading = [...messagesUpToEdit, loadingMessage];
      setMessages(messagesWithLoading);
      conversationStateManager.updateMessages(1, messagesWithLoading);
      
      try {
        // Use the research API to get a new response based on the edited message
        const API_BASE_URL = config.apiUrl.replace('/api/v1', '');
        const response = await fetch(`${API_BASE_URL}/api/v1/research/query`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            query: editText.trim(),
            context: researchResult ? {
              previous_query: researchResult.query,
              session_id: researchResult.session_id
            } : undefined,
            session_id: researchResult?.session_id || undefined,
          }),
        });

        if (!response.ok) {
          throw new Error('Failed to get response');
        }

        const result = await response.json();
        
        // Store updated research result in session data
        if (result.response_type === 'research') {
          sessionDataManager.addQuestionResult(1, result);
          console.log('✅ Updated Question 1 result in session data');
        }
        
        // Replace loading message with actual response
        const regeneratedMessages = messages.slice(0, -1).concat([{ sender: "LLM", text: result.answer }]);
        setMessages(regeneratedMessages);
        conversationStateManager.updateMessages(1, regeneratedMessages);
        
      } catch (error) {
        console.error('Error regenerating LLM response:', error);
        // Replace loading message with error message
        const errorMessages = messages.slice(0, -1).concat([{ 
          sender: "LLM", 
          text: "Sorry, I couldn't regenerate the response right now. Please try again." 
        }]);
        setMessages(errorMessages);
        conversationStateManager.updateMessages(1, errorMessages);
      }
    } else {
      // If editing an LLM message, just update the text
      setMessages(updated);
      conversationStateManager.updateMessages(1, updated);
    }
    
    setEditIndex(null);
    setEditText("");
    setShowConfirm(false);
    console.log("Changes saved, -10 credits deducted.");
  };

  return (
    <div className="relative bg-white p-4 rounded shadow w-full h-full flex flex-col overflow-hidden">
      {/* Header */}
      <h2 className="text-lg font-semibold mb-2">Conversation for Question 1</h2>

      {/* Messages */}
      <div className="space-y-4 flex-1 overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100 hover:scrollbar-thumb-gray-400">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex items-start ${
              msg.sender === "User" ? "justify-end" : "justify-between"
            }`}
          >
            {msg.sender === "LLM" ? (
              renderLLMMessage(msg)
            ) : (
              <div className="flex flex-col items-end max-w-[70%]">
                <div className="px-4 py-2 rounded-lg bg-blue-100 text-sm text-right">
                  <strong>{msg.sender}:</strong> {msg.text}
                </div>
                {/* Edit button below message */}
                <button
                  onClick={() => handleEditClick(idx)}
                  className="text-gray-500 hover:text-gray-700 mt-1"
                >
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="16"
                    height="16"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  >
                    <path d="M12 20h9" />
                    <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" />
                  </svg>
                </button>
              </div>
            )}
          </div>
        ))}
        {/* dummy div to auto-scroll */}
        <div ref={messagesEndRef} />
      </div>

      {/* Floating Pin */}
      {showPin && (
        <button
          onClick={handlePinClick}
          style={{
            position: "absolute",
            top: pinPosition.y + window.scrollY - 40,
            left: pinPosition.x + window.scrollX,
            zIndex: 1000
          }}
          className="bg-white border border-gray-400 px-2 py-1 text-xs rounded shadow hover:bg-gray-100"
        >
          📌 Pin
        </button>
      )}

      {/* Input */}
      <div className="pt-3 border-t mt-3 flex items-center">
        <input
          type="text"
          placeholder="Please add context to your question"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSend();
            }
          }}
          className="flex-1 bg-transparent outline-none text-sm px-3 py-2"
        />
        <button className="ml-2 p-2" onClick={handleSend}>
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="18"
            height="18"
            fill="none"
            viewBox="0 0 18 18"
          >
            <path
              d="M16.5 9a.51.51 0 0 1-.058.239.57.57 0 0 1-.157.199.65.65 0 0 1-.26.1L2.785 15.714a.61.61 0 0 1-.674-.465.61.61 0 0 1 .163-.506l2.132-5.72a.91.91 0 0 0 0-.602L2.274 2.7a.61.61 0 0 1 .674-.764l13.5 6.375a.6.6 0 0 1 .26.1.57.57 0 0 1 .157.199A.51.51 0 0 1 16.5 9ZM16.5 9H4.5"
              stroke="blue"
              strokeWidth="1.125"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </button>
      </div>

      {/* Edit Modal */}
      {editIndex !== null && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded shadow-lg w-1/3">
            <h3 className="font-semibold mb-2">Edit Message</h3>
            <textarea
              className="w-full border border-gray-300 p-2 text-sm mb-4"
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
        </div>
      )}

      {/* Confirmation Popup */}
      {showConfirm && (
        <div className="fixed inset-0 bg-black bg-opacity-40 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-xl shadow-lg w-80 text-center">
            <h2 className="text-lg font-semibold mb-4">Confirm Edit</h2>
            <p className="text-gray-600 mb-6">
              {messages[editIndex!]?.sender === "User" 
                ? "Editing this message will regenerate the AI response. This will cost "
                : "To make these changes, you will lose "
              }
              <span className="font-bold text-red-500">10 credits</span>.
            </p>
            <div className="flex justify-around">
              <button
                onClick={() => setShowConfirm(false)}
                className="px-4 py-2 bg-gray-300 rounded-lg hover:bg-gray-400"
              >
                Cancel
              </button>
              <button
                onClick={confirmSave}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
              >
                Confirm
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Question1;
