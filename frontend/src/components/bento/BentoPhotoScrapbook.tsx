'use client';

import React, { useState } from 'react';
import { Camera, Heart, Sparkles, X, ChevronLeft, ChevronRight } from 'lucide-react';
import { HER_GALLERY, GalleryMoment } from '../../lib/herData';

export function BentoPhotoScrapbook() {
  const [selectedPhoto, setSelectedPhoto] = useState<GalleryMoment | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);

  const openPhoto = (photo: GalleryMoment, index: number) => {
    setSelectedPhoto(photo);
    setCurrentIndex(index);
  };

  const nextPhoto = () => {
    const nextIdx = (currentIndex + 1) % HER_GALLERY.length;
    setCurrentIndex(nextIdx);
    setSelectedPhoto(HER_GALLERY[nextIdx]);
  };

  const prevPhoto = () => {
    const prevIdx = (currentIndex - 1 + HER_GALLERY.length) % HER_GALLERY.length;
    setCurrentIndex(prevIdx);
    setSelectedPhoto(HER_GALLERY[prevIdx]);
  };

  return (
    <>
      <div className="flex flex-col h-full justify-between p-5 rounded-3xl bg-white dark:bg-slate-900 border border-blue-100 dark:border-blue-900/40 shadow-2xs group">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Camera className="w-4 h-4 text-blue-600 dark:text-blue-400" />
            <h3 className="font-serif text-sm font-bold text-slate-900 dark:text-blue-50">
              Her Photo Scrapbook ✨
            </h3>
          </div>
          <span className="text-[10px] text-slate-500 dark:text-slate-400 font-medium">
            Click to view full photo
          </span>
        </div>

        {/* 6-Photo Mini Bento Grid */}
        <div className="grid grid-cols-3 gap-2.5 my-auto">
          {HER_GALLERY.slice(0, 6).map((item, index) => (
            <div
              key={item.id}
              onClick={() => openPhoto(item, index)}
              className="group/photo relative aspect-square rounded-2xl overflow-hidden cursor-pointer bg-slate-100 dark:bg-slate-800 border border-blue-100/50 dark:border-blue-950 shadow-2xs hover:shadow-md transition-all duration-300 hover:scale-105"
            >
              <img
                src={item.src}
                alt={item.title}
                className="w-full h-full object-cover object-top transition-transform duration-500 group-hover/photo:scale-110"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-blue-950/80 via-transparent to-transparent opacity-0 group-hover/photo:opacity-100 transition-opacity flex items-end p-1.5">
                <span className="text-[9px] font-semibold text-white truncate drop-shadow-xs">
                  {item.title}
                </span>
              </div>
            </div>
          ))}
        </div>

        <button
          onClick={() => openPhoto(HER_GALLERY[0], 0)}
          className="w-full mt-3 py-2 px-3 rounded-2xl bg-blue-50 dark:bg-slate-800/80 border border-blue-200 dark:border-blue-900/60 hover:bg-blue-100 dark:hover:bg-slate-800 text-blue-700 dark:text-blue-300 font-semibold text-xs flex items-center justify-center gap-1.5 transition-colors"
        >
          <Sparkles className="w-3.5 h-3.5" />
          <span>Browse All 15 Curated Photos</span>
        </button>
      </div>

      {/* Full Photo Modal */}
      {selectedPhoto && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-fadeIn">
          <div className="relative w-full max-w-2xl rounded-3xl bg-[#FAF7F2] dark:bg-slate-900 border border-blue-200/60 dark:border-blue-900/50 shadow-2xl overflow-hidden flex flex-col md:flex-row max-h-[90vh]">
            <button
              onClick={() => setSelectedPhoto(null)}
              className="absolute top-4 right-4 z-20 p-2 rounded-full bg-black/50 hover:bg-black/70 text-white transition-colors"
            >
              <X className="w-4 h-4" />
            </button>

            <div className="relative md:w-1/2 bg-black flex items-center justify-center min-h-[300px]">
              <img
                src={selectedPhoto.src}
                alt={selectedPhoto.title}
                className="w-full h-full object-contain max-h-[60vh] md:max-h-[85vh]"
              />

              <button
                onClick={prevPhoto}
                className="absolute left-2 top-1/2 -translate-y-1/2 p-2 rounded-full bg-black/50 hover:bg-black/80 text-white transition-transform hover:scale-110"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                onClick={nextPhoto}
                className="absolute right-2 top-1/2 -translate-y-1/2 p-2 rounded-full bg-black/50 hover:bg-black/80 text-white transition-transform hover:scale-110"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>

            <div className="p-6 md:w-1/2 flex flex-col justify-between overflow-y-auto custom-scrollbar">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-[10px] uppercase font-bold tracking-wider px-2.5 py-0.5 rounded-full bg-blue-100 dark:bg-blue-950/80 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-900">
                    {selectedPhoto.category}
                  </span>
                  <span className="text-xs text-slate-500 dark:text-slate-400 font-medium">
                    {currentIndex + 1} of {HER_GALLERY.length}
                  </span>
                </div>

                <h3 className="font-serif text-2xl font-bold text-slate-900 dark:text-white mb-2">
                  {selectedPhoto.title}
                </h3>

                <p className="font-serif italic text-xs text-blue-600 dark:text-blue-400 mb-4">
                  &ldquo;{selectedPhoto.emotionVibe}&rdquo;
                </p>

                <div className="p-4 rounded-2xl bg-white dark:bg-slate-800 border border-blue-100 dark:border-blue-950 text-xs sm:text-sm text-slate-700 dark:text-slate-200 leading-relaxed mb-4">
                  <div className="font-semibold text-blue-700 dark:text-blue-300 mb-1 flex items-center gap-1.5">
                    <Heart className="w-3.5 h-3.5 fill-current" />
                    <span>Why You Look Unforgettable Here:</span>
                  </div>
                  {selectedPhoto.compliment}
                </div>

                <div className="p-3 rounded-2xl bg-blue-50/70 dark:bg-blue-950/40 border border-blue-200/60 dark:border-blue-900/40 text-xs font-serif italic text-slate-600 dark:text-slate-300">
                  &ldquo;{selectedPhoto.loveNote}&rdquo;
                </div>
              </div>

              <div className="mt-6 pt-4 border-t border-blue-100 dark:border-blue-950 flex items-center justify-between text-xs text-slate-500">
                <span>Photographed with grace</span>
                <span className="text-blue-600 dark:text-blue-400 font-semibold">Forever Cherished ✨</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
