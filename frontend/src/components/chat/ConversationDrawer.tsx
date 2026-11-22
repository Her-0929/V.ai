'use client';

import React from 'react';
import { Plus, MessageSquare, Trash2, Clock } from 'lucide-react';
import { ConversationResponse } from '../../types/api';
import { formatDate } from '../../lib/utils';

interface ConversationDrawerProps {
  conversations: ConversationResponse[];
  activeId: string | null;
  onSelectConversation: (id: string) => void;
  onNewConversation: () => void;
  onDeleteConversation: (id: string, e: React.MouseEvent) => void;
  isLoading: boolean;
}

export function ConversationDrawer({
  conversations,
  activeId,
  onSelectConversation,
  onNewConversation,
  onDeleteConversation,
  isLoading,
}: ConversationDrawerProps) {
  return (
    <div className="w-72 lg:w-80 h-full border-r border-[#E8DFD5] dark:border-[#2C2926] bg-[#FAF7F2] dark:bg-[#181615] flex flex-col shrink-0">
      {/* Drawer Header */}
      <div className="p-4 border-b border-[#E8DFD5] dark:border-[#2C2926]">
        <button
          onClick={onNewConversation}
          className="w-full flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-white dark:bg-[#272421] border border-[#E8DFD5] dark:border-[#38332E] text-sm font-medium text-[#2C2623] dark:text-[#F7F3EE] hover:border-[#D96B43]/50 hover:bg-[#FAF7F2] transition-all shadow-2xs cursor-pointer group"
        >
          <Plus className="w-4 h-4 text-[#D96B43] group-hover:scale-110 transition-transform" />
          <span>New Conversation</span>
        </button>
      </div>

      {/* Conversations List */}
      <div className="flex-1 overflow-y-auto p-3 space-y-1 custom-scrollbar">
        <div className="px-2 py-1 text-[11px] font-semibold text-[#A39489] uppercase tracking-wider">
          Recent Dialogues ({conversations.length})
        </div>

        {conversations.length === 0 && !isLoading && (
          <div className="p-6 text-center text-xs text-[#9E9086]">
            <Clock className="w-6 h-6 mx-auto mb-2 opacity-40 text-[#D96B43]" />
            <p>No conversations yet.</p>
            <p className="mt-1 opacity-75">Start a fresh conversation with HER.</p>
          </div>
        )}

        {conversations.map((conv) => {
          const isActive = conv.id === activeId;
          return (
            <div
              key={conv.id}
              onClick={() => onSelectConversation(conv.id)}
              className={`group flex items-center justify-between p-2.5 rounded-xl text-xs font-medium cursor-pointer transition-all ${
                isActive
                  ? 'bg-white dark:bg-[#24211E] text-[#D96B43] dark:text-[#EB8D74] border border-[#E8DFD5] dark:border-[#38332E] shadow-2xs'
                  : 'text-[#61554D] dark:text-[#B3A69C] hover:bg-[#EFE8DF]/70 dark:hover:bg-[#23201D]'
              }`}
            >
              <div className="flex items-center gap-2.5 min-w-0 pr-2">
                <MessageSquare
                  className={`w-3.5 h-3.5 shrink-0 ${
                    isActive ? 'text-[#D96B43]' : 'text-[#A39489]'
                  }`}
                />
                <div className="min-w-0">
                  <div className="truncate font-medium">{conv.title || 'Conversation'}</div>
                  <div className="text-[10px] text-[#A39489]">{formatDate(conv.updated_at)}</div>
                </div>
              </div>

              <button
                onClick={(e) => onDeleteConversation(conv.id, e)}
                className="opacity-0 group-hover:opacity-100 p-1 rounded-md text-[#A39489] hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/40 transition-all shrink-0"
                title="Delete dialogue"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
