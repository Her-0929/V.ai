'use client';

import React from 'react';
import Link from 'next/link';
import {
  FileText,
  Star,
  ExternalLink,
  Tag,
} from 'lucide-react';
import { MemoryTimelineItem } from '../../types/api';
import { Badge } from '../ui/Badge';
import { formatPrecision } from '../../lib/utils';

interface TimelineCardProps {
  item: MemoryTimelineItem;
}

export function TimelineCard({ item }: TimelineCardProps) {
  const getPrecisionBadgeVariant = (precision: string) => {
    switch (precision.toLowerCase()) {
      case 'day':
        return 'warm';
      case 'month':
        return 'sage';
      case 'year':
        return 'amber';
      default:
        return 'default';
    }
  };

  return (
    <div className="relative pl-7 pb-8 group last:pb-2">
      {/* Timeline vertical connector line */}
      <div className="absolute left-2.5 top-3 bottom-0 w-0.5 bg-[#E8DFD5] dark:bg-[#332E2A] group-last:hidden" />

      {/* Timeline circular node */}
      <div className="absolute left-0 top-2 w-5 h-5 rounded-full border-2 border-white dark:border-[#1E1B19] bg-[#D96B43] shadow-xs flex items-center justify-center">
        <div className="w-1.5 h-1.5 rounded-full bg-white" />
      </div>

      {/* Memory Card */}
      <div className="p-5 rounded-3xl bg-white dark:bg-[#201D1B] border border-[#EAE2D8] dark:border-[#38332E] shadow-2xs hover:shadow-md hover:border-[#D96B43]/40 transition-all">
        {/* Header: Date & Precisions */}
        <div className="flex flex-wrap items-center justify-between gap-2 mb-3">
          <div className="flex items-center gap-2">
            <span className="font-serif text-base font-semibold text-[#2C2623] dark:text-[#F7F3EE]">
              {item.formatted_date}
            </span>
            <Badge
              variant={getPrecisionBadgeVariant(item.event_date_precision)}
              size="sm"
            >
              {formatPrecision(item.event_date_precision)}
            </Badge>
          </div>

          {/* Importance Indicators */}
          <div className="flex items-center gap-1" title={`Importance: ${item.importance}/5`}>
            {Array.from({ length: 5 }).map((_, i) => (
              <Star
                key={i}
                className={`w-3 h-3 ${
                  i < item.importance
                    ? 'text-amber-500 fill-amber-500'
                    : 'text-stone-300 dark:text-stone-700'
                }`}
              />
            ))}
          </div>
        </div>

        {/* Content */}
        <p className="text-sm text-[#3D352F] dark:text-[#E8DDD4] leading-relaxed mb-4 font-normal">
          {item.content}
        </p>

        {/* Metadata Footer */}
        <div className="flex flex-wrap items-center justify-between gap-2 pt-3 border-t border-[#F2ECE3] dark:border-[#2D2926] text-xs text-[#7C6E64] dark:text-[#A89C94]">
          <div className="flex items-center gap-2 flex-wrap">
            <Badge variant="outline" size="sm">
              <Tag className="w-2.5 h-2.5 mr-1" />
              {item.memory_type.replace(/_/g, ' ')}
            </Badge>

            {item.primary_source_type && (
              <span className="flex items-center gap-1 text-[11px] text-[#8C7E74]">
                <FileText className="w-3 h-3" />
                <span className="capitalize">{item.primary_source_type}</span>
                {item.primary_source_location && (
                  <span className="opacity-75">({item.primary_source_location})</span>
                )}
              </span>
            )}
          </div>

          {/* Explore Provenance Link */}
          <Link
            href={`/memories?id=${item.id}`}
            className="inline-flex items-center gap-1 text-xs font-medium text-[#D96B43] dark:text-[#EB8D74] hover:underline"
          >
            <span>View Provenance</span>
            <ExternalLink className="w-3 h-3" />
          </Link>
        </div>
      </div>
    </div>
  );
}
