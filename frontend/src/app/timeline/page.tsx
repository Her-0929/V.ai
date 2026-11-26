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
import { Clock, CalendarDays, FolderUp, Camera, Heart, Sparkles } from 'lucide-react';
import Link from 'next/link';
import { HER_GALLERY } from '../../lib/herData';
import { LoveJourneyTimeline } from '../../components/timeline/LoveJourneyTimeline';

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
              <span className="text-2xl">📸</span>
              <h1 className="font-serif text-2xl sm:text-3xl font-medium text-[#2C2623] dark:text-[#F7F3EE]">
                Moments Scrapbook
              </h1>
            </div>
            <p className="text-xs sm:text-sm text-[#7C6E64] dark:text-[#A89C94]">
              A visual timeline of your brightest smiles, celebrations, and unforgettable memories.
            </p>
          </div>

          <div className="flex items-center gap-2 self-start sm:self-auto">
            <span className="text-xs px-3 py-1.5 rounded-xl bg-white dark:bg-[#201D1B] border border-[#E8DFD5] dark:border-[#38332E] font-medium text-[#6B5E57] dark:text-[#C4B7AE]">
              {total} {total === 1 ? 'moment preserved' : 'moments preserved'} ✨
            </span>
          </div>
        </div>

        {/* Visual Timeline Moments Reel */}
        <div className="mb-6 p-4 rounded-3xl bg-white dark:bg-[#201D1B] border border-[#EAE2D8] dark:border-[#38332E] shadow-2xs">
          <div className="flex items-center justify-between mb-3 px-1">
            <div className="flex items-center gap-2">
              <Camera className="w-4 h-4 text-[#D96B43]" />
              <h3 className="font-serif text-sm font-semibold text-[#2C2623] dark:text-[#F7F3EE]">
                Snapshots Through Time ✨
              </h3>
            </div>
            <Link
              href="/profile"
              className="text-xs text-[#D96B43] hover:underline font-medium flex items-center gap-1"
            >
              <span>View Full Album</span>
              <span>&rarr;</span>
            </Link>
          </div>

          <div className="flex items-center gap-3 overflow-x-auto pb-2 custom-scrollbar">
            {HER_GALLERY.map((moment) => (
              <Link
                key={moment.id}
                href={`/?discuss=${encodeURIComponent(moment.title)}`}
                className="group shrink-0 w-36 rounded-2xl overflow-hidden border border-[#E8DFD5] dark:border-[#38332E] bg-[#FAF7F2] dark:bg-[#1E1B19] p-1.5 transition-all hover:border-[#D96B43] hover:shadow-xs"
                title={`Ask HER about "${moment.title}"`}
              >
                <div className="relative w-full h-24 rounded-xl overflow-hidden mb-1.5 bg-[#EFE7DC]">
                  <img
                    src={moment.src}
                    alt={moment.title}
                    className="w-full h-full object-cover group-hover:scale-108 transition-transform duration-300"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent" />
                  <span className="absolute bottom-1 left-1.5 text-[9px] font-semibold text-white/90 drop-shadow-xs flex items-center gap-0.5">
                    <Heart className="w-2.5 h-2.5 text-[#E07A5F] fill-[#E07A5F]" />
                    <span>{moment.emotionVibe.split('&')[0].trim()}</span>
                  </span>
                </div>
                <div className="px-0.5">
                  <div className="text-[11px] font-medium text-[#2C2623] dark:text-[#F7F3EE] truncate group-hover:text-[#D96B43] transition-colors">
                    {moment.title}
                  </div>
                  <div className="text-[9px] text-[#8C7E74] dark:text-[#A89C94] capitalize">
                    {moment.category}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>

        {/* The 2017 - Forever Journey Timeline */}
        <LoveJourneyTimeline />

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
              No Moments Added Yet
            </h3>
            <p className="text-xs text-[#7C6E64] dark:text-[#A89C94] leading-relaxed mb-5">
              {precision || startDate || endDate
                ? 'No memories matched your current precision or date filter. Try clearing your filters.'
                : 'Start a conversation or leave a note in our Wish Capsule to begin adding memories to our story together 💖'}
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
