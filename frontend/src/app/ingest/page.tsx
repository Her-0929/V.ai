'use client';

import React, { useState } from 'react';
import { AppLayout } from '../../components/layout/AppLayout';
import { FileUploader } from '../../components/ingest/FileUploader';
import { TextNoteIngest } from '../../components/ingest/TextNoteIngest';
import { JobStatusCard } from '../../components/ingest/JobStatusCard';
import { MemoryArtifactJobResponse } from '../../types/api';
import {
  UploadCloud,
  FileText,
  PenLine,
  Activity,
  ShieldCheck,
} from 'lucide-react';

export default function IngestPage() {
  const [activeTab, setActiveTab] = useState<'file' | 'text'>('file');
  const [recentJobs, setRecentJobs] = useState<MemoryArtifactJobResponse[]>([]);

  const handleJobCreated = (job: MemoryArtifactJobResponse) => {
    setRecentJobs((prev) => [job, ...prev]);
  };

  return (
    <AppLayout>
      <div className="flex-1 max-w-4xl w-full mx-auto px-4 sm:px-6 py-8">
        {/* Title */}
        <div className="mb-6">
          <div className="flex items-center gap-2 mb-1">
            <UploadCloud className="w-5 h-5 text-[#D96B43]" />
            <h1 className="font-serif text-2xl sm:text-3xl font-medium text-[#2C2623] dark:text-[#F7F3EE]">
              Personal Data Ingestion
            </h1>
          </div>
          <p className="text-xs sm:text-sm text-[#7C6E64] dark:text-[#A89C94]">
            Provide personal letters, notes, and documents. HER extracts long-term factual memories and timestamps.
          </p>
        </div>

        {/* Tab Selector */}
        <div className="flex items-center gap-2 p-1.5 rounded-2xl bg-[#F0EAE1] dark:bg-[#201D1B] max-w-md mb-6">
          <button
            onClick={() => setActiveTab('file')}
            className={`flex-1 flex items-center justify-center gap-2 py-2 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
              activeTab === 'file'
                ? 'bg-white dark:bg-[#2A2623] text-[#D96B43] shadow-xs'
                : 'text-[#6B5E57] dark:text-[#A89C94] hover:text-[#2C2623]'
            }`}
          >
            <FileText className="w-4 h-4" />
            <span>Upload Files (PDF / TXT)</span>
          </button>
          <button
            onClick={() => setActiveTab('text')}
            className={`flex-1 flex items-center justify-center gap-2 py-2 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
              activeTab === 'text'
                ? 'bg-white dark:bg-[#2A2623] text-[#D96B43] shadow-xs'
                : 'text-[#6B5E57] dark:text-[#A89C94] hover:text-[#2C2623]'
            }`}
          >
            <PenLine className="w-4 h-4" />
            <span>Draft Note / Letter</span>
          </button>
        </div>

        {/* Tab Content Box */}
        <div className="p-6 sm:p-8 rounded-3xl bg-white dark:bg-[#201D1B] border border-[#EAE2D8] dark:border-[#38332E] shadow-2xs mb-8">
          {activeTab === 'file' ? (
            <FileUploader onJobCreated={handleJobCreated} />
          ) : (
            <TextNoteIngest onJobCreated={handleJobCreated} />
          )}
        </div>

        {/* Ingestion Pipeline Notice */}
        <div className="p-4 rounded-2xl bg-[#FAF2EB] dark:bg-[#2C211A] border border-[#F3C4B3]/50 dark:border-[#52342A] flex items-start gap-3 text-xs text-[#7C6E64] dark:text-[#D1C6BD] mb-8">
          <ShieldCheck className="w-4 h-4 text-[#D96B43] shrink-0 mt-0.5" />
          <div className="leading-relaxed">
            <strong>Idempotency & Isolation:</strong> Uploaded files are hashed with SHA-256 for duplicate avoidance. Fact extraction executes asynchronously in background tasks without blocking your session.
          </div>
        </div>

        {/* Active & Recent Jobs List */}
        {recentJobs.length > 0 && (
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-[#D96B43]" />
              <h3 className="font-serif text-lg font-medium text-[#2C2623] dark:text-[#F7F3EE]">
                Recent Ingestion Jobs ({recentJobs.length})
              </h3>
            </div>

            <div className="space-y-3">
              {recentJobs.map((job) => (
                <JobStatusCard key={job.job_id} initialJob={job} />
              ))}
            </div>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
