'use client';

import React, { useState } from 'react';
import { Mail, Heart, X, MessageSquareHeart, Sparkles, Feather } from 'lucide-react';
import { OPEN_WHEN_LETTERS, OpenWhenLetter } from '../../lib/herData';
import { useRouter } from 'next/navigation';

export function OpenWhenLetters() {
  const [selectedLetter, setSelectedLetter] = useState<OpenWhenLetter | null>(null);
  const router = useRouter();

  const handleReplyInChat = (letter: OpenWhenLetter) => {
    router.push(`/?discuss=${encodeURIComponent(`I just opened the letter: "${letter.title}"`)}`);
  };

  return (
    <div className="mb-8 space-y-4">
      <div className="flex items-center justify-between px-1">
        <div className="flex items-center gap-2">
          <Mail className="w-5 h-5 text-rose-500" />
          <h2 className="font-serif text-xl sm:text-2xl font-semibold text-[#2C2623] dark:text-[#F7F3EE]">
            Open When Letters 💌
          </h2>
        </div>
        <span className="text-xs text-rose-500 font-medium font-serif italic">
          Click an envelope to open
        </span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {OPEN_WHEN_LETTERS.map((letter) => (
          <div
            key={letter.id}
            onClick={() => setSelectedLetter(letter)}
            className="group relative rounded-3xl p-5 border border-rose-200/80 dark:border-[#38332E] bg-gradient-to-br from-[#FFFBF7] to-[#FDF4EE] dark:from-[#221D1A] dark:to-[#1E1916] shadow-2xs hover:shadow-md hover:border-rose-400 hover:-translate-y-1 transition-all duration-300 cursor-pointer flex flex-col justify-between"
          >
            <div>
              {/* Envelope flap / icon aesthetic */}
              <div className="flex items-center justify-between mb-3">
                <span className="text-2xl p-2 rounded-2xl bg-white dark:bg-[#2C2420] shadow-2xs border border-rose-100 dark:border-[#42352E]">
                  {letter.icon}
                </span>
                <span className="text-[10px] uppercase font-bold tracking-wider px-2 py-0.5 rounded-full bg-rose-100 dark:bg-rose-950/60 text-rose-600 dark:text-rose-300">
                  Sealed 💌
                </span>
              </div>

              <h3 className="font-serif text-base font-semibold text-[#2C2623] dark:text-[#F7F3EE] group-hover:text-rose-600 dark:group-hover:text-rose-400 transition-colors mb-2">
                {letter.title}
              </h3>

              <p className="text-xs text-[#7C6E64] dark:text-[#A89C94] leading-relaxed line-clamp-2 italic">
                &ldquo;{letter.preview}&rdquo;
              </p>
            </div>

            <div className="mt-4 pt-3 border-t border-rose-100 dark:border-[#332A24] flex items-center justify-between text-xs text-rose-500 dark:text-rose-400 font-medium">
              <span className="flex items-center gap-1 text-[11px]">
                <Heart className="w-3 h-3 fill-rose-400 text-rose-400" />
                <span>Just for you</span>
              </span>
              <span className="group-hover:translate-x-1 transition-transform">
                Read Letter &rarr;
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Letter Reading Modal */}
      {selectedLetter && (
        <div
          className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4 animate-fadeIn"
          onClick={() => setSelectedLetter(null)}
        >
          <div
            className="relative max-w-xl w-full bg-[#FAF7F2] dark:bg-[#1C1815] rounded-3xl overflow-hidden shadow-2xl border border-rose-200 dark:border-[#3A302A] flex flex-col max-h-[90vh]"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="p-4 sm:px-6 flex items-center justify-between border-b border-rose-100 dark:border-[#2C2420] bg-white/70 dark:bg-[#201B17]/70">
              <div className="flex items-center gap-2">
                <span className="text-xl">{selectedLetter.icon}</span>
                <h3 className="font-serif text-lg font-semibold text-[#2C2623] dark:text-[#F7F3EE]">
                  {selectedLetter.title}
                </h3>
              </div>
              <button
                onClick={() => setSelectedLetter(null)}
                className="p-1.5 rounded-xl text-[#7C6E64] hover:bg-rose-50 dark:hover:bg-[#2C2420] transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Body / Parchment Letter */}
            <div className="p-6 sm:p-8 overflow-y-auto space-y-6 custom-scrollbar bg-gradient-to-b from-[#FFFDFB] to-[#FAF5EF] dark:from-[#1E1916] dark:to-[#171412]">
              {selectedLetter.associatedPhoto && (
                <div className="relative w-full h-44 rounded-2xl overflow-hidden shadow-sm border border-rose-100 dark:border-[#3A302A]">
                  <img
                    src={selectedLetter.associatedPhoto}
                    alt={selectedLetter.title}
                    className="w-full h-full object-cover object-top"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/50 via-transparent to-transparent" />
                  <span className="absolute bottom-2 left-3 text-xs text-white/95 font-serif italic drop-shadow-sm flex items-center gap-1.5">
                    <Sparkles className="w-3.5 h-3.5 text-amber-300" />
                    <span>A little piece of your magic</span>
                  </span>
                </div>
              )}

              {/* Letter Prose */}
              <div className="p-6 rounded-2xl bg-white dark:bg-[#221D1A] border border-rose-100/80 dark:border-[#352B24] shadow-2xs font-serif text-[#3D352F] dark:text-[#E8DDD4] text-sm leading-relaxed whitespace-pre-line">
                {selectedLetter.content}
              </div>

              {/* Actions */}
              <div className="flex flex-col sm:flex-row gap-3 pt-2">
                <button
                  onClick={() => handleReplyInChat(selectedLetter)}
                  className="flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-rose-500 hover:bg-rose-600 text-white text-xs font-semibold shadow-sm transition-all cursor-pointer"
                >
                  <MessageSquareHeart className="w-4 h-4" />
                  <span>Talk to Me About This Letter 💖</span>
                </button>
                <button
                  onClick={() => setSelectedLetter(null)}
                  className="py-3 px-5 rounded-xl bg-white dark:bg-[#25201C] border border-[#E8DFD5] dark:border-[#38332E] text-xs font-semibold text-[#61554D] dark:text-[#B3A69C] hover:bg-[#FAF7F2] transition-colors cursor-pointer"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
