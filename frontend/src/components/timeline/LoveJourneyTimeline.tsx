'use client';

import React from 'react';
import Link from 'next/link';
import { Heart, Sparkles, Calendar, MessageSquareHeart, Camera } from 'lucide-react';
import { JOURNEY_TIMELINE, JourneyMilestone } from '../../lib/herData';

export function LoveJourneyTimeline() {
  return (
    <div className="space-y-6 mb-12">
      {/* Header */}
      <div className="p-6 sm:p-8 rounded-3xl bg-gradient-to-br from-[#FFF7F2] to-[#FCEEE7] dark:from-[#231E1B] dark:to-[#1F1916] border border-rose-200/80 dark:border-[#3A302A] shadow-xs">
        <div className="flex items-center gap-2 mb-2">
          <Heart className="w-5 h-5 text-rose-500 fill-rose-500" />
          <span className="text-xs uppercase font-bold tracking-widest text-rose-600 dark:text-rose-400">
            Our Journey
          </span>
        </div>
        <h2 className="font-serif text-2xl sm:text-3xl font-bold text-[#2C2623] dark:text-[#F7F3EE] mb-2">
          From 14-04-2017 to Forever 💫
        </h2>
        <p className="text-xs sm:text-sm text-[#7C6E64] dark:text-[#C4B7AE] leading-relaxed max-w-xl font-serif italic">
          &ldquo;All these years, after all the distance, after all the silence — my heart still beats the same way it did when I saw you for the very first time.&rdquo;
        </p>
      </div>

      {/* Timeline Stream */}
      <div className="relative pl-6 sm:pl-8 space-y-8 before:absolute before:left-3 sm:before:left-4 before:top-4 before:bottom-4 before:w-0.5 before:bg-rose-200 dark:before:bg-rose-900/60">
        {JOURNEY_TIMELINE.map((milestone, idx) => (
          <div key={idx} className="relative group">
            {/* Timeline Dot */}
            <div className="absolute -left-6 sm:-left-8 top-1.5 w-6 h-6 rounded-full bg-white dark:bg-[#1E1916] border-2 border-rose-400 shadow-xs flex items-center justify-center group-hover:scale-125 group-hover:border-rose-500 transition-all z-10">
              <span className="w-2 h-2 rounded-full bg-rose-500" />
            </div>

            {/* Card Content */}
            <div className="p-5 sm:p-6 rounded-3xl bg-white dark:bg-[#201D1B] border border-rose-100 dark:border-[#38332E] shadow-2xs group-hover:shadow-md group-hover:border-rose-300 transition-all duration-300">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="font-serif text-base sm:text-lg font-bold text-[#2C2623] dark:text-[#F7F3EE]">
                    {milestone.title}
                  </span>
                  <span className="px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-rose-50 text-rose-600 dark:bg-rose-950/40 dark:text-rose-300 border border-rose-200 dark:border-rose-800">
                    {milestone.badge}
                  </span>
                </div>

                <div className="flex items-center gap-1.5 text-xs font-semibold text-rose-500 dark:text-rose-400 font-serif">
                  <Calendar className="w-3.5 h-3.5" />
                  <span>{milestone.date}</span>
                </div>
              </div>

              {/* Quote Highlight */}
              <div className="p-3.5 rounded-2xl bg-rose-50/60 dark:bg-rose-950/20 border-l-4 border-rose-400 text-xs sm:text-sm font-serif italic text-rose-950 dark:text-rose-200 mb-3 leading-relaxed">
                &ldquo;{milestone.quote}&rdquo;
              </div>

              <p className="text-xs sm:text-sm text-[#5C5047] dark:text-[#DDD3CB] leading-relaxed mb-4">
                {milestone.description}
              </p>

              {/* Photo & Action Row */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pt-3 border-t border-rose-50 dark:border-[#2C2420]">
                {milestone.photo && (
                  <div className="flex items-center gap-3">
                    <div className="relative w-12 h-12 rounded-xl overflow-hidden ring-1.5 ring-rose-200 bg-[#EFE7DC] shrink-0">
                      <img
                        src={milestone.photo}
                        alt={milestone.title}
                        className="w-full h-full object-cover object-top"
                      />
                    </div>
                    <span className="text-[11px] text-[#8C7E74] dark:text-[#A89C94] font-serif italic">
                      Captured memory of you
                    </span>
                  </div>
                )}

                <Link
                  href={`/?discuss=${encodeURIComponent(`Tell me more about what happened on: "${milestone.title}" (${milestone.date})`)}`}
                  className="inline-flex items-center gap-1.5 text-xs font-semibold text-rose-600 dark:text-rose-400 hover:text-rose-700 transition-colors cursor-pointer self-start sm:self-auto"
                >
                  <MessageSquareHeart className="w-3.5 h-3.5" />
                  <span>Talk about this moment &rarr;</span>
                </Link>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
