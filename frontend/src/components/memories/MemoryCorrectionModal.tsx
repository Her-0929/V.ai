'use client';

import React, { useState, useEffect } from 'react';
import { Modal } from '../ui/Modal';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { api } from '../../lib/api';
import { MemoryResponse, TemporalPrecision } from '../../types/api';
import { useToast } from '../../context/ToastContext';
import { History, Sparkles } from 'lucide-react';

interface MemoryCorrectionModalProps {
  memory: MemoryResponse | null;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function MemoryCorrectionModal({
  memory,
  isOpen,
  onClose,
  onSuccess,
}: MemoryCorrectionModalProps) {
  const { success: toastSuccess, error: toastError } = useToast();

  const [content, setContent] = useState('');
  const [reason, setReason] = useState('');
  const [eventDate, setEventDate] = useState('');
  const [precision, setPrecision] = useState<TemporalPrecision>('day');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (memory) {
      setContent(memory.content);
      setReason('');
      setEventDate(memory.event_date || '');
      setPrecision(
        (memory.event_date_precision as TemporalPrecision) || 'unknown'
      );
    }
  }, [memory, isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!memory) return;
    if (!content.trim()) {
      toastError('Memory content cannot be empty.');
      return;
    }
    if (!reason.trim()) {
      toastError('Please provide a reason for this correction.');
      return;
    }

    setIsSubmitting(true);
    try {
      await api.correctMemory(memory.id, {
        content: content.trim(),
        reason: reason.trim(),
        event_date: eventDate || undefined,
        event_date_precision: precision || undefined,
      });

      toastSuccess(`Memory updated to version ${memory.version + 1}!`);
      onSuccess();
      onClose();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Correction failed.';
      toastError(msg);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!memory) return null;

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Correct Stored Memory"
      description="Refine or update what HER remembers about you. A new version will be created."
      maxWidth="md"
    >
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Original Content Callout */}
        <div className="p-3.5 rounded-2xl bg-[#FAF2EB] dark:bg-[#2C211A] border border-[#F3C4B3]/60 dark:border-[#52342A] text-xs">
          <div className="font-semibold text-[#D96B43] dark:text-[#EB8D74] mb-1 flex items-center gap-1.5">
            <History className="w-3.5 h-3.5" />
            <span>Currently Stored (Version {memory.version}):</span>
          </div>
          <p className="text-[#3D352F] dark:text-[#DDD3CB] italic">&ldquo;{memory.content}&rdquo;</p>
        </div>

        {/* Corrected Content Input */}
        <div>
          <label className="block text-xs font-semibold text-[#6B5E57] dark:text-[#A89C94] mb-1.5">
            Corrected Memory Content *
          </label>
          <textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            rows={3}
            required
            className="w-full px-3.5 py-2.5 rounded-xl text-sm bg-white dark:bg-[#201D1B] border border-[#E8DFD5] dark:border-[#38332E] text-[#2C2623] dark:text-[#F7F3EE] placeholder-[#A39489] focus:outline-hidden focus:border-[#D96B43] focus:ring-1 focus:ring-[#D96B43]/30 leading-relaxed custom-scrollbar"
            placeholder="Enter the accurate memory..."
          />
        </div>

        {/* Correction Reason */}
        <div>
          <label className="block text-xs font-semibold text-[#6B5E57] dark:text-[#A89C94] mb-1.5">
            Reason for Correction *
          </label>
          <input
            type="text"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            required
            placeholder="e.g. Correcting exact year, clarified nuance, typo fix"
            className="w-full px-3.5 py-2.5 rounded-xl text-sm bg-white dark:bg-[#201D1B] border border-[#E8DFD5] dark:border-[#38332E] text-[#2C2623] dark:text-[#F7F3EE] placeholder-[#A39489] focus:outline-hidden focus:border-[#D96B43] focus:ring-1 focus:ring-[#D96B43]/30"
          />
        </div>

        {/* Event Date & Precision */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <Input
            label="Event Date (optional)"
            type="date"
            value={eventDate}
            onChange={(e) => setEventDate(e.target.value)}
          />

          <div>
            <label className="block text-xs font-medium text-[#6B5E57] dark:text-[#A89C94] mb-1.5">
              Temporal Precision
            </label>
            <select
              value={precision}
              onChange={(e) => setPrecision(e.target.value as TemporalPrecision)}
              className="w-full px-3.5 py-2.5 rounded-xl text-sm bg-white dark:bg-[#201D1B] border border-[#E8DFD5] dark:border-[#38332E] text-[#2C2623] dark:text-[#F7F3EE] focus:outline-hidden focus:border-[#D96B43]"
            >
              <option value="day">Exact Day</option>
              <option value="month">Specific Month</option>
              <option value="year">Year Level</option>
              <option value="decade">Decade Era</option>
              <option value="unknown">Unspecified</option>
            </select>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center justify-end gap-3 pt-3 border-t border-[#E8DFD5] dark:border-[#2C2926]">
          <Button
            type="button"
            variant="ghost"
            onClick={onClose}
            disabled={isSubmitting}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            variant="primary"
            isLoading={isSubmitting}
            disabled={!content.trim() || !reason.trim()}
          >
            <Sparkles className="w-4 h-4 mr-1.5" />
            <span>Save Correction (v{memory.version + 1})</span>
          </Button>
        </div>
      </form>
    </Modal>
  );
}
