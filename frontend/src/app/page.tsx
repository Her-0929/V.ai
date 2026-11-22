'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { AppLayout } from '../components/layout/AppLayout';
import { MessageBubble } from '../components/chat/MessageBubble';
import { ChatInput } from '../components/chat/ChatInput';
import { ConversationDrawer } from '../components/chat/ConversationDrawer';
import { api } from '../lib/api';
import { ConversationResponse, MessageResponse, RetrievedMemoryInfo } from '../types/api';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { Heart, Sparkles } from 'lucide-react';

export default function ChatPage() {
  const { user, token } = useAuth();
  const { error: toastError, success: toastSuccess } = useToast();

  const [conversations, setConversations] = useState<ConversationResponse[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<MessageResponse[]>([]);
  const [isLoadingMessages, setIsLoadingMessages] = useState<boolean>(false);
  const [isSending, setIsSending] = useState<boolean>(false);
  const [retrievedMemoriesMap, setRetrievedMemoriesMap] = useState<
    Record<string, RetrievedMemoryInfo[]>
  >({});

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isSending]);

  // Load conversations list
  const loadConversations = useCallback(async () => {
    if (!token) return;
    try {
      const data = await api.listConversations();
      setConversations(data.conversations);
      if (data.conversations.length > 0 && !activeConversationId) {
        setActiveConversationId(data.conversations[0].id);
      }
    } catch (err: unknown) {
      console.warn('Failed to load conversations:', err);
    }
  }, [token, activeConversationId]);

  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  // Load messages for active conversation
  const loadActiveMessages = useCallback(async (conversationId: string) => {
    setIsLoadingMessages(true);
    try {
      const data = await api.getConversation(conversationId);
      setMessages(data.messages);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load conversation history.';
      toastError(msg);
    } finally {
      setIsLoadingMessages(false);
    }
  }, [toastError]);

  useEffect(() => {
    if (activeConversationId) {
      loadActiveMessages(activeConversationId);
    } else {
      setMessages([]);
    }
  }, [activeConversationId, loadActiveMessages]);

  // Handle Send Message
  const handleSendMessage = async (text: string) => {
    if (!text.trim()) return;
    setIsSending(true);

    // Optimistic user message preview
    const tempUserId = `temp-${Date.now()}`;
    const optimisticUserMsg: MessageResponse = {
      id: tempUserId,
      conversation_id: activeConversationId || '',
      role: 'user',
      content: text,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, optimisticUserMsg]);

    try {
      const response = await api.sendMessage({
        conversation_id: activeConversationId || undefined,
        message: text,
      });

      // If this was a new conversation, update active ID and conversation list
      if (!activeConversationId) {
        setActiveConversationId(response.conversation_id);
      }

      // Assistant response message
      const assistantMsgId = `assistant-${Date.now()}`;
      const assistantMsg: MessageResponse = {
        id: assistantMsgId,
        conversation_id: response.conversation_id,
        role: 'assistant',
        content: response.response,
        message_metadata: {
          emotional_context: response.emotional_context || undefined,
          memory_count: response.memory_count,
          model: response.model,
          retrieved_memories: response.retrieved_memories,
        },
        created_at: new Date().toISOString(),
      };

      // Store recalled memories in map
      if (response.retrieved_memories?.length) {
        setRetrievedMemoriesMap((prev) => ({
          ...prev,
          [assistantMsgId]: response.retrieved_memories,
        }));
      }

      setMessages((prev) => [...prev, assistantMsg]);

      // Refresh conversations list to update title & timestamp
      loadConversations();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'HER failed to reply.';
      toastError(msg);
      // Remove optimistic message on failure
      setMessages((prev) => prev.filter((m) => m.id !== tempUserId));
    } finally {
      setIsSending(false);
    }
  };

  const handleNewConversation = () => {
    setActiveConversationId(null);
    setMessages([]);
  };

  const handleDeleteConversation = async (id: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm('Are you sure you want to delete this conversation?')) return;
    try {
      await api.deleteConversation(id);
      toastSuccess('Conversation deleted.');
      setConversations((prev) => prev.filter((c) => c.id !== id));
      if (activeConversationId === id) {
        setActiveConversationId(null);
        setMessages([]);
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Could not delete conversation.';
      toastError(msg);
    }
  };

  return (
    <AppLayout>
      <div className="flex-1 flex h-[calc(100vh-4rem)] overflow-hidden">
        {/* Conversation Drawer */}
        <div className="hidden lg:block h-full">
          <ConversationDrawer
            conversations={conversations}
            activeId={activeConversationId}
            onSelectConversation={setActiveConversationId}
            onNewConversation={handleNewConversation}
            onDeleteConversation={handleDeleteConversation}
            isLoading={isLoadingMessages}
          />
        </div>

        {/* Main Chat Stream */}
        <div className="flex-1 flex flex-col h-full bg-[#FAF7F2] dark:bg-[#151413] relative overflow-hidden">
          {/* Messages Viewport */}
          <div className="flex-1 overflow-y-auto px-4 sm:px-6 py-6 custom-scrollbar flex flex-col">
            {messages.length === 0 && !isLoadingMessages ? (
              // Empty State / Companion Welcome
              <div className="flex-1 flex flex-col items-center justify-center max-w-xl mx-auto text-center px-4 py-12 animate-fadeIn">
                <div className="w-16 h-16 rounded-3xl bg-[#E07A5F] flex items-center justify-center text-white shadow-lg shadow-[#E07A5F]/20 mb-6">
                  <Heart className="w-8 h-8 fill-white/80" />
                </div>
                <h2 className="font-serif text-2xl sm:text-3xl font-medium text-[#2C2623] dark:text-[#F7F3EE] mb-3">
                  I&apos;m here, {user?.username || 'friend'}.
                </h2>
                <p className="text-sm text-[#7C6E64] dark:text-[#A89C94] leading-relaxed mb-8 max-w-md">
                  I carry your memories, personal notes, and timeline. What is on your mind today?
                </p>

                {/* Empathetic Starter Prompts */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full text-left">
                  {[
                    'When did we first meet or talk?',
                    'What career goals have I shared with you?',
                    'What do you remember from my uploaded notes?',
                    'How are you feeling right now?',
                  ].map((starter, idx) => (
                    <button
                      key={idx}
                      onClick={() => handleSendMessage(starter)}
                      className="p-3.5 rounded-2xl bg-white dark:bg-[#201D1B] border border-[#E8DFD5] dark:border-[#332E2A] hover:border-[#D96B43]/50 hover:bg-[#FAF7F2] dark:hover:bg-[#272421] text-xs text-[#4A4039] dark:text-[#D1C6BD] font-medium transition-all shadow-2xs text-left cursor-pointer group flex items-start gap-2.5"
                    >
                      <Sparkles className="w-3.5 h-3.5 text-[#D96B43] shrink-0 mt-0.5 group-hover:scale-110 transition-transform" />
                      <span>{starter}</span>
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              // Chat Messages
              <div className="max-w-3xl w-full mx-auto flex flex-col">
                {messages.map((msg) => (
                  <MessageBubble
                    key={msg.id}
                    message={msg}
                    retrievedMemories={retrievedMemoriesMap[msg.id]}
                  />
                ))}

                {isSending && (
                  <div className="flex gap-3.5 self-start mb-6">
                    <div className="w-9 h-9 rounded-2xl bg-[#E07A5F] flex items-center justify-center text-white shrink-0 shadow-2xs">
                      <Heart className="w-4 h-4 fill-white/80 animate-pulse" />
                    </div>
                    <div className="p-4 rounded-3xl bg-white dark:bg-[#221F1D] border border-[#EAE2D8] dark:border-[#38332E] shadow-2xs flex items-center gap-2 text-xs text-[#7C6E64] dark:text-[#A89C94]">
                      <span className="w-1.5 h-1.5 rounded-full bg-[#D96B43] animate-bounce" />
                      <span
                        className="w-1.5 h-1.5 rounded-full bg-[#D96B43] animate-bounce"
                        style={{ animationDelay: '0.15s' }}
                      />
                      <span
                        className="w-1.5 h-1.5 rounded-full bg-[#D96B43] animate-bounce"
                        style={{ animationDelay: '0.3s' }}
                      />
                      <span className="ml-1 font-medium">HER is reflecting and recalling...</span>
                    </div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          {/* Input Bar */}
          <ChatInput onSendMessage={handleSendMessage} isLoading={isSending} />
        </div>
      </div>
    </AppLayout>
  );
}
