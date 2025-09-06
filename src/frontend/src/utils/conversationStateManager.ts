/**
 * Conversation State Manager - Manages conversation state for each question tab
 */

interface Message {
  sender: "User" | "LLM";
  text: string;
}

interface QuestionConversation {
  questionNumber: number;
  messages: Message[];
  lastUpdated: string;
}

interface ConversationState {
  [questionNumber: number]: QuestionConversation;
}

export class ConversationStateManager {
  private static instance: ConversationStateManager;
  private storageKey = 'navo_conversation_state';
  private state: ConversationState = {};

  private constructor() {
    this.loadState();
  }

  static getInstance(): ConversationStateManager {
    if (!ConversationStateManager.instance) {
      ConversationStateManager.instance = new ConversationStateManager();
    }
    return ConversationStateManager.instance;
  }

  /**
   * Initialize conversation for a question with default messages
   */
  initializeQuestion(questionNumber: number, researchResult?: any): void {
    if (this.state[questionNumber]) {
      return; // Already initialized
    }

    const defaultMessages: Message[] = researchResult ? [
      { sender: "User", text: researchResult.query },
      { sender: "LLM", text: researchResult.answer }
    ] : [
      { sender: "User", text: "What is the rationale behind this?" },
      { sender: "LLM", text: "Here's the detailed reasoning..." }
    ];

    this.state[questionNumber] = {
      questionNumber,
      messages: defaultMessages,
      lastUpdated: new Date().toISOString()
    };

    this.saveState();
  }

  /**
   * Get messages for a specific question
   */
  getMessages(questionNumber: number): Message[] {
    if (!this.state[questionNumber]) {
      this.initializeQuestion(questionNumber);
    }
    return this.state[questionNumber].messages;
  }

  /**
   * Update messages for a specific question
   */
  updateMessages(questionNumber: number, messages: Message[]): void {
    if (!this.state[questionNumber]) {
      this.initializeQuestion(questionNumber);
    }

    this.state[questionNumber] = {
      ...this.state[questionNumber],
      messages,
      lastUpdated: new Date().toISOString()
    };

    this.saveState();
  }

  /**
   * Add a new message to a question's conversation
   */
  addMessage(questionNumber: number, message: Message): void {
    if (!this.state[questionNumber]) {
      this.initializeQuestion(questionNumber);
    }

    this.state[questionNumber].messages.push(message);
    this.state[questionNumber].lastUpdated = new Date().toISOString();
    this.saveState();
  }

  /**
   * Clear conversation for a specific question
   */
  clearQuestion(questionNumber: number): void {
    if (this.state[questionNumber]) {
      delete this.state[questionNumber];
      this.saveState();
    }
  }

  /**
   * Clear all conversations
   */
  clearAll(): void {
    this.state = {};
    this.saveState();
  }

  /**
   * Check if a question has any conversation history
   */
  hasConversation(questionNumber: number): boolean {
    return this.state[questionNumber] && this.state[questionNumber].messages.length > 0;
  }

  /**
   * Get conversation summary for all questions
   */
  getConversationSummary(): { questionNumber: number; messageCount: number; lastUpdated: string }[] {
    return Object.values(this.state).map(conv => ({
      questionNumber: conv.questionNumber,
      messageCount: conv.messages.length,
      lastUpdated: conv.lastUpdated
    }));
  }

  /**
   * Load state from localStorage
   */
  private loadState(): void {
    try {
      const data = localStorage.getItem(this.storageKey);
      if (data) {
        this.state = JSON.parse(data);
      }
    } catch (error) {
      console.error('Error loading conversation state:', error);
      this.state = {};
    }
  }

  /**
   * Save state to localStorage
   */
  private saveState(): void {
    try {
      localStorage.setItem(this.storageKey, JSON.stringify(this.state));
    } catch (error) {
      console.error('Error saving conversation state:', error);
    }
  }
}

// Export singleton instance
export const conversationStateManager = ConversationStateManager.getInstance();
