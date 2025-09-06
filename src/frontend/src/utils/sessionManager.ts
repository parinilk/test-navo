/**
 * Session Manager for Navo Frontend
 * Handles session ID generation and persistence across the application
 */

export class SessionManager {
  private static instance: SessionManager;
  private sessionId: string | null = null;
  private readonly SESSION_KEY = 'navo_session_id';
  private readonly CONTEXT_KEY = 'navo_research_context';

  private constructor() {
    this.loadSession();
  }

  public static getInstance(): SessionManager {
    if (!SessionManager.instance) {
      SessionManager.instance = new SessionManager();
    }
    return SessionManager.instance;
  }

  /**
   * Get or create a session ID
   */
  public getSessionId(): string {
    if (!this.sessionId) {
      this.sessionId = this.generateSessionId();
      this.saveSession();
    }
    return this.sessionId;
  }

  /**
   * Get the current session ID without creating a new one
   */
  public getCurrentSessionId(): string | null {
    return this.sessionId;
  }

  /**
   * Start a new session (clears current session)
   */
  public startNewSession(): string {
    this.sessionId = this.generateSessionId();
    this.saveSession();
    this.clearContext();
    return this.sessionId;
  }

  /**
   * Save research context for the session
   */
  public saveContext(context: {
    role: string;
    objective: string;
    topic: string;
  }): void {
    localStorage.setItem(this.CONTEXT_KEY, JSON.stringify(context));
  }

  /**
   * Get research context for the session
   */
  public getContext(): {
    role: string;
    objective: string;
    topic: string;
  } | null {
    try {
      const context = localStorage.getItem(this.CONTEXT_KEY);
      return context ? JSON.parse(context) : null;
    } catch (e) {
      console.error('Failed to parse research context:', e);
      return null;
    }
  }

  /**
   * Clear the current session and context
   */
  public clearSession(): void {
    this.sessionId = null;
    localStorage.removeItem(this.SESSION_KEY);
    this.clearContext();
  }

  /**
   * Clear only the context
   */
  public clearContext(): void {
    localStorage.removeItem(this.CONTEXT_KEY);
  }

  /**
   * Generate a new session ID
   */
  private generateSessionId(): string {
    return `navo_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }

  /**
   * Load session from localStorage
   */
  private loadSession(): void {
    try {
      const savedSessionId = localStorage.getItem(this.SESSION_KEY);
      if (savedSessionId) {
        this.sessionId = savedSessionId;
      }
    } catch (e) {
      console.error('Failed to load session:', e);
    }
  }

  /**
   * Save session to localStorage
   */
  private saveSession(): void {
    if (this.sessionId) {
      localStorage.setItem(this.SESSION_KEY, this.sessionId);
    }
  }

  /**
   * Get session info for debugging
   */
  public getSessionInfo(): {
    sessionId: string | null;
    hasContext: boolean;
    context: any;
  } {
    return {
      sessionId: this.sessionId,
      hasContext: !!this.getContext(),
      context: this.getContext()
    };
  }
}

// Export singleton instance
export const sessionManager = SessionManager.getInstance();
