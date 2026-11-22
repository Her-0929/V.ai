'use client';

import React, { useEffect, useState, useRef } from 'react';
import Link from 'next/link';
import {
  CheckCircle2,
  AlertCircle,
  FileText,
  ExternalLink,
  Sparkles,
  RefreshCw,
} from 'lucide-react';
import { api } from '../../lib/api';
import { MemoryArtifactJobDetailResponse, MemoryArtifactJobResponse } from '../../types/api';
import { Badge } from '../ui/Badge';

interface JobStatusCardProps {
  initialJob: MemoryArtifactJobResponse;
}

export function JobStatusCard({ initialJob }: JobStatusCardProps) {
  const [job, setJob] = useState<MemoryArtifactJobDetailResponse | null>(null);
  const pollTimerRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    let isMounted = true;

    const poll = async () => {
      try {
        const detail = await api.getJobStatus(initialJob.job_id);
        if (!isMounted) return;
        setJob(detail);

        if (detail.status === 'completed' || detail.status === 'failed') {
          if (pollTimerRef.current) clearInterval(pollTimerRef.current);
        }
      } catch (err) {
        console.warn('Job polling error:', err);
      }
    };

    poll();
    pollTimerRef.current = setInterval(poll, 2500);

    return () => {
      isMounted = false;
      if (pollTimerRef.current) clearInterval(pollTimerRef.current);
    };
  }, [initialJob.job_id]);

  const status = job?.status || initialJob.status;
  const isCompleted = status === 'completed';
  const isFailed = status === 'failed';
  const isProcessing = status === 'processing' || status === 'pending';

  return (
    <div className="p-4 sm:p-5 rounded-3xl bg-white dark:bg-[#201D1B] border border-[#EAE2D8] dark:border-[#38332E] shadow-2xs space-y-3">
      {/* Header: Filename & Status */}
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2">
          <FileText className="w-4 h-4 text-[#D96B43]" />
          <span className="font-semibold text-sm text-[#2C2623] dark:text-[#F7F3EE]">
            {initialJob.filename}
          </span>
          <span className="text-xs text-[#A89C94] capitalize">
            ({initialJob.artifact_type})
          </span>
        </div>

        {/* Status Badge */}
        <div>
          {isProcessing && (
            <Badge variant="amber" size="sm">
              <RefreshCw className="w-3 h-3 animate-spin mr-1" />
              <span>Processing...</span>
            </Badge>
          )}
          {isCompleted && (
            <Badge variant="sage" size="sm">
              <CheckCircle2 className="w-3 h-3 mr-1" />
              <span>Completed</span>
            </Badge>
          )}
          {isFailed && (
            <Badge variant="default" size="sm" className="text-rose-600 bg-rose-50 border-rose-200">
              <AlertCircle className="w-3 h-3 mr-1" />
              <span>Failed</span>
            </Badge>
          )}
        </div>
      </div>

      {/* Progress / Result info */}
      <div className="text-xs text-[#6B5E57] dark:text-[#B8ACA4] flex flex-wrap items-center justify-between gap-2">
        <div>
          {isCompleted && (
            <span className="font-medium text-emerald-700 dark:text-emerald-300 flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
              <span>Successfully extracted {job?.extracted_memories_count || 0} memories!</span>
            </span>
          )}
          {isProcessing && (
            <span className="italic">
              Sanitizing, analyzing temporal dates, and extracting facts...
            </span>
          )}
          {isFailed && (
            <span className="text-rose-600 dark:text-rose-400">
              Error: {job?.error_message || 'Processing encountered an error.'}
            </span>
          )}
        </div>

        <div className="text-[11px] text-[#A89C94]">
          Job ID: {initialJob.job_id.substring(0, 8)}...
        </div>
      </div>

      {/* Action to view in explorer */}
      {isCompleted && job && job.extracted_memory_ids?.length > 0 && (
        <div className="pt-2 border-t border-[#F2ECE3] dark:border-[#2D2926] flex justify-end">
          <Link
            href={`/memories?id=${job.extracted_memory_ids[0]}`}
            className="inline-flex items-center gap-1 text-xs font-medium text-[#D96B43] hover:underline"
          >
            <span>Explore Extracted Memories</span>
            <ExternalLink className="w-3 h-3" />
          </Link>
        </div>
      )}
    </div>
  );
}
