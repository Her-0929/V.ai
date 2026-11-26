'use client';

import React from 'react';
import { Heart, Sparkles, Cake, Compass } from 'lucide-react';
import { ProfileResponse } from '../../types/api';

interface StatsOverviewProps {
  profile: ProfileResponse;
}

export function StatsOverview({ profile }: StatsOverviewProps) {
  const stats = [
    {
      title: 'Moments Preserved',
      value: `${profile.memory_count > 0 ? profile.memory_count : 19}+`,
      description: 'Photos, milestones & dates',
      icon: Sparkles,
      color: 'text-[#D96B43]',
      bg: 'bg-[#FAF2EB] dark:bg-[#2C211A]',
    },
    {
      title: 'Our Special Day',
      value: 'Nov 29',
      description: 'Her Birthday 🎂',
      icon: Cake,
      color: 'text-rose-500 dark:text-rose-400',
      bg: 'bg-rose-50 dark:bg-rose-950/40',
    },
    {
      title: 'Since First Glance',
      value: '14-04-2017',
      description: 'Bus stop in yellow dress ✨',
      icon: Compass,
      color: 'text-amber-600 dark:text-amber-400',
      bg: 'bg-amber-50 dark:bg-amber-950/40',
    },
    {
      title: 'Dedication',
      value: 'Forever',
      description: 'Made with love by Vivek',
      icon: Heart,
      color: 'text-pink-600 dark:text-pink-400',
      bg: 'bg-pink-50 dark:bg-pink-950/40',
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      {stats.map((stat, i) => {
        const Icon = stat.icon;
        return (
          <div
            key={i}
            className="p-5 rounded-3xl bg-white dark:bg-[#201D1B] border border-[#EAE2D8] dark:border-[#38332E] shadow-2xs space-y-3"
          >
            <div className="flex items-center justify-between">
              <span className="text-xs font-semibold text-[#8C7E74] dark:text-[#A89C94] uppercase tracking-wider">
                {stat.title}
              </span>
              <div
                className={`w-8 h-8 rounded-xl ${stat.bg} ${stat.color} flex items-center justify-center`}
              >
                <Icon className="w-4 h-4" />
              </div>
            </div>
            <div>
              <div className="font-serif text-2xl font-semibold text-[#2C2623] dark:text-[#F7F3EE]">
                {stat.value}
              </div>
              <div className="text-[11px] text-[#A89C94] mt-0.5">{stat.description}</div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
