'use client';

import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import {
  User,
  Sparkles,
  ChevronDown,
  ChevronUp,
  Brain,
  Calendar,
} from 'lucide-react';
import { MessageResponse, RetrievedMemoryInfo } from '../../types/api';
import { Badge } from '../ui/Badge';
import { getEmotionColor, formatPrecision } from '../../lib/utils';
import { HER_COMPANION } from '../../lib/herData';

interface MessageBubbleProps {
  message: MessageResponse;
  retrievedMemories?: RetrievedMemoryInfo[];
}

export function MessageBubble({ message, retrievedMemories }: MessageBubbleProps) {
  const isAssistant = message.role === 'assistant';
  const [showMemories, setShowMemories] = useState(false);

  // Extract metadata if available
  const meta = message.message_metadata;
  const emotionalContext = meta?.emotional_context;
  const memories = retrievedMemories || (meta?.retrieved_memories as RetrievedMemoryInfo[]) || [];
  const memoryCount = meta?.memory_count ?? memories.length;

  const emotionColors = emotionalContext ? getEmotionColor(emotionalContext.emotion) : null;

  return (
    <div
      className={`group flex gap-3.5 mb-6 max-w-3xl w-full ${
        isAssistant ? 'self-start' : 'self-end flex-row-reverse'
      }`}
    >
      {/* Avatar */}
      {isAssistant ? (
        <div className="relative w-9 h-9 rounded-2xl overflow-hidden shrink-0 shadow-2xs ring-2 ring-[#E07A5F]/30 bg-[#E07A5F] group-hover:ring-[#D96B43] transition-all">
          <img
            src={HER_COMPANION.avatarSm}
            alt={HER_COMPANION.name}
            className="w-full h-full object-cover object-top"
          />
          <span className="absolute bottom-0 right-0 w-2 h-2 rounded-full bg-emerald-500 ring-1.5 ring-white dark:ring-[#221F1D]" />
        </div>
      ) : (
        <div className="w-9 h-9 rounded-2xl flex items-center justify-center shrink-0 shadow-2xs bg-[#EFE7DC] dark:bg-[#38332E] text-[#6B5E57] dark:text-[#EAE3DC]">
          <User className="w-4 h-4" />
        </div>
      )}

      {/* Message Content Container */}
      <div className={`flex flex-col min-w-0 ${isAssistant ? 'items-start' : 'items-end'}`}>
        {/* Name and Emotional Context Pill */}
        <div className="flex items-center gap-2 mb-1.5 px-1">
          <span className="text-xs font-medium text-[#7C6E64] dark:text-[#A89C94]">
            {isAssistant ? 'HER' : 'You'}
          </span>

          {isAssistant && emotionalContext && emotionColors && (
            <span
              className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium border ${emotionColors.bg} ${emotionColors.text} ${emotionColors.border}`}
              title={`Confidence: ${(emotionalContext.confidence * 100).toFixed(0)}%`}
            >
              <span className={`w-1.5 h-1.5 rounded-full ${emotionColors.dot}`} />
              <span className="capitalize">{emotionalContext.emotion.toLowerCase()}</span>
              {emotionalContext.intensity && (
                <span className="opacity-75">({emotionalContext.intensity.toLowerCase()})</span>
              )}
            </span>
          )}

          {isAssistant && memoryCount > 0 && (
            <button
              onClick={() => setShowMemories(!showMemories)}
              className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-medium bg-[#FAF2EB] dark:bg-[#2C211A] text-[#D96B43] dark:text-[#EB8D74] border border-[#F3C4B3]/60 dark:border-[#52342A] hover:bg-[#F5E4D7] transition-colors cursor-pointer"
            >
              <Sparkles className="w-2.5 h-2.5" />
              <span>{memoryCount} {memoryCount === 1 ? 'memory recalled' : 'memories recalled'}</span>
              {showMemories ? <ChevronUp className="w-2.5 h-2.5" /> : <ChevronDown className="w-2.5 h-2.5" />}
            </button>
          )}
        </div>

        {/* Bubble */}
        <div
          className={`p-4 sm:p-5 rounded-2xl sm:rounded-3xl shadow-xs transition-colors leading-relaxed ${
            isAssistant
              ? 'bg-white dark:bg-[#221F1D] border border-[#EAE2D8] dark:border-[#38332E] text-[#2C2623] dark:text-[#F7F3EE]'
              : 'bg-[#F1E8DC] dark:bg-[#342F2B] text-[#2C2623] dark:text-[#F7F3EE] rounded-tr-sm sm:rounded-tr-sm'
          }`}
        >
          <div className="prose prose-stone dark:prose-invert prose-sm max-w-none break-words">
            <ReactMarkdown>{message.content}</ReactMarkdown>
          </div>
        </div>

        {/* Collapsible RAG Grounded Memories Accordion */}
        {isAssistant && showMemories && memories.length > 0 && (
          <div className="mt-3 w-full p-3.5 rounded-2xl bg-[#F7F2EC] dark:bg-[#1E1B19] border border-[#E8DFD5] dark:border-[#332E2A] space-y-2 text-xs animate-fadeIn">
            <div className="flex items-center gap-1.5 text-[11px] font-semibold text-[#8C7E74] dark:text-[#B3A69C] uppercase tracking-wider pb-1 border-b border-[#E8DFD5] dark:border-[#2C2926]">
              <Brain className="w-3.5 h-3.5 text-[#D96B43]" />
              <span>Retrieved Memory Grounding ({memories.length})</span>
            </div>
            {memories.map((mem, idx) => (
              <div
                key={idx}
                className="p-2.5 rounded-xl bg-white dark:bg-[#25221F] border border-[#EAE2D8] dark:border-[#38332E] space-y-1.5"
              >
                <div className="flex items-center justify-between gap-2">
                  <Badge variant="warm" size="sm">
                    {mem.memory_type?.replace('_', ' ') || 'memory'}
                  </Badge>
                  {mem.event_date && (
                    <span className="flex items-center gap-1 text-[11px] text-[#8C7E74]">
                      <Calendar className="w-3 h-3" />
                      <span>{mem.event_date} ({formatPrecision(mem.event_date_precision)})</span>
                    </span>
                  )}
                </div>
                <p className="text-xs text-[#3D352F] dark:text-[#DDD3CB] italic">
                  &ldquo;{mem.content}&rdquo;
                </p>
                {mem.similarity !== undefined && (
                  <div className="text-[10px] text-[#A39489]">
                    Semantic relevance: {(mem.similarity * 100).toFixed(1)}%
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
