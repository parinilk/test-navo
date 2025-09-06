import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import dashboardApi from '../services/dashboardApi';
import type { DashboardData, ResearchSessionSummary } from '../services/dashboardApi';
import CustomDatePicker from './CustomDatePicker';

const DynamicDashboard: React.FC = () => {
  const navigate = useNavigate();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortOrder, setSortOrder] = useState<'newest' | 'oldest'>('newest');

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await dashboardApi.getDashboardData(undefined, 10, 10);
      setDashboardData(data);
    } catch (err) {
      setError('Failed to load dashboard data. Please try again.');
      console.error('Dashboard loading error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteSession = async (sessionId: string) => {
    if (!confirm('Are you sure you want to delete this research session?')) {
      return;
    }

    const success = await dashboardApi.deleteSession(sessionId);
    if (success) {
      // Reload dashboard data after deletion
      await loadDashboardData();
    } else {
      alert('Failed to delete session. Please try again.');
    }
  };

  const handleContinueResearch = (sessionId: string) => {
    // Navigate to research page with the session ID
    navigate(`/research?session_id=${sessionId}`);
  };

  const handleViewReport = (sessionId: string) => {
    // Navigate to report page with the session ID
    navigate(`/report?session_id=${sessionId}`);
  };

  const filteredAndSortedSessions = (sessions: ResearchSessionSummary[]) => {
    let filtered = sessions;
    
    if (searchTerm) {
      filtered = sessions.filter(session => 
        session.title.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    return filtered.sort((a, b) => {
      const dateA = new Date(a.last_activity).getTime();
      const dateB = new Date(b.last_activity).getTime();
      return sortOrder === 'newest' ? dateB - dateA : dateA - dateB;
    });
  };

  const DraftCard: React.FC<{ session: ResearchSessionSummary }> = ({ session }) => (
    <div className="bg-white rounded-lg border border-[#EAECF0] p-4 w-1/3 flex flex-col gap-2 group hover:shadow-md transition-shadow cursor-pointer" onClick={() => handleContinueResearch(session.session_id)}>
      <div className="flex justify-between">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 18 18" fill="none">
          <g clipPath="url(#clip0_178_1708)">
            <path d="M10.05 1.49999H4.5C4.10218 1.49999 3.72064 1.65802 3.43934 1.93933C3.15804 2.22063 3 2.60216 3 2.99999V15C3 15.3978 3.15804 15.7793 3.43934 16.0606C3.72064 16.342 4.10218 16.5 4.5 16.5H13.5C13.8978 16.5 14.2794 16.342 14.5607 16.0606C14.842 15.7793 15 15.3978 15 15V9.44999M1.5 4.49999H4.5M1.5 7.49999H4.5M1.5 10.5H4.5M1.5 13.5H4.5M16.0335 4.21949C16.3323 3.92072 16.5001 3.51551 16.5001 3.09299C16.5001 2.67047 16.3323 2.26526 16.0335 1.96649C15.7347 1.66772 15.3295 1.49988 14.907 1.49988C14.4845 1.49988 14.0793 1.66772 13.7805 1.96649L10.023 5.72549C9.84469 5.90371 9.71416 6.12399 9.6435 6.36599L9.01575 8.51849C8.99693 8.58303 8.9958 8.65143 9.01248 8.71656C9.02917 8.78168 9.06305 8.84112 9.11058 8.88865C9.15812 8.93619 9.21756 8.97007 9.28268 8.98676C9.3478 9.00344 9.41621 9.00231 9.48075 8.98349L11.6332 8.35574C11.8752 8.28507 12.0955 8.15455 12.2737 7.97624L16.0335 4.21949Z" stroke="black" strokeWidth="1.35" strokeLinecap="round" strokeLinejoin="round" />
          </g>
          <defs>
            <clipPath id="clip0_178_1708">
              <rect width="18" height="18" fill="white" />
            </clipPath>
          </defs>
        </svg>

        <div className="relative">
          <button 
            className="p-1 hover:bg-gray-100 rounded"
            onClick={(e) => {
              e.stopPropagation(); // Prevent card click
            }}
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 18 18" fill="none">
              <path d="M9 9.75C9.41421 9.75 9.75 9.41421 9.75 9C9.75 8.58579 9.41421 8.25 9 8.25C8.58579 8.25 8.25 8.58579 8.25 9C8.25 9.41421 8.58579 9.75 9 9.75Z" stroke="black" strokeWidth="1.125" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M14.25 9.75C14.6642 9.75 15 9.41421 15 9C15 8.58579 14.6642 8.25 14.25 8.25C13.8358 8.25 13.5 8.58579 13.5 9C13.5 9.41421 13.8358 9.75 14.25 9.75Z" stroke="black" strokeWidth="1.125" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M3.75 9.75C4.16421 9.75 4.5 9.41421 4.5 9C4.5 8.58579 4.16421 8.25 3.75 8.25C3.33579 8.25 3 8.58579 3 9C3 9.41421 3.33579 9.75 3.75 9.75Z" stroke="black" strokeWidth="1.125" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
          <div className="absolute right-0 top-8 bg-white border border-gray-200 rounded-lg shadow-lg py-2 w-40 z-10 hidden group-hover:block">
            <button 
              onClick={(e) => {
                e.stopPropagation();
                handleContinueResearch(session.session_id);
              }}
              className="w-full text-left px-4 py-2 hover:bg-gray-100 text-sm"
            >
              Continue Research
            </button>
            <button 
              onClick={(e) => {
                e.stopPropagation();
                handleDeleteSession(session.session_id);
              }}
              className="w-full text-left px-4 py-2 hover:bg-gray-100 text-sm text-red-600"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
      
      <span className="text-left text-sm">Draft</span>
      <h5 className="text-[#101828] text-left font-semibold line-clamp-2" title={session.title}>
        {session.title}
      </h5>
      <p className="text-xs text-[#667085] text-left">
        Last updated {dashboardApi.formatDate(session.last_activity)}
      </p>
      <div className="flex justify-between items-center">
        <span className={`w-fit px-2 py-1 text-xs rounded-full ${dashboardApi.getStatusColor(session.status)}`}>
          {dashboardApi.getStatusText(session.status)}
        </span>
        <span className="text-xs text-[#667085]">
          {session.total_queries} question{session.total_queries !== 1 ? 's' : ''}
        </span>
      </div>
    </div>
  );

  const CompletedCard: React.FC<{ session: ResearchSessionSummary }> = ({ session }) => (
    <div className="bg-white rounded-lg border border-[#EAECF0] p-4 flex flex-col gap-1 group">
      <div className="flex justify-between items-start">
        <h2 className="text-[#101828] font-sm text-left flex-1 line-clamp-2" title={session.title}>
          {session.title}
        </h2>
        <div className="relative">
          <button className="p-1 hover:bg-gray-100 rounded opacity-0 group-hover:opacity-100 transition-opacity">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 18 18" fill="none">
              <path d="M9 9.75C9.41421 9.75 9.75 9.41421 9.75 9C9.75 8.58579 9.41421 8.25 9 8.25C8.58579 8.25 8.25 8.58579 8.25 9C8.25 9.41421 8.58579 9.75 9 9.75Z" stroke="black" strokeWidth="1.125" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M14.25 9.75C14.6642 9.75 15 9.41421 15 9C15 8.58579 14.6642 8.25 14.25 8.25C13.8358 8.25 13.5 8.58579 13.5 9C13.5 9.41421 13.8358 9.75 14.25 9.75Z" stroke="black" strokeWidth="1.125" strokeLinecap="round" strokeLinejoin="round" />
              <path d="M3.75 9.75C4.16421 9.75 4.5 9.41421 4.5 9C4.5 8.58579 4.16421 8.25 3.75 8.25C3.33579 8.25 3 8.58579 3 9C3 9.41421 3.33579 9.75 3.75 9.75Z" stroke="black" strokeWidth="1.125" strokeLinecap="round" strokeLinejoin="round" />
            </svg>
          </button>
          <div className="absolute right-0 top-8 bg-white border border-gray-200 rounded-lg shadow-lg py-2 w-40 z-10 hidden group-hover:block">
            <button 
              onClick={() => handleViewReport(session.session_id)}
              className="w-full text-left px-4 py-2 hover:bg-gray-100 text-sm"
            >
              View Report
            </button>
            <button 
              onClick={() => handleDeleteSession(session.session_id)}
              className="w-full text-left px-4 py-2 hover:bg-gray-100 text-sm text-red-600"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
      
      <div className="flex items-center gap-2">
        <span className="w-2 h-2 rounded-full bg-[#12B76A]"></span>
        <p className="text-xs text-[#667085]">
          Complete · Created {dashboardApi.formatDate(session.created_at)}
        </p>
        <span className="text-xs text-[#667085]">
          · {session.total_queries} question{session.total_queries !== 1 ? 's' : ''}
        </span>
      </div>
    </div>
  );

  if (loading) {
    return (
      <main className="flex-1 p-[12px] w-[1210px] h-[963px] bg-[#F7F8FC] overflow-y-auto">
        <div className="flex justify-center items-center h-full">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading dashboard...</p>
          </div>
        </div>
      </main>
    );
  }

  if (error) {
    return (
      <main className="flex-1 p-[12px] w-[1210px] h-[963px] bg-[#F7F8FC] overflow-y-auto">
        <div className="flex justify-center items-center h-full">
          <div className="text-center">
            <p className="text-red-600 mb-4">{error}</p>
            <button 
              onClick={loadDashboardData}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              Retry
            </button>
          </div>
        </div>
      </main>
    );
  }

  const filteredDrafts = filteredAndSortedSessions(dashboardData?.drafts || []);
  const filteredCompleted = filteredAndSortedSessions(dashboardData?.completed || []);

  return (
    <main className="flex-1 p-[12px] w-[1210px] h-[963px] bg-[#F7F8FC] overflow-y-auto">
      
      {/* Stats Section */}
      <div className="mb-6 grid grid-cols-4 gap-4">
        <div className="bg-white rounded-lg border border-[#EAECF0] p-4">
          <h3 className="text-2xl font-bold text-[#101828]">{dashboardData?.stats.draft_count || 0}</h3>
          <p className="text-sm text-[#667085]">Draft Sessions</p>
        </div>
        <div className="bg-white rounded-lg border border-[#EAECF0] p-4">
          <h3 className="text-2xl font-bold text-[#101828]">{dashboardData?.stats.completed_count || 0}</h3>
          <p className="text-sm text-[#667085]">Completed Reports</p>
        </div>
        <div className="bg-white rounded-lg border border-[#EAECF0] p-4">
          <h3 className="text-2xl font-bold text-[#101828]">{dashboardData?.stats.total_queries || 0}</h3>
          <p className="text-sm text-[#667085]">Total Questions</p>
        </div>
        <div className="bg-white rounded-lg border border-[#EAECF0] p-4">
          <h3 className="text-2xl font-bold text-[#101828]">{dashboardData?.stats.total_sessions || 0}</h3>
          <p className="text-sm text-[#667085]">Total Sessions</p>
        </div>
      </div>

      {/* Drafts Section */}
      <div className="flex flex-col gap-2 mb-6">
        <div className="flex justify-between items-center">
          <h1 className="text-left font-semibold">Drafts ({filteredDrafts.length})</h1>
          <button 
            onClick={() => navigate('/research')}
            className="px-4 py-2 bg-blue-500 text-white text-sm rounded hover:bg-blue-600"
          >
            + New Research
          </button>
        </div>

        {filteredDrafts.length === 0 ? (
          <div className="bg-white rounded-lg border border-[#EAECF0] p-8 text-center">
            <p className="text-[#667085]">No draft sessions found. Start a new research session to see it here.</p>
          </div>
        ) : (
          <div className="flex gap-4 flex-wrap">
            {filteredDrafts.slice(0, 3).map((session) => (
              <DraftCard key={session.session_id} session={session} />
            ))}
          </div>
        )}
      </div>

      {/* Reports Section */}
      <div className="flex flex-col gap-1">
        <h1 className="text-left font-semibold">Reports ({filteredCompleted.length})</h1>

        <div className="w-[1162px] h-[44px]">
          <div className="flex gap-4 mt-2 mb-4">
            <div className="relative max-w-sm">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 18 18" fill="none">
                  <path d="M15.75 15.75L12.495 12.495M14.25 8.25C14.25 11.5637 11.5637 14.25 8.25 14.25C4.93629 14.25 2.25 11.5637 2.25 8.25C2.25 4.93629 4.93629 2.25 8.25 2.25C11.5637 2.25 14.25 4.93629 14.25 8.25Z" stroke="black" strokeWidth="1.125" strokeLinecap="round" strokeLinejoin="round" />
                </svg>
              </div>
              <input
                type="text"
                className="w-[200px] h-9 pl-10 border border-[#D0D5DD] rounded-lg bg-white text-sm text-[#344054]"
                placeholder="Search"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            <CustomDatePicker />

            <button
              onClick={() => setSortOrder(sortOrder === 'newest' ? 'oldest' : 'newest')}
              className="h-9 w-[200px] px-3 bg-white border border-[#D0D5DD] rounded-lg text-sm text-[#344054] inline-flex items-center hover:bg-blue-200"
              type="button"
            >
              <span className="flex items-center gap-2">
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="18"
                  height="18"
                  viewBox="0 0 18 18"
                  fill="none"
                >
                  <path
                    d="M2.25 12L5.25 15M5.25 15L8.25 12M5.25 15V3M15.75 6L12.75 3M12.75 3L9.75 6M12.75 3V15"
                    stroke="black"
                    strokeWidth="1.35"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                </svg>
                {sortOrder === 'newest' ? 'Newest first' : 'Oldest first'}
              </span>
            </button>
          </div>
        </div>

        <div className="flex flex-col gap-4">
          {filteredCompleted.length === 0 ? (
            <div className="bg-white rounded-lg border border-[#EAECF0] p-8 text-center">
              <p className="text-[#667085]">No completed reports found. Complete a research session to see reports here.</p>
            </div>
          ) : (
            filteredCompleted.map((session) => (
              <CompletedCard key={session.session_id} session={session} />
            ))
          )}
        </div>
      </div>
    </main>
  );
};

export default DynamicDashboard;
