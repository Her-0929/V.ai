'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import {
  Camera,
  Heart,
  Sparkles,
  Maximize2,
  X,
  MessageSquareHeart,
  Tag,
} from 'lucide-react';
import { HER_GALLERY, HerPhotoMoment } from '../../lib/herData';

export function HerVisualGallery() {
  const router = useRouter();
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [activeModalMoment, setActiveModalMoment] = useState<HerPhotoMoment | null>(null);

  const categories = [
    { label: 'All Moments ✨', value: 'all' },
    { label: 'Festivals & Silk 🌸', value: 'celebration' },
    { label: 'Rooftops & Sunshine ☀️', value: 'portrait' },
    { label: 'Road Trips & Laughter 🚗', value: 'adventure' },
    { label: 'Fairytales & Stars 🌌', value: 'dream' },
    { label: 'Cozy & Candid 🤍', value: 'intimate' },
  ];

  const filteredMoments = selectedCategory === 'all'
    ? HER_GALLERY
    : HER_GALLERY.filter((m) => m.category === selectedCategory);

  const handleDiscussMoment = (moment: HerPhotoMoment) => {
    router.push(`/?discuss=${encodeURIComponent(`I am looking at our picture: "${moment.title}"`)}`);
  };

  return (
    <div className="p-6 sm:p-8 rounded-3xl bg-white dark:bg-[#201D1B] border border-rose-100 dark:border-[#38332E] shadow-2xs space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-rose-100 dark:border-[#2C2926]">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-2xl">📸</span>
            <h3 className="font-serif text-xl sm:text-2xl font-semibold text-[#2C2623] dark:text-[#F7F3EE]">
              Your Personal Scrapbook
            </h3>
          </div>
          <p className="text-xs sm:text-sm text-[#7C6E64] dark:text-[#A89C94]">
            A curated collection of your prettiest moments, laughs, and timeless memories.
          </p>
        </div>

        <div className="flex items-center gap-1.5 self-start sm:self-auto px-3.5 py-1.5 rounded-full bg-rose-50 dark:bg-rose-950/40 text-rose-600 dark:text-rose-300 border border-rose-200 dark:border-rose-800 text-xs font-semibold">
          <Heart className="w-3.5 h-3.5 fill-current" />
          <span>{HER_GALLERY.length} Memories Saved</span>
        </div>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto pb-1 custom-scrollbar">
        {categories.map((cat) => (
          <button
            key={cat.value}
            onClick={() => setSelectedCategory(cat.value)}
            className={`px-3.5 py-2 rounded-2xl text-xs font-medium whitespace-nowrap transition-all cursor-pointer ${
              selectedCategory === cat.value
                ? 'bg-rose-500 text-white shadow-xs'
                : 'bg-[#FAF7F2] dark:bg-[#2A2623] text-[#61554D] dark:text-[#A89C94] hover:bg-rose-50 dark:hover:bg-[#342F2B]'
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {/* Gallery Grid (Polaroid Scrapbook Aesthetic) */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {filteredMoments.map((moment) => (
          <div
            key={moment.id}
            onClick={() => setActiveModalMoment(moment)}
            className="group relative rounded-3xl overflow-hidden border border-rose-100/80 dark:border-[#38332E] bg-[#FFFDFB] dark:bg-[#1A1816] p-3 shadow-2xs hover:shadow-lg hover:border-rose-300 hover:-translate-y-1 transition-all duration-300 cursor-pointer flex flex-col"
          >
            {/* Image Container */}
            <div className="relative w-full aspect-4/3 rounded-2xl overflow-hidden bg-[#EFE7DC] dark:bg-[#2C2926] mb-3">
              <img
                src={moment.src}
                alt={moment.alt}
                className="w-full h-full object-cover object-center group-hover:scale-106 transition-transform duration-500"
                loading="lazy"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-60 group-hover:opacity-80 transition-opacity" />

              {/* Expand Button */}
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setActiveModalMoment(moment);
                }}
                className="absolute top-2.5 right-2.5 p-1.5 rounded-full bg-black/40 text-white hover:bg-black/70 backdrop-blur-xs opacity-0 group-hover:opacity-100 transition-opacity"
                title="View full note"
              >
                <Maximize2 className="w-3.5 h-3.5" />
              </button>

              {/* Vibe badge */}
              <div className="absolute bottom-2.5 left-2.5">
                <span className="inline-flex items-center gap-1 text-[10px] font-medium text-white px-2 py-0.5 rounded-full bg-black/40 backdrop-blur-xs">
                  <Sparkles className="w-2.5 h-2.5 text-amber-300" />
                  <span>{moment.emotionVibe}</span>
                </span>
              </div>
            </div>

            {/* Description & Compliment */}
            <div className="px-1 flex flex-col flex-1 justify-between gap-2">
              <div>
                <h4 className="font-serif text-base font-semibold text-[#2C2623] dark:text-[#F7F3EE] group-hover:text-rose-600 dark:group-hover:text-rose-400 transition-colors">
                  {moment.title}
                </h4>
                <p className="text-xs font-serif italic text-rose-800/80 dark:text-rose-300/80 mt-1 line-clamp-2">
                  &ldquo;{moment.compliment}&rdquo;
                </p>
              </div>

              <div className="pt-2.5 border-t border-rose-50 dark:border-[#2C2926] flex items-center justify-between text-[11px] text-[#9C8E85]">
                <span className="flex items-center gap-1 text-rose-500">
                  <Heart className="w-3 h-3 fill-rose-400" />
                  <span>Treasured</span>
                </span>
                <span className="font-medium text-rose-600 dark:text-rose-400 group-hover:translate-x-0.5 transition-transform flex items-center gap-0.5">
                  <span>Read Note</span>
                  <span>&rarr;</span>
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Lightbox / Memory Detail Modal */}
      {activeModalMoment && (
        <div
          className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4 animate-fadeIn"
          onClick={() => setActiveModalMoment(null)}
        >
          <div
            className="relative max-w-2xl w-full bg-[#FAF7F2] dark:bg-[#1A1816] rounded-3xl overflow-hidden shadow-2xl border border-rose-200 dark:border-[#332E2A] flex flex-col max-h-[90vh]"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="p-4 sm:px-6 flex items-center justify-between border-b border-rose-100 dark:border-[#2C2926] bg-white dark:bg-[#201D1B]">
              <div className="flex items-center gap-2">
                <Camera className="w-4 h-4 text-rose-500" />
                <h3 className="font-serif text-lg font-semibold text-[#2C2623] dark:text-[#F7F3EE]">
                  {activeModalMoment.title}
                </h3>
              </div>
              <button
                onClick={() => setActiveModalMoment(null)}
                className="p-1.5 rounded-xl text-[#7C6E64] hover:bg-rose-50 dark:hover:bg-[#2C2926] transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Image Viewport */}
            <div className="relative w-full max-h-[48vh] bg-black/95 flex items-center justify-center overflow-hidden">
              <img
                src={activeModalMoment.src}
                alt={activeModalMoment.alt}
                className="max-h-[48vh] w-auto max-w-full object-contain"
              />
            </div>

            {/* Modal Body & Love Note */}
            <div className="p-5 sm:p-6 overflow-y-auto space-y-4 custom-scrollbar">
              <div className="flex flex-wrap items-center gap-2">
                <span className="px-3 py-1 rounded-full text-xs font-semibold bg-rose-50 dark:bg-rose-950/40 text-rose-600 dark:text-rose-300 border border-rose-200 dark:border-rose-900 flex items-center gap-1.5">
                  <Heart className="w-3 h-3 fill-current" />
                  <span>{activeModalMoment.emotionVibe}</span>
                </span>
              </div>

              {/* Compliment Quote Callout */}
              <div className="p-4 rounded-2xl bg-rose-50/70 dark:bg-rose-950/20 border border-rose-200/60 dark:border-rose-900/40">
                <div className="text-[11px] font-bold uppercase tracking-wider text-rose-700 dark:text-rose-300 mb-1 flex items-center gap-1">
                  <Sparkles className="w-3.5 h-3.5" />
                  <span>Why You Look Unforgettable Here</span>
                </div>
                <p className="text-sm font-serif italic text-rose-950 dark:text-rose-200 leading-relaxed">
                  &ldquo;{activeModalMoment.compliment}&rdquo;
                </p>
              </div>

              {/* Love Note */}
              <div className="space-y-1">
                <span className="text-[11px] font-semibold text-[#8C7E74] dark:text-[#A89C94] uppercase tracking-wider">
                  A Little Thought
                </span>
                <p className="text-sm text-[#4A4039] dark:text-[#DDD3CB] leading-relaxed">
                  {activeModalMoment.loveNote}
                </p>
              </div>

              {/* Action Buttons */}
              <div className="pt-2 flex flex-col sm:flex-row gap-3">
                <button
                  onClick={() => handleDiscussMoment(activeModalMoment)}
                  className="flex-1 flex items-center justify-center gap-2 py-3 px-4 rounded-xl bg-rose-500 hover:bg-rose-600 text-white text-xs font-semibold transition-all shadow-sm cursor-pointer"
                >
                  <MessageSquareHeart className="w-4 h-4" />
                  <span>Talk to Me About This Picture 💖</span>
                </button>
                <button
                  onClick={() => setActiveModalMoment(null)}
                  className="py-3 px-5 rounded-xl bg-white dark:bg-[#2A2623] border border-[#E8DFD5] dark:border-[#38332E] text-xs font-semibold text-[#61554D] dark:text-[#B3A69C] hover:bg-rose-50 transition-all cursor-pointer"
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
