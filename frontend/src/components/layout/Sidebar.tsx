'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  MessageSquare,
  Clock,
  Compass,
  UploadCloud,
  User,
  Heart,
  Sparkles,
} from 'lucide-react';

const NAV_ITEMS = [
  {
    name: 'Home / Chat',
    href: '/',
    icon: MessageSquare,
    description: 'Conversation with HER',
  },
  {
    name: 'Memory Timeline',
    href: '/timeline',
    icon: Clock,
    description: 'Chronological timeline',
  },
  {
    name: 'Memory Explorer',
    href: '/memories',
    icon: Compass,
    description: 'Browse & provenance',
  },
  {
    name: 'Upload Memories',
    href: '/ingest',
    icon: UploadCloud,
    description: 'Notes, letters & files',
  },
  {
    name: 'Profile & Settings',
    href: '/profile',
    icon: User,
    description: 'Preferences & privacy',
  },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden md:flex flex-col w-64 lg:w-72 border-r border-[#E8DFD5] dark:border-[#2C2926] bg-[#F7F2EC] dark:bg-[#1A1816] h-screen sticky top-0 p-5 shrink-0 transition-colors">
      {/* Brand Header */}
      <div className="flex items-center gap-3 px-2 py-3 mb-6">
        <div className="w-10 h-10 rounded-2xl bg-[#E07A5F] flex items-center justify-center text-white shadow-sm shadow-[#E07A5F]/30">
          <Heart className="w-5 h-5 fill-white/80" />
        </div>
        <div>
          <div className="flex items-center gap-1.5">
            <span className="font-serif text-xl font-medium tracking-tight text-[#2C2623] dark:text-[#F7F3EE]">
              HER AI
            </span>
            <span className="text-[10px] font-medium tracking-wider px-1.5 py-0.5 rounded-full bg-[#E07A5F]/10 text-[#D96B43] dark:bg-[#E07A5F]/20 dark:text-[#EB8D74] border border-[#E07A5F]/20">
              v0.4.0
            </span>
          </div>
          <p className="text-xs text-[#85776E] dark:text-[#A0938A] font-sans">
            Personal AI Companion
          </p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 space-y-1.5">
        <div className="px-2 pb-2 text-[11px] font-semibold tracking-wider text-[#A39489] uppercase">
          Navigation
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
              className={`group flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all duration-150 ${
                isActive
                  ? 'bg-white dark:bg-[#272421] text-[#D96B43] dark:text-[#EB8D74] shadow-sm border border-[#E8DFD5] dark:border-[#38332E]'
                  : 'text-[#61554D] dark:text-[#B3A69C] hover:bg-[#EFE8DF] dark:hover:bg-[#23201D] hover:text-[#2C2623] dark:hover:text-[#F7F3EE]'
              }`}
            >
              <Icon
                className={`w-4 h-4 transition-transform duration-150 group-hover:scale-105 ${
                  isActive
                    ? 'text-[#D96B43] dark:text-[#EB8D74]'
                    : 'text-[#8C7E74] dark:text-[#8C7E74]'
                }`}
              />
              <div className="flex-1">
                <span className="block leading-none">{item.name}</span>
              </div>
              {isActive && (
                <div className="w-1.5 h-1.5 rounded-full bg-[#D96B43] dark:bg-[#EB8D74]" />
              )}
            </Link>
          );
        })}
      </nav>

      {/* Companion Presence Card */}
      <div className="mt-auto p-4 rounded-2xl bg-white/70 dark:bg-[#23201D]/70 border border-[#E8DFD5] dark:border-[#332E2A] backdrop-blur-sm">
        <div className="flex items-center gap-2 mb-2">
          <Sparkles className="w-4 h-4 text-[#E07A5F]" />
          <span className="text-xs font-medium text-[#2C2623] dark:text-[#EFEAE4]">
            RAG & Empathy Active
          </span>
        </div>
        <p className="text-[11px] text-[#7C6E64] dark:text-[#9E9086] leading-relaxed">
          Grounding replies with temporal memories and emotional sensitivity.
        </p>
      </div>
    </aside>
  );
}
