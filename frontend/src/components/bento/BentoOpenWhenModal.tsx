'use client';

import React, { useState } from 'react';
import { Mail, Heart, X, ChevronRight } from 'lucide-react';
import { OPEN_WHEN_LETTERS, OpenWhenLetter } from '../../lib/herData';

export function BentoOpenWhenModal() {
  const [selectedLetter, setSelectedLetter] = useState<OpenWhenLetter | null>(null);

  return (
    <>
      <div className="flex flex-col h-full justify-between p-5 rounded-3xl bg-gradient-to-br from-blue-500/10 via-indigo-500/10 to-sky-500/5 dark:from-slate-900/90 dark:to-blue-950/40 border border-blue-200/80 dark:border-blue-900/50 relative overflow-hidden group shadow-2xs">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <span className="text-xl">💌</span>
            <span className="text-[11px] font-bold uppercase tracking-wider text-blue-700 dark:text-blue-300">
              Open When Letters
            </span>
          </div>
          <span className="text-[10px] px-2.5 py-0.5 rounded-full bg-blue-100 dark:bg-blue-950/80 text-blue-700 dark:text-blue-300 font-bold border border-blue-200 dark:border-blue-900">
            {OPEN_WHEN_LETTERS.length} Sealed
          </span>
        </div>

        <div className="space-y-2 my-auto">
          {OPEN_WHEN_LETTERS.slice(0, 3).map((letter) => (
            <button
              key={letter.id}
              onClick={() => setSelectedLetter(letter)}
              className="w-full text-left p-2.5 rounded-2xl bg-white/90 dark:bg-slate-900/80 hover:bg-white dark:hover:bg-slate-800 border border-blue-100/90 dark:border-blue-950 transition-all hover:scale-[1.02] shadow-2xs flex items-center justify-between group/item"
            >
              <div className="flex items-center gap-2.5 truncate">
                <span className="text-base">{letter.icon}</span>
                <div className="truncate">
                  <div className="text-xs font-semibold text-slate-900 dark:text-blue-50 truncate group-hover/item:text-blue-600 transition-colors">
                    {letter.title}
                  </div>
                  <div className="text-[10px] text-slate-500 dark:text-slate-400 truncate">
                    {letter.dateBadge}
                  </div>
                </div>
              </div>
              <ChevronRight className="w-3.5 h-3.5 text-blue-400 group-hover/item:translate-x-0.5 transition-transform shrink-0" />
            </button>
          ))}
        </div>

        <button
          onClick={() => setSelectedLetter(OPEN_WHEN_LETTERS[0])}
          className="w-full mt-3 py-2 px-3 rounded-2xl bg-blue-600 hover:bg-blue-700 text-white font-medium text-xs flex items-center justify-center gap-1.5 shadow-sm transition-all hover:shadow-blue-500/25"
        >
          <Mail className="w-3.5 h-3.5" />
          <span>Read All Sealed Letters</span>
        </button>
      </div>

      {/* Letter Reading Modal */}
      {selectedLetter && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fadeIn">
          <div className="relative w-full max-w-lg rounded-3xl bg-[#FAF7F2] dark:bg-slate-900 border border-blue-200 dark:border-blue-900/60 shadow-2xl p-6 sm:p-8 max-h-[85vh] overflow-y-auto custom-scrollbar">
            <button
              onClick={() => setSelectedLetter(null)}
              className="absolute top-4 right-4 p-2 rounded-full bg-black/5 dark:bg-white/10 hover:bg-black/10 dark:hover:bg-white/20 text-slate-600 dark:text-slate-300 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>

            <div className="flex items-center gap-3 mb-4">
              <span className="text-3xl">{selectedLetter.icon}</span>
              <div>
                <span className="text-[11px] font-bold text-blue-600 dark:text-blue-400 uppercase tracking-widest">
                  {selectedLetter.dateBadge}
                </span>
                <h3 className="font-serif text-xl sm:text-2xl font-bold text-slate-900 dark:text-white">
                  {selectedLetter.title}
                </h3>
              </div>
            </div>

            {selectedLetter.associatedPhoto && (
              <div className="w-full h-48 rounded-2xl overflow-hidden mb-4 border border-blue-200/60 shadow-xs">
                <img
                  src={selectedLetter.associatedPhoto}
                  alt={selectedLetter.title}
                  className="w-full h-full object-cover object-top"
                />
              </div>
            )}

            <div className="font-serif text-sm sm:text-base text-slate-800 dark:text-slate-200 leading-relaxed whitespace-pre-line space-y-4 p-4 rounded-2xl bg-white/90 dark:bg-slate-800/80 border border-blue-100 dark:border-blue-950">
              {selectedLetter.content}
            </div>

            <div className="mt-6 pt-4 border-t border-blue-100 dark:border-blue-950 flex items-center justify-between">
              <div className="flex items-center gap-1.5 overflow-x-auto py-1">
                {OPEN_WHEN_LETTERS.map((l) => (
                  <button
                    key={l.id}
                    onClick={() => setSelectedLetter(l)}
                    className={`px-2.5 py-1 rounded-xl text-xs font-serif transition-all ${
                      selectedLetter.id === l.id
                        ? 'bg-blue-600 text-white font-bold shadow-xs'
                        : 'bg-white dark:bg-slate-800 text-slate-600 dark:text-slate-400 hover:bg-blue-50'
                    }`}
                  >
                    {l.icon}
                  </button>
                ))}
              </div>

              <div className="text-xs font-serif italic text-blue-600 dark:text-blue-400 flex items-center gap-1">
                <Heart className="w-3.5 h-3.5 fill-current" />
                <span>Yours Vivek</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
