'use client';

import React from 'react';
import { Brain, MessageSquare, Calendar, Shield } from 'lucide-react';
import { ProfileResponse } from '../../types/api';
import { formatDate } from '../../lib/utils';

interface StatsOverviewProps {
  profile: ProfileResponse;
}

export function StatsOverview({ profile }: StatsOverviewProps) {
  const stats = [
    {
      title: 'Stored Memories',
      value: profile.memory_count,
      description: 'Facts, dates & life events',
      icon: Brain,
      color: 'text-[#D96B43]',
      bg: 'bg-[#FAF2EB] dark:bg-[#2C211A]',
    },
    {
      title: 'Conversations',
      value: profile.conversation_count,
      description: 'Dialogue sessions with HER',
      icon: MessageSquare,
      color: 'text-amber-600 dark:text-amber-400',
      bg: 'bg-amber-50 dark:bg-amber-950/40',
    },
    {
      title: 'Companion Since',
      value: formatDate(profile.user.created_at),
      description: 'Account activation date',
      icon: Calendar,
      color: 'text-emerald-600 dark:text-emerald-400',
      bg: 'bg-emerald-50 dark:bg-emerald-950/40',
    },
    {
      title: 'Privacy Scope',
      value: 'Tenant Isolated',
      description: 'Argon2id + Row-level security',
      icon: Shield,
      color: 'text-sky-600 dark:text-sky-400',
      bg: 'bg-sky-50 dark:bg-sky-950/40',
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
