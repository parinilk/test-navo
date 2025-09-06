/**
 * Test script for conversation state manager
 * This can be run in the browser console to test the functionality
 */

import { conversationStateManager } from './conversationStateManager';

export const testConversationState = () => {
  console.log('🧪 Testing Conversation State Manager...');
  
  // Test 1: Initialize Question 1 with research result
  const mockResearchResult = {
    query: "How does hyaluronic acid work?",
    answer: "Hyaluronic acid works as a humectant...",
    rationale: "Based on scientific research...",
    sources_used: ["source1", "source2"],
    session_id: "test-session-123",
    timestamp: new Date().toISOString(),
    retrieved_products: []
  };
  
  conversationStateManager.initializeQuestion(1, mockResearchResult);
  console.log('✅ Question 1 initialized with research result');
  
  // Test 2: Add a new message to Question 1
  conversationStateManager.addMessage(1, {
    sender: "User",
    text: "Can you tell me more about molecular weights?"
  });
  console.log('✅ Added user message to Question 1');
  
  // Test 3: Initialize Question 2 (should be fresh)
  conversationStateManager.initializeQuestion(2);
  console.log('✅ Question 2 initialized with default messages');
  
  // Test 4: Add messages to Question 2
  conversationStateManager.addMessage(2, {
    sender: "User",
    text: "What about Question 2?"
  });
  conversationStateManager.addMessage(2, {
    sender: "LLM",
    text: "This is a response for Question 2"
  });
  console.log('✅ Added conversation to Question 2');
  
  // Test 5: Check Question 1 still has its conversation
  const question1Messages = conversationStateManager.getMessages(1);
  console.log('📝 Question 1 messages:', question1Messages.length, 'messages');
  
  // Test 6: Check Question 2 has its conversation
  const question2Messages = conversationStateManager.getMessages(2);
  console.log('📝 Question 2 messages:', question2Messages.length, 'messages');
  
  // Test 7: Check conversation summary
  const summary = conversationStateManager.getConversationSummary();
  console.log('📊 Conversation summary:', summary);
  
  // Test 8: Test Question 3 (should be fresh)
  conversationStateManager.initializeQuestion(3);
  const question3Messages = conversationStateManager.getMessages(3);
  console.log('📝 Question 3 messages (fresh):', question3Messages.length, 'messages');
  
  console.log('🎉 All tests completed!');
  
  return {
    question1Messages,
    question2Messages,
    question3Messages,
    summary
  };
};

// Export for use in browser console
if (typeof window !== 'undefined') {
  (window as any).testConversationState = testConversationState;
}
