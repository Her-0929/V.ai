'use client';

import React, { useState, useEffect, useCallback, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { AppLayout } from '../../components/layout/AppLayout';
import { MemoryCard } from '../../components/memories/MemoryCard';
import { ProvenanceModal } from '../../components/memories/ProvenanceModal';
import { MemoryCorrectionModal } from '../../components/memories/MemoryCorrectionModal';
import { OpenWhenLetters } from '../../components/memories/OpenWhenLetters';
import { Spinner } from '../../components/ui/Spinner';
import { Button } from '../../components/ui/Button';
import { api } from '../../lib/api';
import { MemoryResponse } from '../../types/api';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import {
  Compass,
  Search,
  Download,
  Brain,
  FolderUp,
  X,
  Camera,
} from 'lucide-react';
import Link from 'next/link';

const MEMORY_CATEGORIES = [
  { label: 'All Categories', value: '' },
  { label: 'Life Events', value: 'life_event' },
  { label: 'Career Goals', value: 'career_goal' },
  { label: 'Relationships', value: 'relationship' },
  { label: 'Personal Info', value: 'personal_info' },
  { label: 'Hobbies & Interests', value: 'hobby' },
  { label: 'Emotional Experiences', value: 'emotional_experience' },
  { label: 'Milestones', value: 'milestone' },
];

function MemoryExplorerContent() {
  const searchParams = useSearchParams();
  const queryMemoryId = searchParams.get('id');

  const { token } = useAuth();
  const { success: toastSuccess, error: toastError } = useToast();

  const [memories, setMemories] = useState<MemoryResponse[]>([]);
  const [total, setTotal] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Filters
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [isSemanticSearching, setIsSemanticSearching] = useState<boolean>(false);
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [showActiveOnly, setShowActiveOnly] = useState<boolean>(true);

  // Modals state
  const [selectedProvenanceId, setSelectedProvenanceId] = useState<string | null>(null);
  const [isProvenanceOpen, setIsProvenanceOpen] = useState<boolean>(false);

  const [selectedCorrectionMemory, setSelectedCorrectionMemory] =
    useState<MemoryResponse | null>(null);
  const [isCorrectionOpen, setIsCorrectionOpen] = useState<boolean>(false);

  // Load memories
  const loadMemories = useCallback(async () => {
    if (!token) return;
    setIsLoading(true);
    try {
      const data = await api.listMemories({
        memory_type: selectedCategory || undefined,
        is_active: showActiveOnly,
        limit: 100,
      });
      setMemories(data.memories);
      setTotal(data.total);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load memories.';
      toastError(msg);
    } finally {
      setIsLoading(false);
    }
  }, [token, selectedCategory, showActiveOnly, toastError]);

  useEffect(() => {
    loadMemories();
  }, [loadMemories]);

  // If ?id= is in search params, auto-open provenance
  useEffect(() => {
    if (queryMemoryId) {
      setSelectedProvenanceId(queryMemoryId);
      setIsProvenanceOpen(true);
    }
  }, [queryMemoryId]);

  // Handle Semantic Vector Search
  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) {
      loadMemories();
      return;
    }

    setIsSemanticSearching(true);
    try {
      const searchRes = await api.searchMemories({
        query: searchQuery.trim(),
        limit: 20,
        min_similarity: 0.15,
      });

      // Map search results back to full memory list by fetching or matching
      const memoryIds = searchRes.results.map((r) => r.id);
      // Fetch matching full memory objects
      const matched = await Promise.all(
        memoryIds.map(async (id) => {
          try {
            return await api.getMemory(id);
          } catch {
            return null;
          }
        })
      );

      const validMatches = matched.filter((m): m is MemoryResponse => m !== null);
      setMemories(validMatches);
      setTotal(validMatches.length);
      toastSuccess(`Found ${validMatches.length} semantically relevant memories.`);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Search failed.';
      toastError(msg);
    } finally {
      setIsSemanticSearching(false);
    }
  };

  const handleClearSearch = () => {
    setSearchQuery('');
    loadMemories();
  };

  const handleInspectProvenance = (mem: MemoryResponse) => {
    setSelectedProvenanceId(mem.id);
    setIsProvenanceOpen(true);
  };

  const handleCorrectMemory = (mem: MemoryResponse) => {
    setSelectedCorrectionMemory(mem);
    setIsCorrectionOpen(true);
  };

  const handleDeactivate = async (id: string) => {
    if (!confirm('Deactivate this memory? HER will stop retrieving it during conversations.'))
      return;
    try {
      await api.deactivateMemory(id);
      toastSuccess('Memory deactivated.');
      loadMemories();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to deactivate memory.';
      toastError(msg);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this memory permanently? This cannot be undone.')) return;
    try {
      await api.deleteMemory(id);
      toastSuccess('Memory deleted.');
      loadMemories();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to delete memory.';
      toastError(msg);
    }
  };

  const handleExport = async () => {
    try {
      const exportData = await api.exportMemories();
      const blob = new Blob([JSON.stringify(exportData, null, 2)], {
        type: 'application/json',
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `her_ai_memories_${new Date().toISOString().substring(0, 10)}.json`;
      a.click();
      URL.revokeObjectURL(url);
      toastSuccess(`Exported ${exportData.total_memories} memories as JSON.`);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Export failed.';
      toastError(msg);
    }
  };

  return (
    <div className="flex-1 max-w-5xl w-full mx-auto px-4 sm:px-6 py-8">
      {/* Page Title & Actions */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="text-2xl">💌</span>
            <h1 className="font-serif text-2xl sm:text-3xl font-medium text-[#2C2623] dark:text-[#F7F3EE]">
              Letters & Little Memories
            </h1>
          </div>
          <p className="text-xs sm:text-sm text-[#7C6E64] dark:text-[#A89C94]">
            Envelopes sealed with care, thoughts written just for you, and little moments saved forever.
          </p>
        </div>

        <div className="flex items-center gap-2.5 self-start sm:self-auto">
          <Link
            href="/profile"
            className="px-3.5 py-1.5 rounded-xl bg-white dark:bg-[#201D1B] border border-[#E8DFD5] dark:border-[#38332E] text-xs font-semibold text-rose-500 hover:border-rose-300 transition-all shadow-2xs flex items-center gap-1.5"
          >
            <Camera className="w-3.5 h-3.5" />
            <span>Open Scrapbook</span>
          </Link>
        </div>
      </div>

      {/* Interactive Open When Letters */}
      <OpenWhenLetters />

      {/* Notes & Search Header */}
      <div className="flex items-center justify-between mb-3 px-1">
        <h3 className="font-serif text-lg font-medium text-[#2C2623] dark:text-[#F7F3EE]">
          Preserved Notes & Memories ({total})
        </h3>
      </div>

      {/* Semantic Search & Category Bar */}
      <div className="p-4 sm:p-5 rounded-3xl bg-white dark:bg-[#201D1B] border border-[#EAE2D8] dark:border-[#38332E] shadow-2xs mb-6 space-y-4">
        {/* Semantic Search Input */}
        <form onSubmit={handleSearch} className="relative flex items-center">
          <Search className="w-4 h-4 text-[#A89C94] absolute left-3.5 pointer-events-none" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search semantically (e.g. 'temple visits', 'first sighting', 'ambitions')..."
            className="w-full pl-10 pr-24 py-2.5 rounded-2xl bg-[#F7F2EC] dark:bg-[#2C2926] border border-[#E8DFD5] dark:border-[#38332E] text-sm text-[#2C2623] dark:text-[#F7F3EE] placeholder-[#A39489] focus:outline-hidden focus:border-[#D96B43]"
          />
          {searchQuery && (
            <button
              type="button"
              onClick={handleClearSearch}
              className="absolute right-20 p-1 text-[#A89C94] hover:text-[#2C2623]"
            >
              <X className="w-4 h-4" />
            </button>
          )}
          <button
            type="submit"
            disabled={isSemanticSearching}
            className="absolute right-2 px-3 py-1.5 rounded-xl bg-[#D96B43] text-white text-xs font-medium hover:bg-[#C55730] transition-colors cursor-pointer"
          >
            {isSemanticSearching ? 'Searching...' : 'Search'}
          </button>
        </form>

        {/* Categories & Active Filter */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-[#F2ECE3] dark:border-[#2D2926]">
          {/* Category Chips */}
          <div className="flex items-center gap-1.5 overflow-x-auto pb-1 sm:pb-0 custom-scrollbar max-w-full">
            {MEMORY_CATEGORIES.map((cat) => {
              const isSelected = selectedCategory === cat.value;
              return (
                <button
                  key={cat.value}
                  onClick={() => setSelectedCategory(cat.value)}
                  className={`px-3 py-1 rounded-xl text-xs font-medium whitespace-nowrap transition-colors cursor-pointer ${
                    isSelected
                      ? 'bg-[#D96B43] text-white shadow-2xs'
                      : 'bg-[#F7F2EC] dark:bg-[#2C2926] text-[#6B5E57] dark:text-[#C4B7AE] hover:bg-[#EFE7DC]'
                  }`}
                >
                  {cat.label}
                </button>
              );
            })}
          </div>

          {/* Status Toggle */}
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowActiveOnly(!showActiveOnly)}
              className={`px-3 py-1 rounded-xl text-xs font-medium border transition-colors cursor-pointer ${
                showActiveOnly
                  ? 'bg-emerald-50 text-emerald-800 border-emerald-200 dark:bg-emerald-950/40 dark:text-emerald-300 dark:border-emerald-800'
                  : 'bg-stone-100 text-stone-700 border-stone-300 dark:bg-stone-800 dark:text-stone-300 dark:border-stone-700'
              }`}
            >
              {showActiveOnly ? 'Showing: Active Only' : 'Showing: Active & Superseded'}
            </button>
          </div>
        </div>
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="py-20 flex flex-col items-center justify-center gap-3">
          <Spinner size="lg" />
          <p className="text-xs text-[#8C7E74]">Accessing neural memory vault...</p>
        </div>
      )}

      {/* Empty State */}
      {!isLoading && memories.length === 0 && (
        <div className="p-12 text-center rounded-3xl bg-white dark:bg-[#201D1B] border border-[#EAE2D8] dark:border-[#38332E] max-w-md mx-auto">
          <Brain className="w-10 h-10 text-[#D96B43] mx-auto mb-3 opacity-60" />
          <h3 className="font-serif text-lg font-medium text-[#2C2623] dark:text-[#F7F3EE] mb-1">
            No Memories Found
          </h3>
          <p className="text-xs text-[#7C6E64] dark:text-[#A89C94] leading-relaxed mb-5">
            {searchQuery
              ? `No memories matched "${searchQuery}". Try a broader search term.`
              : 'No memories match the selected filters.'}
          </p>
          <div className="flex items-center justify-center gap-3">
            <Link
              href="/ingest"
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl bg-[#D96B43] text-white text-xs font-medium hover:bg-[#C55730] transition-colors"
            >
              <FolderUp className="w-3.5 h-3.5" />
              <span>Ingest New Notes</span>
            </Link>
          </div>
        </div>
      )}

      {/* Memories Grid */}
      {!isLoading && memories.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 animate-fadeIn">
          {memories.map((mem) => (
            <MemoryCard
              key={mem.id}
              memory={mem}
              onInspectProvenance={handleInspectProvenance}
              onCorrectMemory={handleCorrectMemory}
              onDeactivateMemory={handleDeactivate}
              onDeleteMemory={handleDelete}
            />
          ))}
        </div>
      )}

      {/* Provenance Audit Modal */}
      <ProvenanceModal
        memoryId={selectedProvenanceId}
        isOpen={isProvenanceOpen}
        onClose={() => {
          setIsProvenanceOpen(false);
          setSelectedProvenanceId(null);
        }}
      />

      {/* Memory Correction Modal */}
      <MemoryCorrectionModal
        memory={selectedCorrectionMemory}
        isOpen={isCorrectionOpen}
        onClose={() => {
          setIsCorrectionOpen(false);
          setSelectedCorrectionMemory(null);
        }}
        onSuccess={loadMemories}
      />
    </div>
  );
}

export default function MemoryExplorerPage() {
  return (
    <AppLayout>
      <Suspense fallback={<div className="p-8"><Spinner /></div>}>
        <MemoryExplorerContent />
      </Suspense>
    </AppLayout>
  );
}
