/**
 * Session Data Manager - Collects research data from all question tabs for comprehensive report generation
 */

interface QuestionResult {
  questionNumber: number;
  query: string;
  answer: string;
  rationale: string;
  sources_used: string[];
  retrieved_products?: any[];
  web_search_results?: any[];
  timestamp: string;
  session_id: string;
}

interface SessionData {
  session_id: string;
  created_at: string;
  updated_at: string;
  question_results: QuestionResult[];
  pinned_insights: string[];
  research_context: {
    role?: string;
    objective?: string;
    topic?: string;
  };
}

export class SessionDataManager {
  private static instance: SessionDataManager;
  private storageKey = 'navo_session_data';

  private constructor() {}

  static getInstance(): SessionDataManager {
    if (!SessionDataManager.instance) {
      SessionDataManager.instance = new SessionDataManager();
    }
    return SessionDataManager.instance;
  }

  /**
   * Initialize a new session or get existing one
   */
  initializeSession(sessionId: string, context?: any): SessionData {
    let sessionData = this.getSessionData();
    
    if (!sessionData || sessionData.session_id !== sessionId) {
      // Create new session
      sessionData = {
        session_id: sessionId,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
        question_results: [],
        pinned_insights: [],
        research_context: context || {}
      };
      this.saveSessionData(sessionData);
    }
    
    return sessionData;
  }

  /**
   * Add research result from a question tab
   */
  addQuestionResult(questionNumber: number, result: any): void {
    const sessionData = this.getSessionData();
    if (!sessionData) {
      console.error('No active session found');
      return;
    }

    // Remove any existing result for this question
    sessionData.question_results = sessionData.question_results.filter(
      r => r.questionNumber !== questionNumber
    );

    // Add new result
    const questionResult: QuestionResult = {
      questionNumber,
      query: result.query || '',
      answer: result.answer || '',
      rationale: result.rationale || '',
      sources_used: result.sources_used || [],
      retrieved_products: result.retrieved_products || [],
      web_search_results: result.web_search_results || [],
      timestamp: result.timestamp || new Date().toISOString(),
      session_id: result.session_id || sessionData.session_id
    };

    sessionData.question_results.push(questionResult);
    sessionData.updated_at = new Date().toISOString();
    
    this.saveSessionData(sessionData);
    console.log(`✅ Stored research result for Question ${questionNumber}`);
  }

  /**
   * Update pinned insights
   */
  updatePinnedInsights(insights: string[]): void {
    const sessionData = this.getSessionData();
    if (!sessionData) {
      console.error('No active session found');
      return;
    }

    sessionData.pinned_insights = insights;
    sessionData.updated_at = new Date().toISOString();
    this.saveSessionData(sessionData);
  }

  /**
   * Get all collected data for report generation
   */
  getReportData(): {
    pinned_insights: string[];
    all_retrieved_products: any[];
    all_web_search_results: any[];
    all_question_results: QuestionResult[];
    research_context: any;
    session_id: string;
  } {
    const sessionData = this.getSessionData();
    if (!sessionData) {
      return {
        pinned_insights: [],
        all_retrieved_products: [],
        all_web_search_results: [],
        all_question_results: [],
        research_context: {},
        session_id: ''
      };
    }

    // Collect all products from all questions
    const all_retrieved_products: any[] = [];
    const all_web_search_results: any[] = [];

    sessionData.question_results.forEach(result => {
      if (result.retrieved_products) {
        all_retrieved_products.push(...result.retrieved_products);
      }
      if (result.web_search_results) {
        all_web_search_results.push(...result.web_search_results);
      }
    });

    return {
      pinned_insights: sessionData.pinned_insights,
      all_retrieved_products,
      all_web_search_results,
      all_question_results: sessionData.question_results,
      research_context: sessionData.research_context,
      session_id: sessionData.session_id
    };
  }

  /**
   * Get session statistics
   */
  getSessionStats(): {
    questionsCompleted: number;
    totalProducts: number;
    totalWebSources: number;
    pinnedInsights: number;
  } {
    const sessionData = this.getSessionData();
    if (!sessionData) {
      return { questionsCompleted: 0, totalProducts: 0, totalWebSources: 0, pinnedInsights: 0 };
    }

    let totalProducts = 0;
    let totalWebSources = 0;

    sessionData.question_results.forEach(result => {
      totalProducts += result.retrieved_products?.length || 0;
      totalWebSources += result.web_search_results?.length || 0;
    });

    return {
      questionsCompleted: sessionData.question_results.length,
      totalProducts,
      totalWebSources,
      pinnedInsights: sessionData.pinned_insights.length
    };
  }

  /**
   * Clear session data
   */
  clearSession(): void {
    localStorage.removeItem(this.storageKey);
  }

  /**
   * Get current session data
   */
  private getSessionData(): SessionData | null {
    try {
      const data = localStorage.getItem(this.storageKey);
      return data ? JSON.parse(data) : null;
    } catch (error) {
      console.error('Error loading session data:', error);
      return null;
    }
  }

  /**
   * Save session data
   */
  private saveSessionData(data: SessionData): void {
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(data));
    } catch (error) {
      console.error('Error saving session data:', error);
    }
  }

  /**
   * Get current session ID
   */
  getCurrentSessionId(): string | null {
    const sessionData = this.getSessionData();
    return sessionData?.session_id || null;
  }

  /**
   * Check if question has been completed
   */
  isQuestionCompleted(questionNumber: number): boolean {
    const sessionData = this.getSessionData();
    if (!sessionData) return false;
    
    return sessionData.question_results.some(r => r.questionNumber === questionNumber);
  }

  /**
   * Get the latest research result for a specific question
   */
  getQuestionResult(questionNumber: number): QuestionResult | null {
    const sessionData = this.getSessionData();
    if (!sessionData) return null;
    
    return sessionData.question_results.find(r => r.questionNumber === questionNumber) || null;
  }
}

// Export singleton instance
export const sessionDataManager = SessionDataManager.getInstance();
