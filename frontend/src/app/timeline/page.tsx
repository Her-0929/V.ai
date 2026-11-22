'use client';

import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { AppLayout } from '../../components/layout/AppLayout';
import { TimelineCard } from '../../components/timeline/TimelineCard';
import { TimelineFilters } from '../../components/timeline/TimelineFilters';
import { Spinner } from '../../components/ui/Spinner';
import { api } from '../../lib/api';
import { MemoryTimelineItem } from '../../types/api';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import { Clock, CalendarDays, FolderUp } from 'lucide-react';
import Link from 'next/link';

export default function TimelinePage() {
  const { token } = useAuth();
  const { error: toastError } = useToast();

  const [items, setItems] = useState<MemoryTimelineItem[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Filters state
  const [order, setOrder] = useState<'asc' | 'desc'>('asc');
  const [precision, setPrecision] = useState<string>('');
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');

  const loadTimeline = useCallback(async () => {
    if (!token) return;
    setIsLoading(true);
    try {
      const data = await api.getTimeline({
        order,
        precision: precision || undefined,
        start_date: startDate || undefined,
        end_date: endDate || undefined,
        limit: 150,
      });
      setItems(data.items);
      setTotal(data.total);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load timeline.';
      toastError(msg);
    } finally {
      setIsLoading(false);
    }
  }, [token, order, precision, startDate, endDate, toastError]);

  useEffect(() => {
    loadTimeline();
  }, [loadTimeline]);

  // Group items by year
  const groupedItems = useMemo(() => {
    const groups: Record<string, MemoryTimelineItem[]> = {};

    items.forEach((item) => {
      let year = 'Undated Memories';
      if (item.event_date) {
        year = item.event_date.substring(0, 4);
      } else if (item.formatted_date && /\b(19\d\d|20\d\d)\b/.test(item.formatted_date)) {
        const match = item.formatted_date.match(/\b(19\d\d|20\d\d)\b/);
        if (match) year = match[0];
      }
      if (!groups[year]) {
        groups[year] = [];
      }
      groups[year].push(item);
    });

    return groups;
  }, [items]);

  const handleResetFilters = () => {
    setPrecision('');
    setStartDate('');
    setEndDate('');
    setOrder('asc');
  };

  return (
    <AppLayout>
      <div className="flex-1 max-w-4xl w-full mx-auto px-4 sm:px-6 py-8">
        {/* Page Title & Intro */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <Clock className="w-5 h-5 text-[#D96B43]" />
              <h1 className="font-serif text-2xl sm:text-3xl font-medium text-[#2C2623] dark:text-[#F7F3EE]">
                Memory Timeline
              </h1>
            </div>
            <p className="text-xs sm:text-sm text-[#7C6E64] dark:text-[#A89C94]">
              Chronological journey of your life events, memories, and personal milestones.
            </p>
          </div>

          <div className="flex items-center gap-2 self-start sm:self-auto">
            <span className="text-xs px-3 py-1.5 rounded-xl bg-white dark:bg-[#201D1B] border border-[#E8DFD5] dark:border-[#38332E] font-medium text-[#6B5E57] dark:text-[#C4B7AE]">
              {total} {total === 1 ? 'event recorded' : 'events recorded'}
            </span>
          </div>
        </div>

        {/* Filter Controls */}
        <TimelineFilters
          order={order}
          onOrderChange={setOrder}
          precision={precision}
          onPrecisionChange={setPrecision}
          startDate={startDate}
          onStartDateChange={setStartDate}
          endDate={endDate}
          onEndDateChange={setEndDate}
          onReset={handleResetFilters}
        />

        {/* Loading Spinner */}
        {isLoading && (
          <div className="py-20 flex flex-col items-center justify-center gap-3">
            <Spinner size="lg" />
            <p className="text-xs text-[#8C7E74]">Reconstructing your chronological timeline...</p>
          </div>
        )}

        {/* Empty State */}
        {!isLoading && items.length === 0 && (
          <div className="p-12 text-center rounded-3xl bg-white dark:bg-[#201D1B] border border-[#EAE2D8] dark:border-[#38332E] max-w-md mx-auto">
            <CalendarDays className="w-10 h-10 text-[#D96B43] mx-auto mb-3 opacity-60" />
            <h3 className="font-serif text-lg font-medium text-[#2C2623] dark:text-[#F7F3EE] mb-1">
              No Timeline Memories Found
            </h3>
            <p className="text-xs text-[#7C6E64] dark:text-[#A89C94] leading-relaxed mb-5">
              {precision || startDate || endDate
                ? 'No memories matched your current precision or date filter. Try clearing your filters.'
                : 'Upload personal letters, notes, or talk with HER to begin weaving your life timeline.'}
            </p>
            <div className="flex items-center justify-center gap-3">
              <Link
                href="/ingest"
                className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#D96B43] text-white text-xs font-medium hover:bg-[#C55730] transition-colors"
              >
                <FolderUp className="w-3.5 h-3.5" />
                <span>Upload Notes / Letters</span>
              </Link>
            </div>
          </div>
        )}

        {/* Chronological Stream Grouped by Year */}
        {!isLoading && items.length > 0 && (
          <div className="space-y-8 animate-fadeIn">
            {Object.keys(groupedItems).map((year) => (
              <div key={year} className="relative">
                {/* Year Header Capsule */}
                <div className="sticky top-20 z-20 mb-6 flex items-center gap-3">
                  <div className="px-3.5 py-1.5 rounded-2xl bg-[#E07A5F] text-white font-serif text-sm font-semibold shadow-xs">
                    {year}
                  </div>
                  <div className="flex-1 h-px bg-[#E8DFD5] dark:bg-[#332E2A]" />
                  <span className="text-[11px] text-[#A89C94]">
                    {groupedItems[year].length} {groupedItems[year].length === 1 ? 'memory' : 'memories'}
                  </span>
                </div>

                {/* Items in Year */}
                <div className="ml-1 sm:ml-3">
                  {groupedItems[year].map((item) => (
                    <TimelineCard key={item.id} item={item} />
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
