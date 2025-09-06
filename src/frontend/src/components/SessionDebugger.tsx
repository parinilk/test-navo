import React, { useState, useEffect } from 'react';
import { sessionManager } from '../utils/sessionManager';

const SessionDebugger: React.FC = () => {
  const [sessionInfo, setSessionInfo] = useState(sessionManager.getSessionInfo());

  useEffect(() => {
    const interval = setInterval(() => {
      setSessionInfo(sessionManager.getSessionInfo());
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const handleNewSession = () => {
    sessionManager.startNewSession();
    setSessionInfo(sessionManager.getSessionInfo());
  };

  const handleClearSession = () => {
    sessionManager.clearSession();
    setSessionInfo(sessionManager.getSessionInfo());
  };

  return (
    <div className="fixed bottom-4 right-4 bg-white border border-gray-300 rounded-lg p-4 shadow-lg z-50 max-w-sm">
      <h3 className="font-semibold text-sm mb-2">🔍 Session Debugger</h3>
      
      <div className="text-xs space-y-1">
        <div>
          <strong>Session ID:</strong>
          <div className="font-mono text-xs bg-gray-100 p-1 rounded break-all">
            {sessionInfo.sessionId || 'None'}
          </div>
        </div>
        
        <div>
          <strong>Has Context:</strong> {sessionInfo.hasContext ? '✅ Yes' : '❌ No'}
        </div>
        
        {sessionInfo.context && (
          <div>
            <strong>Context:</strong>
            <div className="bg-gray-100 p-1 rounded text-xs">
              <div>Role: {sessionInfo.context.role}</div>
              <div>Objective: {sessionInfo.context.objective}</div>
              <div>Topic: {sessionInfo.context.topic}</div>
            </div>
          </div>
        )}
      </div>
      
      <div className="flex gap-2 mt-3">
        <button
          onClick={handleNewSession}
          className="px-2 py-1 bg-blue-500 text-white text-xs rounded hover:bg-blue-600"
        >
          New Session
        </button>
        <button
          onClick={handleClearSession}
          className="px-2 py-1 bg-red-500 text-white text-xs rounded hover:bg-red-600"
        >
          Clear
        </button>
      </div>
    </div>
  );
};

export default SessionDebugger;
