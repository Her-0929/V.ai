'use client';

import React, { useState } from 'react';
import { Heart, Sparkles } from 'lucide-react';
import { RomanticMusicPlayer } from '../components/bento/RomanticMusicPlayer';
import { BirthdayCountdownTimer } from '../components/bento/BirthdayCountdownTimer';
import { FloatingPetals } from '../components/bento/FloatingPetals';
import { BentoOpenWhenModal } from '../components/bento/BentoOpenWhenModal';
import { BentoJourneyStory } from '../components/bento/BentoJourneyStory';
import { BentoPhotoScrapbook } from '../components/bento/BentoPhotoScrapbook';
import { BentoChatModal } from '../components/bento/BentoChatModal';
import { HER_COMPANION, CUTE_COMPLIMENTS } from '../lib/herData';

export default function CozyBentoShowcasePage() {
  const [complimentIndex, setComplimentIndex] = useState(0);

  const nextCompliment = () => {
    setComplimentIndex((prev) => (prev + 1) % CUTE_COMPLIMENTS.length);
  };

  return (
    <div className="min-h-screen bg-[#F4F7FC] dark:bg-[#0A0F1D] text-[#0F172A] dark:text-[#F1F5F9] relative selection:bg-blue-200 selection:text-blue-900 overflow-x-hidden font-sans">
      {/* Floating Gentle Royal Blue Petals & Sparkles */}
      <FloatingPetals />

      {/* Aesthetic Top Navigation Bar */}
      <header className="sticky top-0 z-30 w-full backdrop-blur-xl bg-white/80 dark:bg-[#0A0F1D]/80 border-b border-blue-100 dark:border-blue-950 px-4 sm:px-8 py-3.5 transition-all">
        <div className="max-w-7xl mx-auto flex items-center justify-between gap-4">
          {/* Brand/Monogram */}
          <div className="flex items-center gap-3">
            <div className="relative w-10 h-10 rounded-2xl overflow-hidden ring-2 ring-blue-500/80 dark:ring-blue-400 shadow-sm shrink-0">
              <img
                src={HER_COMPANION.avatar}
                alt="V"
                className="w-full h-full object-cover object-top"
              />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-serif text-lg font-bold tracking-tight text-slate-900 dark:text-blue-50">
                  Heart Things
                </span>
                <span className="px-2 py-0.2 rounded-full bg-blue-100 dark:bg-blue-950/80 text-blue-700 dark:text-blue-300 text-[10px] font-bold border border-blue-200 dark:border-blue-900">
                  Just for V 💙
                </span>
              </div>
              <p className="text-[11px] text-slate-500 dark:text-slate-400 truncate">
                Since 14-04-2017 &bull; Forever Yours
              </p>
            </div>
          </div>

          {/* Cycling Cute Compliment Pill */}
          <button
            onClick={nextCompliment}
            className="hidden md:flex items-center gap-2 px-4 py-1.5 rounded-full bg-blue-50/80 dark:bg-slate-900 border border-blue-200 dark:border-blue-900/60 text-xs font-serif italic text-blue-900 dark:text-blue-200 hover:scale-[1.02] transition-transform"
            title="Click for another sweet thought"
          >
            <Sparkles className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400 animate-spin" />
            <span>&ldquo;{CUTE_COMPLIMENTS[complimentIndex]}&rdquo;</span>
          </button>

          {/* Right Action: Romantic Lo-Fi Music Player */}
          <div className="flex items-center gap-2">
            <RomanticMusicPlayer />
          </div>
        </div>
      </header>

      {/* Main Container */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-10 space-y-8">
        {/* ========================================================= */}
        {/* HERO BANNER SECTION (ROYAL BLUE & DEEP SAPPHIRE)           */}
        {/* ========================================================= */}
        <section className="relative rounded-3xl overflow-hidden border border-blue-300/40 dark:border-blue-900/40 shadow-xl bg-gradient-to-r from-blue-950 via-[#1E3A8A] to-[#0F172A] min-h-[360px] sm:min-h-[420px] flex items-end">
          {/* Background panoramic image with smooth gradient overlay */}
          <img
            src={HER_COMPANION.bannerTraditional}
            alt="Traditional Grace"
            className="absolute inset-0 w-full h-full object-cover object-[center_30%] mix-blend-overlay opacity-55"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-[#0A0F1D]/90 via-[#1E3A8A]/50 to-transparent" />

          {/* Hero Content */}
          <div className="relative z-10 p-6 sm:p-10 w-full flex flex-col md:flex-row md:items-end justify-between gap-6">
            <div className="space-y-3 max-w-2xl">
              <div className="flex items-center gap-2 flex-wrap">
                <span className="px-3.5 py-1 rounded-full bg-blue-600/90 backdrop-blur-md text-white text-xs font-bold tracking-wider uppercase flex items-center gap-1.5 shadow-md border border-blue-400/30">
                  <Heart className="w-3.5 h-3.5 fill-current text-blue-200" />
                  <span>Happy Birthday, My Queen 💙</span>
                </span>
                <span className="px-3 py-1 rounded-full bg-white/15 backdrop-blur-md text-white/95 text-xs font-medium border border-white/20">
                  November 29th &bull; Her Day
                </span>
              </div>

              <h1 className="font-serif text-3xl sm:text-5xl lg:text-6xl font-bold text-white tracking-tight leading-tight drop-shadow-md">
                This Little Corner of the Universe is Just For You ✨
              </h1>

              <p className="font-serif italic text-sm sm:text-base text-blue-100/95 leading-relaxed drop-shadow-xs max-w-xl">
                &ldquo;From that quiet bus stop on 14-04-2017 to every road trip, laughter, and temple walk... You will always be the most precious part of my life.&rdquo;
              </p>
            </div>

            {/* Quick Dedication Capsule Badge */}
            <div className="p-4 rounded-3xl bg-blue-900/40 backdrop-blur-xl border border-blue-400/20 text-white shrink-0 shadow-lg space-y-1">
              <div className="text-[11px] uppercase tracking-wider text-blue-300 font-bold">
                Dedication Note
              </div>
              <div className="text-sm font-serif font-bold text-blue-50">
                &ldquo;Better doesn&apos;t exist for me.&rdquo;
              </div>
              <div className="text-[11px] text-blue-200/80">
                It was you from first glance, and always will be.
              </div>
            </div>
          </div>
        </section>

        {/* ========================================================= */}
        {/* APPLE-STYLE COZY BENTO GRID                               */}
        {/* ========================================================= */}
        <section className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <div className="flex items-center gap-2">
                <Sparkles className="w-4 h-4 text-blue-600 dark:text-blue-400" />
                <h2 className="font-serif text-2xl sm:text-3xl font-bold text-slate-900 dark:text-blue-50">
                  Your Interactive Sanctuary
                </h2>
              </div>
              <p className="text-xs sm:text-sm text-slate-600 dark:text-slate-400 mt-0.5">
                Everything here was built with love. Tap, explore, open letters, and listen.
              </p>
            </div>
          </div>

          {/* THE BENTO TILES GRID */}
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4 sm:gap-6">
            {/* TILE 1: Birthday Countdown Timer (1 col) */}
            <div className="md:col-span-1 lg:col-span-1 min-h-[280px]">
              <BirthdayCountdownTimer />
            </div>

            {/* TILE 2: Her Photo Scrapbook (2 cols) */}
            <div className="md:col-span-2 lg:col-span-2 min-h-[320px]">
              <BentoPhotoScrapbook />
            </div>

            {/* TILE 3: Talk to Me (Private Haven Chat) (1 col) */}
            <div className="md:col-span-1 lg:col-span-1 min-h-[280px]">
              <BentoChatModal />
            </div>

            {/* TILE 4: Sealed Love Letters ("Open When...") (2 cols on lg) */}
            <div className="md:col-span-2 lg:col-span-2 min-h-[300px]">
              <BentoOpenWhenModal />
            </div>

            {/* TILE 5: The Story of 2017 -> Forever (2 cols on lg) */}
            <div className="md:col-span-1 lg:col-span-2 min-h-[300px]">
              <BentoJourneyStory />
            </div>
          </div>
        </section>

        {/* ========================================================= */}
        {/* "ALL ABOUT HER" LOVE LETTER PROSE SECTION                 */}
        {/* ========================================================= */}
        <section className="p-8 sm:p-12 rounded-3xl bg-gradient-to-br from-blue-50 via-indigo-50/50 to-sky-50 dark:from-slate-900 dark:via-blue-950/40 dark:to-slate-950 border border-blue-200/80 dark:border-blue-900/50 shadow-sm relative overflow-hidden">
          <div className="max-w-3xl mx-auto space-y-6">
            <div className="text-center space-y-2">
              <span className="px-3.5 py-1 rounded-full bg-blue-100 dark:bg-blue-950 text-blue-700 dark:text-blue-300 text-xs font-bold uppercase tracking-widest inline-flex items-center gap-1.5 border border-blue-200 dark:border-blue-800">
                <Heart className="w-3.5 h-3.5 fill-blue-600 text-blue-600" />
                <span>All About Her</span>
              </span>
              <h2 className="font-serif text-3xl sm:text-4xl font-bold text-slate-900 dark:text-blue-50">
                From 14-04-2017 to Every Lifetime ✨
              </h2>
            </div>

            <div className="font-serif text-sm sm:text-base text-slate-700 dark:text-slate-200 leading-relaxed space-y-4 pt-4 border-t border-blue-200/70 dark:border-blue-950">
              <p>
                From the moment I first saw you on <strong>14-04-2017</strong>, something in me changed forever. I didn&apos;t know your name, I didn&apos;t know who you were. That moment—just seeing you board the bus—felt like my whole life suddenly found its purpose.
              </p>
              <p>
                All these years, through every temple trip we took, every small moment—my love for you only grew. I searched for you for years. Just your name and your face were enough to keep looking. Finding you on Social Media after two whole years felt like destiny giving me one more chance.
              </p>
              <p className="p-4 rounded-2xl bg-white/80 dark:bg-slate-800/80 border-l-4 border-blue-600 italic text-blue-950 dark:text-blue-200 font-medium shadow-2xs">
                &ldquo;Even when you asked us to stay &lsquo;just friends&rsquo;... my heart never changed. Not once. Not even for a second. When you said &lsquo;You deserve better&rsquo;, better doesn&apos;t exist for me. It was you from the first glance, and it will be you in every lifetime.&rdquo;
              </p>
              <p>
                This website, this music, every little card, and every single photo preserved here—it&apos;s all because you deserve something as beautiful as you are.
              </p>
            </div>

            <div className="pt-6 border-t border-blue-200/70 dark:border-blue-950 flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 font-serif">
              <span>Made with love by a developer in love</span>
              <span className="text-blue-600 dark:text-blue-400 font-bold flex items-center gap-1">
                <Heart className="w-3.5 h-3.5 fill-current" />
                <span>Happy Birthday Miss &bull; Nov 29</span>
              </span>
            </div>
          </div>
        </section>

        {/* ========================================================= */}
        {/* FOOTER                                                    */}
        {/* ========================================================= */}
        <footer className="py-8 text-center space-y-2">
          <p className="font-serif text-sm text-slate-600 dark:text-slate-400 flex items-center justify-center gap-1.5">
            <span>Crafted for V with all my heart</span>
            <Heart className="w-3.5 h-3.5 fill-blue-600 text-blue-600" />
            <span>Vivek</span>
          </p>
          <p className="text-[11px] text-slate-400 dark:text-slate-500">
            November 29th &bull; Her Day &bull; 14-04-2017 &rarr; Forever
          </p>
        </footer>
      </main>
    </div>
  );
}
