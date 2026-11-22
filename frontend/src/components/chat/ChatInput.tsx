'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Sparkles } from 'lucide-react';

interface ChatInputProps {
  onSendMessage: (content: string) => Promise<void>;
  isLoading: boolean;
}

export function ChatInput({ onSendMessage, isLoading }: ChatInputProps) {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(
        textareaRef.current.scrollHeight,
        180
      )}px`;
    }
  }, [input]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    const msg = input.trim();
    setInput('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
    await onSendMessage(msg);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <div className="w-full max-w-3xl mx-auto px-4 pb-5 pt-2">
      <form
        onSubmit={handleSubmit}
        className="relative flex items-end rounded-3xl bg-white dark:bg-[#221F1D] border border-[#E2D8CC] dark:border-[#38332E] shadow-sm focus-within:border-[#D96B43] focus-within:ring-2 focus-within:ring-[#D96B43]/20 transition-all p-2 sm:p-2.5"
      >
        <textarea
          ref={textareaRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Talk with HER... (Shift+Enter for newline)"
          rows={1}
          disabled={isLoading}
          className="flex-1 max-h-44 resize-none bg-transparent px-3 py-2 text-sm text-[#2C2623] dark:text-[#F7F3EE] placeholder-[#A39489] focus:outline-hidden leading-relaxed custom-scrollbar"
        />

        <div className="flex items-center gap-1.5 shrink-0 pl-2 pb-1">
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className={`w-9 h-9 rounded-2xl flex items-center justify-center transition-all ${
              input.trim() && !isLoading
                ? 'bg-[#D96B43] text-white hover:bg-[#C55730] shadow-xs cursor-pointer active:scale-95'
                : 'bg-[#F2ECE3] dark:bg-[#2F2B28] text-[#A89C94] cursor-not-allowed'
            }`}
            aria-label="Send message"
          >
            {isLoading ? (
              <Sparkles className="w-4 h-4 animate-spin text-[#D96B43]" />
            ) : (
              <Send className="w-4 h-4" />
            )}
          </button>
        </div>
      </form>
      <div className="mt-2 text-center text-[11px] text-[#A89C94]">
        HER AI personalizes responses using emotional intelligence and long-term memory.
      </div>
    </div>
  );
}
