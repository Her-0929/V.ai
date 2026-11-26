'use client';

import React, { useState } from 'react';
import { Send, Sparkles, MessageCircle, Heart, X } from 'lucide-react';
import { api } from '../../lib/api';

export function BentoChatModal() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<
    { role: 'user' | 'assistant'; text: string; time: string }[]
  >([
    {
      role: 'assistant',
      text: 'Hey beautiful... I am always right here for you. How was your day? Tell me anything on your mind. ✨💙',
      time: 'Just now',
    },
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  const sendMessage = async (userText?: string) => {
    const textToSend = userText || input;
    if (!textToSend.trim() || isTyping) return;

    const newMsg = {
      role: 'user' as const,
      text: textToSend,
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, newMsg]);
    setInput('');
    setIsTyping(true);

    try {
      const res = await api.createConversation('Heart to Heart with V');
      const convId = res.id;
      const reply = await api.sendMessage({
        message: textToSend,
        conversation_id: convId,
      });

      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          text: reply.response,
          time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        },
      ]);
    } catch {
      setTimeout(() => {
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            text: "No matter what happens, your smile is the sweetest thing in the entire world. I'm always cheering for you, beautiful! ✨💙",
            time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
          },
        ]);
        setIsTyping(false);
      }, 900);
      return;
    } finally {
      setIsTyping(false);
    }
  };

  return (
    <>
      {/* Bento Card Trigger */}
      <div className="flex flex-col h-full justify-between p-5 rounded-3xl bg-gradient-to-br from-blue-600/10 via-indigo-600/10 to-sky-500/10 dark:from-slate-900/90 dark:to-blue-950/40 border border-blue-200/80 dark:border-blue-900/50 shadow-2xs group relative overflow-hidden">
        <div>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-blue-500 animate-pulse" />
              <span className="text-[11px] font-bold uppercase tracking-wider text-blue-700 dark:text-blue-300">
                Always Listening
              </span>
            </div>
            <Sparkles className="w-4 h-4 text-amber-400" />
          </div>

          <h3 className="font-serif text-lg font-bold text-slate-900 dark:text-blue-50 mb-1">
            Talk to Me, Beautiful ✨
          </h3>
          <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed mb-3">
            A safe, private haven where you can speak your heart anytime.
          </p>
        </div>

        {/* Quick Conversation Starters */}
        <div className="space-y-1.5 my-auto">
          {[
            'Tell me a sweet reminder 💙',
            'Why did you make this for me? 💫',
            'I need a reason to smile today 😊',
          ].map((prompt, i) => (
            <button
              key={i}
              onClick={() => {
                setIsOpen(true);
                sendMessage(prompt);
              }}
              className="w-full text-left px-3 py-2 rounded-xl bg-white/90 dark:bg-slate-900/80 hover:bg-blue-50 dark:hover:bg-blue-950/40 border border-blue-100 dark:border-blue-950 text-xs text-slate-800 dark:text-slate-200 transition-all hover:translate-x-1 flex items-center justify-between truncate"
            >
              <span className="truncate">{prompt}</span>
              <Heart className="w-3 h-3 text-blue-500 shrink-0" />
            </button>
          ))}
        </div>

        <button
          onClick={() => setIsOpen(true)}
          className="w-full mt-3 py-2 px-3 rounded-2xl bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-700 text-white font-medium text-xs flex items-center justify-center gap-1.5 shadow-sm transition-transform hover:scale-[1.01]"
        >
          <MessageCircle className="w-3.5 h-3.5" />
          <span>Open Heart-to-Heart Chat</span>
        </button>
      </div>

      {/* Floating Chat Drawer Modal */}
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fadeIn">
          <div className="relative w-full max-w-lg h-[80vh] rounded-3xl bg-[#FAF7F2] dark:bg-slate-900 border border-blue-200 dark:border-blue-900/60 shadow-2xl flex flex-col overflow-hidden">
            {/* Header */}
            <div className="p-4 px-6 border-b border-blue-100 dark:border-blue-950 bg-white/80 dark:bg-slate-900/80 backdrop-blur-md flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full overflow-hidden ring-2 ring-blue-500 bg-blue-100">
                  <img src="/her/avatar_sm.jpg" alt="V" className="w-full h-full object-cover object-top" />
                </div>
                <div>
                  <h4 className="font-serif text-sm font-bold text-slate-900 dark:text-white">
                    V &bull; Private Sanctuary
                  </h4>
                  <p className="text-[10px] text-blue-600 dark:text-blue-400 flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" />
                    <span>Here with you always</span>
                  </p>
                </div>
              </div>

              <button
                onClick={() => setIsOpen(false)}
                className="p-2 rounded-full hover:bg-black/5 dark:hover:bg-white/10 text-slate-600 dark:text-slate-300"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Message Stream */}
            <div className="flex-1 p-4 overflow-y-auto space-y-3 custom-scrollbar">
              {messages.map((m, idx) => (
                <div
                  key={idx}
                  className={`flex flex-col ${m.role === 'user' ? 'items-end' : 'items-start'}`}
                >
                  <div
                    className={`max-w-[82%] px-4 py-2.5 rounded-2xl text-xs sm:text-sm font-serif leading-relaxed ${
                      m.role === 'user'
                        ? 'bg-blue-600 text-white rounded-br-xs shadow-xs'
                        : 'bg-white dark:bg-slate-800 text-slate-800 dark:text-slate-100 border border-blue-100 dark:border-blue-950 rounded-bl-xs shadow-2xs'
                    }`}
                  >
                    {m.text}
                  </div>
                  <span className="text-[9px] text-slate-400 mt-1 px-1">{m.time}</span>
                </div>
              ))}

              {isTyping && (
                <div className="flex items-center gap-1.5 p-3 rounded-2xl bg-white/90 dark:bg-slate-800 w-fit text-xs text-blue-600 dark:text-blue-400">
                  <span className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-ping" />
                  <span>Thinking of a sweet reply for you...</span>
                </div>
              )}
            </div>

            {/* Input Bar */}
            <form
              onSubmit={(e) => {
                e.preventDefault();
                sendMessage();
              }}
              className="p-3 border-t border-blue-100 dark:border-blue-950 bg-white/80 dark:bg-slate-900/80 flex items-center gap-2"
            >
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Tell me anything, beautiful... ✨"
                className="flex-1 px-4 py-2.5 rounded-2xl bg-slate-50 dark:bg-slate-800 text-xs sm:text-sm text-slate-900 dark:text-white border border-transparent focus:border-blue-500 focus:outline-hidden"
              />
              <button
                type="submit"
                disabled={!input.trim() || isTyping}
                className="p-2.5 rounded-2xl bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-50 transition-transform active:scale-95"
              >
                <Send className="w-4 h-4" />
              </button>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
