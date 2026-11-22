'use client';

import React from 'react';
import {
  Calendar,
  Compass,
  Edit3,
  Trash2,
  PowerOff,
  Star,
  CheckCircle2,
  Clock,
} from 'lucide-react';
import { MemoryResponse } from '../../types/api';
import { Badge } from '../ui/Badge';
import { formatDate, formatPrecision } from '../../lib/utils';

interface MemoryCardProps {
  memory: MemoryResponse;
  onInspectProvenance: (memory: MemoryResponse) => void;
  onCorrectMemory: (memory: MemoryResponse) => void;
  onDeactivateMemory?: (id: string) => void;
  onDeleteMemory?: (id: string) => void;
}

export function MemoryCard({
  memory,
  onInspectProvenance,
  onCorrectMemory,
  onDeactivateMemory,
  onDeleteMemory,
}: MemoryCardProps) {
  const isSuperseded = memory.status === 'superseded' || !memory.is_active;

  return (
    <div
      className={`p-5 rounded-3xl bg-white dark:bg-[#201D1B] border transition-all ${
        isSuperseded
          ? 'opacity-70 border-[#E5DDD4] dark:border-[#2C2926] bg-[#FAF7F2]/50'
          : 'border-[#EAE2D8] dark:border-[#38332E] shadow-2xs hover:shadow-md hover:border-[#D96B43]/40'
      }`}
    >
      {/* Header Badges & Actions */}
      <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
        <div className="flex items-center gap-2 flex-wrap">
          <Badge variant="warm" size="sm">
            {memory.memory_type.replace(/_/g, ' ')}
          </Badge>

          {isSuperseded ? (
            <Badge variant="default" size="sm">
              Superseded (v{memory.version})
            </Badge>
          ) : (
            <Badge variant="sage" size="sm">
              <CheckCircle2 className="w-2.5 h-2.5 mr-0.5" />
              Active (v{memory.version})
            </Badge>
          )}

          {memory.event_date && (
            <span className="flex items-center gap-1 text-[11px] text-[#8C7E74]">
              <Calendar className="w-3 h-3" />
              <span>
                {formatDate(memory.event_date)} ({formatPrecision(memory.event_date_precision)})
              </span>
            </span>
          )}
        </div>

        {/* Importance Stars */}
        <div className="flex items-center gap-1" title={`Importance: ${memory.importance}/5`}>
          {Array.from({ length: 5 }).map((_, i) => (
            <Star
              key={i}
              className={`w-3 h-3 ${
                i < memory.importance
                  ? 'text-amber-500 fill-amber-500'
                  : 'text-stone-300 dark:text-stone-700'
              }`}
            />
          ))}
        </div>
      </div>

      {/* Main Content */}
      <p className="text-sm text-[#2C2623] dark:text-[#F7F3EE] leading-relaxed mb-4 font-normal">
        {memory.content}
      </p>

      {/* Card Footer Actions */}
      <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-[#F2ECE3] dark:border-[#2D2926] text-xs">
        <div className="flex items-center gap-2 text-[11px] text-[#A89C94]">
          <Clock className="w-3 h-3" />
          <span>Recorded {formatDate(memory.created_at)}</span>
        </div>

        <div className="flex items-center gap-2">
          {/* Provenance Button */}
          <button
            onClick={() => onInspectProvenance(memory)}
            className="flex items-center gap-1 px-2.5 py-1.5 rounded-xl bg-[#FAF2EB] dark:bg-[#2C221A] text-[#D96B43] dark:text-[#EB8D74] hover:bg-[#F5E4D7] transition-colors font-medium text-xs cursor-pointer"
          >
            <Compass className="w-3 h-3" />
            <span>Provenance</span>
          </button>

          {/* Correct Button */}
          {!isSuperseded && (
            <button
              onClick={() => onCorrectMemory(memory)}
              className="flex items-center gap-1 px-2.5 py-1.5 rounded-xl bg-[#F4EFE9] dark:bg-[#292522] text-[#61554D] dark:text-[#D1C6BD] hover:bg-[#EAE2D8] transition-colors font-medium text-xs cursor-pointer"
            >
              <Edit3 className="w-3 h-3" />
              <span>Correct</span>
            </button>
          )}

          {/* Deactivate Button */}
          {!isSuperseded && onDeactivateMemory && (
            <button
              onClick={() => onDeactivateMemory(memory.id)}
              className="p-1.5 rounded-xl text-[#A89C94] hover:text-stone-700 hover:bg-[#EFE7DC] transition-colors"
              title="Deactivate Memory"
            >
              <PowerOff className="w-3.5 h-3.5" />
            </button>
          )}

          {/* Delete Button */}
          {onDeleteMemory && (
            <button
              onClick={() => onDeleteMemory(memory.id)}
              className="p-1.5 rounded-xl text-[#A89C94] hover:text-rose-600 hover:bg-rose-50 transition-colors"
              title="Delete Memory Permanently"
            >
              <Trash2 className="w-3.5 h-3.5" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
