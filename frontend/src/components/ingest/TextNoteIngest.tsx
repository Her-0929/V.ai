'use client';

import React, { useState } from 'react';
import { Sparkles } from 'lucide-react';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { api } from '../../lib/api';
import { ArtifactType, MemoryArtifactJobResponse } from '../../types/api';
import { useToast } from '../../context/ToastContext';

interface TextNoteIngestProps {
  onJobCreated: (job: MemoryArtifactJobResponse) => void;
}

export function TextNoteIngest({ onJobCreated }: TextNoteIngestProps) {
  const { success: toastSuccess, error: toastError } = useToast();

  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [artifactType, setArtifactType] = useState<ArtifactType>('note');
  const [contextNotes, setContextNotes] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) {
      toastError('Content cannot be empty.');
      return;
    }

    setIsSubmitting(true);
    try {
      const job = await api.ingestText({
        title: title.trim() || 'Personal Note',
        content: content.trim(),
        artifact_type: artifactType,
        context_notes: contextNotes.trim() || undefined,
      });

      toastSuccess(`Submitted note "${title || 'Personal Note'}". Ingestion running!`);
      onJobCreated(job);
      setTitle('');
      setContent('');
      setContextNotes('');
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Ingestion failed.';
      toastError(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <Input
          label="Title / Heading"
          placeholder="e.g. Reflections on College Years, Letter to Mom"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
        />

        <div>
          <label className="block text-xs font-semibold text-[#6B5E57] dark:text-[#A89C94] mb-1.5">
            Category
          </label>
          <select
            value={artifactType}
            onChange={(e) => setArtifactType(e.target.value as ArtifactType)}
            className="w-full px-3.5 py-2.5 rounded-xl text-sm bg-white dark:bg-[#201D1B] border border-[#E8DFD5] dark:border-[#38332E] text-[#2C2623] dark:text-[#F7F3EE] focus:outline-hidden focus:border-[#D96B43]"
          >
            <option value="note">Journal Note</option>
            <option value="letter">Personal Letter</option>
            <option value="document">Document</option>
          </select>
        </div>
      </div>

      <div>
        <label className="block text-xs font-semibold text-[#6B5E57] dark:text-[#A89C94] mb-1.5">
          Note Content *
        </label>
        <textarea
          rows={6}
          required
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="Write your note, memory, thoughts, or letter here. HER will parse facts, dates, and emotional nuances..."
          className="w-full px-3.5 py-2.5 rounded-2xl text-sm bg-white dark:bg-[#201D1B] border border-[#E8DFD5] dark:border-[#38332E] text-[#2C2623] dark:text-[#F7F3EE] placeholder-[#A39489] focus:outline-hidden focus:border-[#D96B43] leading-relaxed custom-scrollbar"
        />
      </div>

      <div>
        <label className="block text-xs font-semibold text-[#6B5E57] dark:text-[#A89C94] mb-1.5">
          Context Notes (Optional)
        </label>
        <input
          type="text"
          value={contextNotes}
          onChange={(e) => setContextNotes(e.target.value)}
          placeholder="e.g. Written in Bangalore during final semester"
          className="w-full px-3.5 py-2.5 rounded-xl text-sm bg-white dark:bg-[#201D1B] border border-[#E8DFD5] dark:border-[#38332E] text-[#2C2623] dark:text-[#F7F3EE] placeholder-[#A39489] focus:outline-hidden focus:border-[#D96B43]"
        />
      </div>

      <div className="flex justify-end pt-2">
        <Button
          type="submit"
          variant="primary"
          isLoading={isSubmitting}
          disabled={!content.trim()}
        >
          <Sparkles className="w-4 h-4 mr-1.5" />
          <span>Ingest & Extract Memories</span>
        </Button>
      </div>
    </form>
  );
}
