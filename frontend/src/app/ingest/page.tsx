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
  const [activeTab, setActiveTab] = useState<'file' | 'text'>('text');
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
            <span className="text-2xl">✨</span>
            <h1 className="font-serif text-2xl sm:text-3xl font-medium text-[#2C2623] dark:text-[#F7F3EE]">
              Wish Capsule & Memories
            </h1>
          </div>
          <p className="text-xs sm:text-sm text-[#7C6E64] dark:text-[#A89C94]">
            Share a secret thought, a wish for the future, or write down a little story you want preserved in our world.
          </p>
        </div>

        {/* Companion Welcome Banner */}
        <div className="mb-6 p-4 sm:p-5 rounded-3xl bg-white dark:bg-[#201D1B] border border-rose-100 dark:border-[#38332E] shadow-2xs flex items-center gap-4">
          <div className="relative w-14 h-14 sm:w-16 sm:h-16 rounded-2xl overflow-hidden shrink-0 ring-2 ring-rose-300 bg-[#E07A5F] shadow-xs">
            <img
              src="/her/white_festive.jpg"
              alt="You"
              className="w-full h-full object-cover object-top"
            />
          </div>
          <div>
            <h3 className="font-serif text-base sm:text-lg font-medium text-[#2C2623] dark:text-[#F7F3EE]">
              Leave a note in our capsule 💌
            </h3>
            <p className="text-xs text-[#7C6E64] dark:text-[#A89C94] leading-relaxed">
              Every word you write here becomes part of this universe. It will always be remembered and cherished.
            </p>
          </div>
        </div>

        {/* Tab Selector */}
        <div className="flex items-center gap-2 p-1.5 rounded-2xl bg-[#F0EAE1] dark:bg-[#201D1B] max-w-md mb-6">
          <button
            onClick={() => setActiveTab('text')}
            className={`flex-1 flex items-center justify-center gap-2 py-2 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
              activeTab === 'text'
                ? 'bg-white dark:bg-[#2A2623] text-rose-600 shadow-xs'
                : 'text-[#6B5E57] dark:text-[#A89C94] hover:text-[#2C2623]'
            }`}
          >
            <PenLine className="w-4 h-4" />
            <span>Write A Note / Wish ✍️</span>
          </button>
          <button
            onClick={() => setActiveTab('file')}
            className={`flex-1 flex items-center justify-center gap-2 py-2 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
              activeTab === 'file'
                ? 'bg-white dark:bg-[#2A2623] text-rose-600 shadow-xs'
                : 'text-[#6B5E57] dark:text-[#A89C94] hover:text-[#2C2623]'
            }`}
          >
            <FileText className="w-4 h-4" />
            <span>Upload Story File 📄</span>
          </button>
        </div>

        {/* Tab Content Box */}
        <div className="p-6 sm:p-8 rounded-3xl bg-white dark:bg-[#201D1B] border border-rose-100 dark:border-[#38332E] shadow-2xs mb-8">
          {activeTab === 'file' ? (
            <FileUploader onJobCreated={handleJobCreated} />
          ) : (
            <TextNoteIngest onJobCreated={handleJobCreated} />
          )}
        </div>

        {/* Sweet Notice */}
        <div className="p-4 rounded-2xl bg-rose-50/70 dark:bg-rose-950/20 border border-rose-200/60 dark:border-rose-900/40 flex items-start gap-3 text-xs text-rose-800 dark:text-rose-300 mb-8 font-serif italic">
          <ShieldCheck className="w-4 h-4 text-rose-500 shrink-0 mt-0.5" />
          <div className="leading-relaxed">
            <strong>Private & Sacred:</strong> Whatever you write here is preserved safely. This space is entirely your own.
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
