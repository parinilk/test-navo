/**
 * Dashboard API service for Navo Frontend
 * Handles communication with the dashboard endpoints
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export interface ResearchSessionSummary {
  session_id: string;
  title: string;
  status: string;
  created_at: string;
  updated_at: string;
  last_activity: string;
  total_queries: number;
  report_generated: boolean;
  queries_preview: Array<{
    query: string;
    timestamp: string;
  }>;
}

export interface DashboardStats {
  draft_count: number;
  completed_count: number;
  total_queries: number;
  total_sessions: number;
}

export interface DashboardData {
  drafts: ResearchSessionSummary[];
  completed: ResearchSessionSummary[];
  stats: DashboardStats;
}

class DashboardApiService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = API_BASE_URL;
  }

  /**
   * Get complete dashboard data (drafts, completed, and stats)
   */
  async getDashboardData(userId?: string, draftLimit = 10, completedLimit = 10): Promise<DashboardData> {
    try {
      const params = new URLSearchParams();
      if (userId) params.append('user_id', userId);
      params.append('draft_limit', draftLimit.toString());
      params.append('completed_limit', completedLimit.toString());

      const response = await fetch(`${this.baseUrl}/dashboard/?${params}`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch dashboard data: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      // Return empty data structure on error
      return {
        drafts: [],
        completed: [],
        stats: {
          draft_count: 0,
          completed_count: 0,
          total_queries: 0,
          total_sessions: 0
        }
      };
    }
  }

  /**
   * Get dashboard statistics
   */
  async getDashboardStats(userId?: string): Promise<DashboardStats> {
    try {
      const params = new URLSearchParams();
      if (userId) params.append('user_id', userId);

      const response = await fetch(`${this.baseUrl}/dashboard/stats?${params}`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch dashboard stats: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
      return {
        draft_count: 0,
        completed_count: 0,
        total_queries: 0,
        total_sessions: 0
      };
    }
  }

  /**
   * Get draft research sessions
   */
  async getDraftSessions(userId?: string, limit = 20): Promise<ResearchSessionSummary[]> {
    try {
      const params = new URLSearchParams();
      if (userId) params.append('user_id', userId);
      params.append('limit', limit.toString());

      const response = await fetch(`${this.baseUrl}/dashboard/drafts?${params}`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch draft sessions: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching draft sessions:', error);
      return [];
    }
  }

  /**
   * Get completed research sessions
   */
  async getCompletedSessions(userId?: string, limit = 20): Promise<ResearchSessionSummary[]> {
    try {
      const params = new URLSearchParams();
      if (userId) params.append('user_id', userId);
      params.append('limit', limit.toString());

      const response = await fetch(`${this.baseUrl}/dashboard/completed?${params}`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch completed sessions: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching completed sessions:', error);
      return [];
    }
  }

  /**
   * Delete a research session
   */
  async deleteSession(sessionId: string, userId?: string): Promise<boolean> {
    try {
      const params = new URLSearchParams();
      if (userId) params.append('user_id', userId);

      const response = await fetch(`${this.baseUrl}/dashboard/sessions/${sessionId}?${params}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error(`Failed to delete session: ${response.statusText}`);
      }

      return true;
    } catch (error) {
      console.error('Error deleting session:', error);
      return false;
    }
  }

  /**
   * Update session status
   */
  async updateSessionStatus(sessionId: string, status: 'draft' | 'completed' | 'archived', reportData?: any): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/dashboard/sessions/${sessionId}/status`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          status,
          report_data: reportData
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to update session status: ${response.statusText}`);
      }

      return true;
    } catch (error) {
      console.error('Error updating session status:', error);
      return false;
    }
  }

  /**
   * Create a new research session
   */
  async createSession(title: string, userId?: string): Promise<{ session_id: string; title: string; status: string } | null> {
    try {
      const response = await fetch(`${this.baseUrl}/dashboard/sessions`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title,
          user_id: userId
        }),
      });

      if (!response.ok) {
        throw new Error(`Failed to create session: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error creating session:', error);
      return null;
    }
  }

  /**
   * Get detailed information about a specific research session
   */
  async getSessionDetails(sessionId: string): Promise<any> {
    try {
      const response = await fetch(`${this.baseUrl}/dashboard/sessions/${sessionId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`Failed to get session details: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting session details:', error);
      throw error;
    }
  }

  /**
   * Format date for display
   */
  formatDate(dateString: string): string {
    try {
      const date = new Date(dateString);
      const now = new Date();
      const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));

      if (diffInHours < 1) {
        return 'Just now';
      } else if (diffInHours < 24) {
        return `${diffInHours}h ago`;
      } else if (diffInHours < 48) {
        return 'Yesterday';
      } else {
        const diffInDays = Math.floor(diffInHours / 24);
        return `${diffInDays} days ago`;
      }
    } catch (error) {
      return 'Unknown';
    }
  }

  /**
   * Get status badge color
   */
  getStatusColor(status: string): string {
    switch (status.toLowerCase()) {
      case 'draft':
        return 'text-orange-400 bg-orange-50';
      case 'completed':
        return 'text-green-400 bg-green-50';
      case 'archived':
        return 'text-gray-400 bg-gray-50';
      default:
        return 'text-gray-400 bg-gray-50';
    }
  }

  /**
   * Get status display text
   */
  getStatusText(status: string): string {
    switch (status.toLowerCase()) {
      case 'draft':
        return 'In progress';
      case 'completed':
        return 'Completed';
      case 'archived':
        return 'Archived';
      default:
        return status;
    }
  }
}

// Export the service instance
export const dashboardApi = new DashboardApiService();
export default dashboardApi;

// Re-export types for easier importing
export type { DashboardData, ResearchSessionSummary, DashboardStats };
