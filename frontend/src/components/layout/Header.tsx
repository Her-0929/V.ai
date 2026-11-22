'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  Menu,
  X,
  Heart,
  MessageSquare,
  Clock,
  Compass,
  UploadCloud,
  User as UserIcon,
  Activity,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

const NAV_ITEMS = [
  { name: 'Chat', href: '/', icon: MessageSquare },
  { name: 'Timeline', href: '/timeline', icon: Clock },
  { name: 'Explorer', href: '/memories', icon: Compass },
  { name: 'Upload', href: '/ingest', icon: UploadCloud },
  { name: 'Profile', href: '/profile', icon: UserIcon },
];

export function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [isBackendHealthy, setIsBackendHealthy] = useState<boolean | null>(null);
  const pathname = usePathname();
  const { user } = useAuth();

  useEffect(() => {
    // Check backend health
    const checkHealth = async () => {
      try {
        const res = await fetch('http://localhost:8000/health');
        if (res.ok) {
          setIsBackendHealthy(true);
        } else {
          setIsBackendHealthy(false);
        }
      } catch {
        setIsBackendHealthy(false);
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 30000);
    return () => clearInterval(interval);
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
          <Link href="/" className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-xl bg-[#E07A5F] flex items-center justify-center text-white">
              <Heart className="w-3.5 h-3.5 fill-white/80" />
            </div>
            <span className="font-serif text-lg font-medium text-[#2C2623] dark:text-[#F7F3EE]">
              HER AI
            </span>
          </Link>
        </div>

        {/* Desktop title / location indicator */}
        <div className="hidden md:flex items-center gap-2">
          <span className="text-xs uppercase font-medium tracking-widest text-[#9C8E85]">
            Companion Space
          </span>
          <span className="text-stone-300 dark:text-stone-700">/</span>
          <span className="text-sm font-medium text-[#4A4039] dark:text-[#D1C6BD] capitalize">
            {pathname === '/' ? 'Conversation' : pathname.replace('/', '')}
          </span>
        </div>

        {/* Right side controls */}
        <div className="flex items-center gap-3">
          {/* Backend Status indicator */}
          <div
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium border ${
              isBackendHealthy === true
                ? 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-700 dark:text-emerald-300 border-emerald-200 dark:border-emerald-800'
                : isBackendHealthy === false
                ? 'bg-rose-50 dark:bg-rose-950/40 text-rose-700 dark:text-rose-300 border-rose-200 dark:border-rose-800'
                : 'bg-stone-100 dark:bg-stone-800 text-stone-600 dark:text-stone-400 border-stone-200 dark:border-stone-700'
            }`}
            title={
              isBackendHealthy === true
                ? 'Backend connected (http://localhost:8000)'
                : 'Backend unreachable'
            }
          >
            <Activity className="w-3 h-3 animate-pulse" />
            <span className="hidden sm:inline">
              {isBackendHealthy === true ? 'Backend Connected' : 'Backend Offline'}
            </span>
            <span className="sm:hidden">
              {isBackendHealthy === true ? 'Online' : 'Offline'}
            </span>
          </div>

          {/* User Profile Capsule */}
          <Link
            href="/profile"
            className="flex items-center gap-2 p-1.5 pl-2.5 rounded-full bg-white dark:bg-[#272421] border border-[#E8DFD5] dark:border-[#38332E] hover:border-[#D96B43]/50 transition-colors shadow-2xs"
          >
            <span className="text-xs font-medium text-[#4A4039] dark:text-[#EAE3DC] max-w-[100px] truncate">
              {user?.username || 'Guest'}
            </span>
            <div className="w-6 h-6 rounded-full bg-[#EFE7DC] dark:bg-[#38332E] flex items-center justify-center text-[#D96B43] dark:text-[#EB8D74] text-xs font-semibold">
              {(user?.username || 'V')[0].toUpperCase()}
            </div>
          </Link>
        </div>
      </header>

      {/* Mobile drawer overlay */}
      {mobileMenuOpen && (
        <div className="md:hidden fixed inset-0 z-40 bg-black/40 backdrop-blur-xs flex">
          <div className="w-64 bg-[#F7F2EC] dark:bg-[#1A1816] h-full p-5 flex flex-col shadow-2xl">
            <div className="flex items-center justify-between pb-4 border-b border-[#E8DFD5] dark:border-[#2C2926]">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-xl bg-[#E07A5F] flex items-center justify-center text-white">
                  <Heart className="w-4 h-4 fill-white/80" />
                </div>
                <span className="font-serif text-lg font-medium text-[#2C2623] dark:text-[#F7F3EE]">
                  HER AI
                </span>
              </div>
              <button
                onClick={() => setMobileMenuOpen(false)}
                className="p-1 rounded-lg text-[#61554D] hover:bg-[#EFE7DC]"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <nav className="flex-1 py-4 space-y-1">
              {NAV_ITEMS.map((item) => {
                const isActive =
                  pathname === item.href ||
                  (item.href !== '/' && pathname.startsWith(item.href));
                const Icon = item.icon;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium ${
                      isActive
                        ? 'bg-white dark:bg-[#272421] text-[#D96B43] shadow-xs'
                        : 'text-[#61554D] dark:text-[#B3A69C]'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    <span>{item.name}</span>
                  </Link>
                );
              })}
            </nav>

            <div className="pt-4 border-t border-[#E8DFD5] dark:border-[#2C2926] text-xs text-[#85776E]">
              Logged in as: <strong className="text-[#2C2623] dark:text-white">{user?.username}</strong>
            </div>
          </div>
          <div className="flex-1" onClick={() => setMobileMenuOpen(false)} />
        </div>
      )}
    </>
  );
}
