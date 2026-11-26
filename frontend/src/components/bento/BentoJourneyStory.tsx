'use client';

import React, { useState } from 'react';
import { Calendar, Heart, Sparkles, X } from 'lucide-react';
import { JOURNEY_TIMELINE, JourneyMilestone } from '../../lib/herData';

export function BentoJourneyStory() {
  const [activeMilestone, setActiveMilestone] = useState<JourneyMilestone | null>(null);

  return (
    <>
      <div className="flex flex-col h-full justify-between p-5 rounded-3xl bg-gradient-to-br from-blue-900/10 via-indigo-900/10 to-sky-600/10 dark:from-slate-900 dark:to-blue-950/60 border border-blue-200/80 dark:border-blue-900/50 relative overflow-hidden group shadow-2xs">
        <div>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-blue-600 dark:text-blue-400" />
              <span className="text-[11px] font-bold uppercase tracking-wider text-blue-700 dark:text-blue-300">
                Our Story: 2017 &rarr; Forever
              </span>
            </div>
            <span className="text-[10px] text-blue-600 dark:text-blue-400 font-serif font-bold">
              10 Milestones
            </span>
          </div>

          <h3 className="font-serif text-lg font-bold text-slate-900 dark:text-blue-50 mb-1">
            The Journey of You &amp; Me 💫
          </h3>
          <p className="text-xs text-slate-600 dark:text-slate-300 italic font-serif line-clamp-2 mb-3">
            &ldquo;From that bus stop in 2017 to every road trip and smile — my heart has only ever beaten for you.&rdquo;
          </p>
        </div>

        {/* Milestone Quick List */}
        <div className="space-y-1.5 my-2">
          {JOURNEY_TIMELINE.slice(0, 4).map((m, idx) => (
            <div
              key={idx}
              onClick={() => setActiveMilestone(m)}
              className="p-2 rounded-xl bg-white/90 dark:bg-slate-900/80 border border-blue-100 dark:border-blue-950 hover:border-blue-400 cursor-pointer transition-all flex items-center justify-between text-xs"
            >
              <div className="flex items-center gap-2 truncate">
                <span className="w-1.5 h-1.5 rounded-full bg-blue-600 dark:bg-blue-400 shrink-0" />
                <span className="font-semibold text-slate-900 dark:text-slate-200 truncate">
                  {m.title}
                </span>
              </div>
              <span className="text-[10px] font-serif font-bold text-blue-600 dark:text-blue-400 shrink-0">
                {m.date.split(',')[0]}
              </span>
            </div>
          ))}
        </div>

        <button
          onClick={() => setActiveMilestone(JOURNEY_TIMELINE[0])}
          className="w-full py-2 px-3 rounded-2xl bg-gradient-to-r from-blue-600 via-indigo-600 to-blue-700 text-white font-medium text-xs flex items-center justify-center gap-1.5 shadow-sm transition-transform hover:scale-[1.01]"
        >
          <Calendar className="w-3.5 h-3.5" />
          <span>Walk Down Memory Lane (All 10 Dates)</span>
        </button>
      </div>

      {/* Story Modal */}
      {activeMilestone && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fadeIn">
          <div className="relative w-full max-w-xl rounded-3xl bg-[#FAF7F2] dark:bg-slate-900 border border-blue-200 dark:border-blue-900/60 shadow-2xl p-6 sm:p-8 max-h-[90vh] overflow-y-auto custom-scrollbar">
            <button
              onClick={() => setActiveMilestone(null)}
              className="absolute top-4 right-4 p-2 rounded-full bg-black/5 dark:bg-white/10 hover:bg-black/10 dark:hover:bg-white/20 text-slate-600 dark:text-slate-300"
            >
              <X className="w-4 h-4" />
            </button>

            <div className="flex items-center gap-2 text-blue-600 dark:text-blue-400 font-serif text-xs font-bold mb-1">
              <Calendar className="w-3.5 h-3.5" />
              <span>{activeMilestone.date}</span>
              <span>&bull;</span>
              <span className="px-2 py-0.5 rounded-full bg-blue-100 dark:bg-blue-950 text-[10px] border border-blue-200 dark:border-blue-800">
                {activeMilestone.badge}
              </span>
            </div>

            <h2 className="font-serif text-2xl font-bold text-slate-900 dark:text-white mb-3">
              {activeMilestone.title}
            </h2>

            {activeMilestone.photo && (
              <div className="w-full h-56 rounded-2xl overflow-hidden mb-4 border border-blue-200/60 shadow-xs">
                <img
                  src={activeMilestone.photo}
                  alt={activeMilestone.title}
                  className="w-full h-full object-cover object-top"
                />
              </div>
            )}

            <div className="p-4 rounded-2xl bg-blue-50/80 dark:bg-blue-950/40 border-l-4 border-blue-600 font-serif italic text-blue-950 dark:text-blue-200 text-sm mb-4 leading-relaxed">
              &ldquo;{activeMilestone.quote}&rdquo;
            </div>

            <p className="text-sm text-slate-800 dark:text-slate-200 leading-relaxed mb-6 font-serif">
              {activeMilestone.description}
            </p>

            <div className="pt-4 border-t border-blue-100 dark:border-blue-950 flex items-center justify-between">
              <span className="text-xs text-slate-500 dark:text-slate-400 font-serif">
                Milestone of Our Story
              </span>

              <div className="flex items-center gap-2">
                {JOURNEY_TIMELINE.map((m, idx) => (
                  <button
                    key={idx}
                    onClick={() => setActiveMilestone(m)}
                    className={`w-2.5 h-2.5 rounded-full transition-all ${
                      activeMilestone.date === m.date
                        ? 'bg-blue-600 scale-150 ring-2 ring-blue-300'
                        : 'bg-blue-200 dark:bg-blue-900/60 hover:bg-blue-300'
                    }`}
                    title={m.title}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
