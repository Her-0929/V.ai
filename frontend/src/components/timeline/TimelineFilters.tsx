'use client';

import React from 'react';
import { ArrowDownAZ, ArrowUpZA } from 'lucide-react';

interface TimelineFiltersProps {
  order: 'asc' | 'desc';
  onOrderChange: (order: 'asc' | 'desc') => void;
  precision: string;
  onPrecisionChange: (precision: string) => void;
  startDate: string;
  onStartDateChange: (date: string) => void;
  endDate: string;
  onEndDateChange: (date: string) => void;
  onReset: () => void;
}

export function TimelineFilters({
  order,
  onOrderChange,
  precision,
  onPrecisionChange,
  startDate,
  onStartDateChange,
  endDate,
  onEndDateChange,
  onReset,
}: TimelineFiltersProps) {
  const hasActiveFilters = precision !== '' || startDate !== '' || endDate !== '';

  return (
    <div className="p-4 sm:p-5 rounded-3xl bg-white dark:bg-[#201D1B] border border-[#EAE2D8] dark:border-[#38332E] shadow-2xs mb-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        {/* Left: Precision & Sort Order */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Order Toggle */}
          <div className="flex items-center rounded-xl bg-[#F7F2EC] dark:bg-[#2C2926] p-1 border border-[#E8DFD5] dark:border-[#38332E]">
            <button
              onClick={() => onOrderChange('asc')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                order === 'asc'
                  ? 'bg-white dark:bg-[#1E1B19] text-[#D96B43] shadow-xs'
                  : 'text-[#7C6E64] dark:text-[#A89C94] hover:text-[#2C2623]'
              }`}
              title="Oldest First"
            >
              <ArrowDownAZ className="w-3.5 h-3.5" />
              <span>Oldest First</span>
            </button>
            <button
              onClick={() => onOrderChange('desc')}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                order === 'desc'
                  ? 'bg-white dark:bg-[#1E1B19] text-[#D96B43] shadow-xs'
                  : 'text-[#7C6E64] dark:text-[#A89C94] hover:text-[#2C2623]'
              }`}
              title="Newest First"
            >
              <ArrowUpZA className="w-3.5 h-3.5" />
              <span>Newest First</span>
            </button>
          </div>

          {/* Precision Selector */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-[#8C7E74] dark:text-[#A89C94] font-medium hidden sm:inline">
              Precision:
            </span>
            <select
              value={precision}
              onChange={(e) => onPrecisionChange(e.target.value)}
              className="px-3 py-1.5 rounded-xl text-xs font-medium bg-[#F7F2EC] dark:bg-[#2C2926] border border-[#E8DFD5] dark:border-[#38332E] text-[#2C2623] dark:text-[#F7F3EE] focus:outline-hidden focus:border-[#D96B43]"
            >
              <option value="">All Precisions</option>
              <option value="day">Exact Day</option>
              <option value="month">Specific Month</option>
              <option value="year">Year Level</option>
              <option value="decade">Decade Era</option>
            </select>
          </div>
        </div>

        {/* Right: Date Range & Clear */}
        <div className="flex flex-wrap items-center gap-2.5">
          <div className="flex items-center gap-1.5">
            <input
              type="date"
              value={startDate}
              onChange={(e) => onStartDateChange(e.target.value)}
              className="px-2.5 py-1.5 rounded-xl text-xs bg-[#F7F2EC] dark:bg-[#2C2926] border border-[#E8DFD5] dark:border-[#38332E] text-[#2C2623] dark:text-[#F7F3EE] focus:outline-hidden"
              placeholder="Start Date"
            />
            <span className="text-xs text-[#A89C94]">to</span>
            <input
              type="date"
              value={endDate}
              onChange={(e) => onEndDateChange(e.target.value)}
              className="px-2.5 py-1.5 rounded-xl text-xs bg-[#F7F2EC] dark:bg-[#2C2926] border border-[#E8DFD5] dark:border-[#38332E] text-[#2C2623] dark:text-[#F7F3EE] focus:outline-hidden"
              placeholder="End Date"
            />
          </div>

          {hasActiveFilters && (
            <button
              onClick={onReset}
              className="px-2.5 py-1.5 rounded-xl text-xs font-medium text-[#D96B43] hover:bg-[#FDEEE9] dark:hover:bg-[#38241D] transition-colors"
            >
              Reset
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
