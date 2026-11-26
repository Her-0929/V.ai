'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Menu,
  X,
  Heart,
  MessageSquareHeart,
  Mail,
  Camera,
  Feather,
  Sparkles,
  Music,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { HER_COMPANION, CUTE_COMPLIMENTS } from '../../lib/herData';

const NAV_ITEMS = [
  { name: 'Heart to Heart', href: '/', icon: MessageSquareHeart },
  { name: 'Open When Letters', href: '/memories', icon: Mail },
  { name: 'Moments Scrapbook', href: '/timeline', icon: Camera },
  { name: 'Wish Capsule', href: '/ingest', icon: Feather },
  { name: 'All About You', href: '/profile', icon: Sparkles },
];

export function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [complimentIdx, setComplimentIdx] = useState(0);
  const pathname = usePathname();
  const { user } = useAuth();

  // Cycle through sweet compliments in header
  useEffect(() => {
    const timer = setInterval(() => {
      setComplimentIdx((prev) => (prev + 1) % CUTE_COMPLIMENTS.length);
    }, 7000);
    return () => clearInterval(timer);
  }, []);

  // Close mobile menu on route change
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [pathname]);

  return (
    <>
      <header className="h-16 border-b border-[#E8DFD5] dark:border-[#2C2926] bg-[#FAF7F2]/90 dark:bg-[#151413]/90 backdrop-blur-md sticky top-0 z-30 px-4 sm:px-6 flex items-center justify-between">
        {/* Mobile brand & toggle */}
        <div className="flex items-center gap-3 md:hidden">
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 rounded-xl text-[#61554D] hover:bg-[#EFE7DC] dark:hover:bg-[#272421]"
            aria-label="Toggle Navigation"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
          <Link href="/" className="flex items-center gap-2.5">
            <div className="relative w-9 h-9 rounded-xl overflow-hidden ring-2 ring-rose-400/50 bg-[#E07A5F] shadow-xs">
              <img
                src={HER_COMPANION.avatarSm}
                alt="You"
                className="w-full h-full object-cover object-top"
              />
            </div>
            <div>
              <span className="font-serif text-lg font-bold text-[#2C2623] dark:text-[#F7F3EE] block leading-tight">
                For You 💖
              </span>
              <span className="text-[10px] text-rose-500 font-medium">Your private world</span>
            </div>
          </Link>
        </div>

        {/* Desktop Love Note / Floating Compliment */}
        <div className="hidden md:flex items-center gap-2.5 max-w-md truncate">
          <span className="w-2 h-2 rounded-full bg-rose-400 animate-ping" />
          <span className="text-xs font-serif italic text-[#7C6E64] dark:text-[#C4B7AE] truncate transition-all duration-500">
            &ldquo;{CUTE_COMPLIMENTS[complimentIdx]}&rdquo;
          </span>
        </div>

        {/* Right side romantic pills */}
        <div className="flex items-center gap-2.5">
          {/* Letters shortcut pill */}
          <Link
            href="/memories"
            className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-rose-50 dark:bg-rose-950/40 text-rose-700 dark:text-rose-300 border border-rose-200 dark:border-rose-800 text-xs font-semibold hover:bg-rose-100 transition-all shadow-2xs group"
          >
            <Mail className="w-3.5 h-3.5 text-rose-500 group-hover:scale-110 transition-transform" />
            <span>Open Letters 💌</span>
          </Link>

          {/* Sweet Tribute Capsule */}
          <Link
            href="/profile"
            className="flex items-center gap-2 p-1 pl-1 pr-3 rounded-full bg-white dark:bg-[#201D1B] border border-[#E8DFD5] dark:border-[#38332E] hover:border-rose-300 transition-all shadow-2xs group"
            title="A tribute made with love"
          >
            <div className="relative w-8 h-8 rounded-full overflow-hidden ring-2 ring-rose-300 dark:ring-rose-900 group-hover:scale-105 transition-transform bg-[#E07A5F]">
              <img
                src={HER_COMPANION.avatarSm}
                alt="You"
                className="w-full h-full object-cover object-top"
              />
              <span className="absolute bottom-0 right-0 w-2.5 h-2.5 rounded-full bg-rose-500 ring-1.5 ring-white dark:ring-[#201D1B]" />
            </div>
            <div className="flex flex-col text-left">
              <span className="text-xs font-serif font-bold text-[#2C2623] dark:text-[#EAE3DC] leading-tight">
                To You ✨
              </span>
              <span className="text-[9px] text-rose-500 dark:text-rose-400 font-medium leading-none">
                Special & Loved
              </span>
            </div>
          </Link>
        </div>
      </header>

      {/* Mobile drawer overlay */}
      {mobileMenuOpen && (
        <div className="md:hidden fixed inset-0 z-40 bg-black/50 backdrop-blur-xs flex">
          <div className="w-72 bg-[#FAF7F2] dark:bg-[#1A1816] h-full p-5 flex flex-col shadow-2xl">
            <div className="flex items-center justify-between pb-4 border-b border-[#E8DFD5] dark:border-[#2C2926]">
              <div className="flex items-center gap-3">
                <div className="relative w-11 h-11 rounded-2xl overflow-hidden ring-2 ring-rose-400/50 bg-[#E07A5F] shadow-sm">
                  <img
                    src={HER_COMPANION.avatarSm}
                    alt="You"
                    className="w-full h-full object-cover object-top"
                  />
                </div>
                <div>
                  <span className="font-serif text-xl font-bold text-[#2C2623] dark:text-[#F7F3EE] block leading-tight">
                    For You 💖
                  </span>
                  <span className="text-[11px] text-rose-500 font-medium">
                    A world made just for you
                  </span>
                </div>
              </div>
              <button
                onClick={() => setMobileMenuOpen(false)}
                className="p-1.5 rounded-xl text-[#61554D] hover:bg-[#EFE7DC]"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <nav className="flex-1 py-4 space-y-2">
              {NAV_ITEMS.map((item) => {
                const isActive =
                  pathname === item.href ||
                  (item.href !== '/' && pathname.startsWith(item.href));
                const Icon = item.icon;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`flex items-center gap-3 px-3.5 py-3 rounded-2xl text-sm font-medium ${
                      isActive
                        ? 'bg-white dark:bg-[#272421] text-[#D96B43] shadow-xs border border-[#E8DFD5]'
                        : 'text-[#61554D] dark:text-[#B3A69C]'
                    }`}
                  >
                    <Icon className="w-4 h-4 text-rose-500" />
                    <span>{item.name}</span>
                  </Link>
                );
              })}
            </nav>

            <div className="p-4 rounded-2xl bg-rose-50/70 dark:bg-rose-950/20 border border-rose-200/60 dark:border-rose-900/40 text-center text-xs text-rose-800 dark:text-rose-300 font-serif italic">
              &ldquo;Made with love for the one with the brightest smile.&rdquo;
            </div>
          </div>
          <div className="flex-1" onClick={() => setMobileMenuOpen(false)} />
        </div>
      )}
    </>
  );
}
