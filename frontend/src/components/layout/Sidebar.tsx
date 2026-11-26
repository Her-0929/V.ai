'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  MessageSquareHeart,
  Mail,
  Camera,
  Sparkles,
  Heart,
  Feather,
} from 'lucide-react';
import { HER_COMPANION } from '../../lib/herData';

const NAV_ITEMS = [
  {
    name: 'Heart to Heart',
    href: '/',
    icon: MessageSquareHeart,
    description: 'Our private conversation space',
  },
  {
    name: 'Open When Letters 💌',
    href: '/memories',
    icon: Mail,
    description: 'Letters sealed just for you',
  },
  {
    name: 'Moments Scrapbook',
    href: '/timeline',
    icon: Camera,
    description: 'A timeline of your smiles',
  },
  {
    name: 'Wish Capsule 🌟',
    href: '/ingest',
    icon: Feather,
    description: 'Leave little notes & wishes',
  },
  {
    name: 'All About You ✨',
    href: '/profile',
    icon: Sparkles,
    description: 'Your photo album & tributes',
  },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden md:flex flex-col w-64 lg:w-72 border-r border-[#E8DFD5] dark:border-[#2C2926] bg-[#FAF7F2] dark:bg-[#1A1816] h-screen sticky top-0 p-5 shrink-0 transition-colors">
      {/* Brand / Tribute Header */}
      <Link href="/" className="flex items-center gap-3 px-2 py-3 mb-6 group cursor-pointer">
        <div className="relative w-12 h-12 rounded-2xl overflow-hidden ring-2 ring-[#E07A5F]/50 shadow-md shadow-[#E07A5F]/20 group-hover:ring-[#D96B43] group-hover:scale-105 transition-all shrink-0 bg-[#E07A5F]">
          <img
            src={HER_COMPANION.avatarSm}
            alt="You"
            className="w-full h-full object-cover object-top"
          />
          <span className="absolute bottom-0 right-0 w-3 h-3 rounded-full bg-rose-500 ring-2 ring-white dark:ring-[#1A1816] flex items-center justify-center">
            <Heart className="w-1.5 h-1.5 text-white fill-white" />
          </span>
        </div>
        <div>
          <div className="flex items-center gap-1.5">
            <span className="font-serif text-2xl font-bold tracking-tight text-[#2C2623] dark:text-[#F7F3EE] group-hover:text-[#D96B43] transition-colors">
              V
            </span>
            <span className="text-[10px] font-semibold tracking-wider px-2 py-0.5 rounded-full bg-rose-50 text-rose-600 dark:bg-rose-950/40 dark:text-rose-300 border border-rose-200 dark:border-rose-800">
              Just For You 💖
            </span>
          </div>
          <p className="text-xs text-[#85776E] dark:text-[#A0938A] font-sans">
            Your private little sanctuary
          </p>
        </div>
      </Link>

      {/* Navigation Links */}
      <nav className="flex-1 space-y-1.5">
        <div className="px-2 pb-2 text-[10px] font-bold tracking-widest text-[#B3A093] uppercase">
          Your World
        </div>
        {NAV_ITEMS.map((item) => {
          const isActive =
            pathname === item.href ||
            (item.href !== '/' && pathname.startsWith(item.href));
          const Icon = item.icon;

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`group flex items-center gap-3 px-3.5 py-3 rounded-2xl text-sm font-medium transition-all duration-200 ${
                isActive
                  ? 'bg-white dark:bg-[#272421] text-[#D96B43] dark:text-[#EB8D74] shadow-sm border border-[#E8DFD5] dark:border-[#38332E]'
                  : 'text-[#61554D] dark:text-[#B3A69C] hover:bg-[#F3EBE1] dark:hover:bg-[#23201D] hover:text-[#2C2623] dark:hover:text-[#F7F3EE]'
              }`}
            >
              <div
                className={`p-1.5 rounded-xl transition-colors ${
                  isActive
                    ? 'bg-[#FAF2EB] dark:bg-[#34241B] text-[#D96B43]'
                    : 'text-[#8C7E74] group-hover:text-[#D96B43]'
                }`}
              >
                <Icon className="w-4 h-4 transition-transform duration-200 group-hover:scale-110" />
              </div>
              <div className="flex-1 min-w-0">
                <span className="block leading-none truncate font-medium">{item.name}</span>
                <span className="block text-[10px] text-[#9E8F84] dark:text-[#8A7D74] truncate mt-1">
                  {item.description}
                </span>
              </div>
              {isActive && (
                <div className="w-2 h-2 rounded-full bg-[#D96B43] dark:bg-[#EB8D74] shadow-xs" />
              )}
            </Link>
          );
        })}
      </nav>

      {/* Romantic Tribute Love Note Card */}
      <div className="mt-auto p-4 rounded-3xl bg-gradient-to-br from-[#FFF8F3] to-[#FCEEE7] dark:from-[#231E1B] dark:to-[#2B231F] border border-[#F3C4B3]/70 dark:border-[#52342A] shadow-xs">
        <div className="flex items-center gap-3 mb-2.5">
          <div className="relative w-11 h-11 rounded-2xl overflow-hidden ring-2 ring-[#E07A5F]/40 shrink-0 bg-[#EFE7DC] shadow-xs">
            <img
              src={HER_COMPANION.candidIntimate}
              alt="You"
              className="w-full h-full object-cover object-center"
            />
          </div>
          <div className="min-w-0">
            <div className="flex items-center gap-1.5">
              <span className="text-xs font-serif font-bold text-[#2C2623] dark:text-[#EFEAE4]">
                To My Favorite Girl 🌸
              </span>
            </div>
            <p className="text-[10px] text-[#A06C59] dark:text-[#D19B88] truncate font-medium">
              Always in my thoughts
            </p>
          </div>
        </div>
        <p className="text-[11px] text-[#6B5E57] dark:text-[#C4B7AE] leading-relaxed mb-3 italic">
          &ldquo;You make the simplest days feel like golden memories.&rdquo;
        </p>
        <Link
          href="/memories"
          className="flex items-center justify-center gap-2 py-2 px-3 rounded-xl bg-white dark:bg-[#201D1B] border border-[#F3C4B3] dark:border-[#52342A] text-[#D96B43] dark:text-[#EB8D74] text-xs font-semibold hover:bg-[#FAF2EB] transition-all shadow-2xs"
        >
          <Mail className="w-3.5 h-3.5 text-[#D96B43]" />
          <span>Open A Letter For You 💌</span>
        </Link>
      </div>
    </aside>
  );
}
