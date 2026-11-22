'use client';

import React, { useEffect, useState } from 'react';
import { Modal } from '../ui/Modal';
import { Spinner } from '../ui/Spinner';
import { Badge } from '../ui/Badge';
import { api } from '../../lib/api';
import { MemoryProvenanceResponse } from '../../types/api';
import { formatDate, formatPrecision } from '../../lib/utils';
import {
  FileText,
  GitCommit,
  ShieldCheck,
  Calendar,
  Quote,
  AlertCircle,
  FileCode,
} from 'lucide-react';

interface ProvenanceModalProps {
  memoryId: string | null;
  isOpen: boolean;
  onClose: () => void;
}

export function ProvenanceModal({
  memoryId,
  isOpen,
  onClose,
}: ProvenanceModalProps) {
  const [provenance, setProvenance] = useState<MemoryProvenanceResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!isOpen || !memoryId) {
      setProvenance(null);
      setError(null);
      return;
    }

    const fetchProvenance = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await api.getProvenance(memoryId);
        setProvenance(data);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Failed to load provenance audit trail.';
        setError(msg);
      } finally {
        setIsLoading(false);
      }
    };

    fetchProvenance();
  }, [isOpen, memoryId]);

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title="Memory Provenance & Audit Trail"
      description="Verifiable source documentation and version history for this memory."
      maxWidth="lg"
    >
      {isLoading && (
        <div className="py-12 flex flex-col items-center justify-center gap-3">
          <Spinner size="md" />
          <p className="text-xs text-[#8C7E74]">Tracing memory origins & version history...</p>
        </div>
      )}

      {error && (
        <div className="p-4 rounded-2xl bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900 flex items-start gap-3 text-xs text-rose-800 dark:text-rose-200">
          <AlertCircle className="w-4 h-4 shrink-0 text-rose-600 mt-0.5" />
          <div>
            <div className="font-semibold">Unable to resolve provenance</div>
            <div className="mt-1">{error}</div>
          </div>
        </div>
      )}

      {provenance && (
        <div className="space-y-6">
          {/* Overview Capsule */}
          <div className="p-4 rounded-2xl bg-[#F7F2EC] dark:bg-[#25221F] border border-[#EAE2D8] dark:border-[#38332E]">
            <div className="flex flex-wrap items-center justify-between gap-2 mb-2">
              <div className="flex items-center gap-2">
                <Badge variant="warm" size="sm">
                  {provenance.memory_type.replace(/_/g, ' ')}
                </Badge>
                <Badge variant={provenance.status === 'active' ? 'sage' : 'default'} size="sm">
                  v{provenance.version} — {provenance.status}
                </Badge>
              </div>

              {provenance.event_date && (
                <span className="flex items-center gap-1 text-xs text-[#8C7E74]">
                  <Calendar className="w-3.5 h-3.5" />
                  <span>
                    {formatDate(provenance.event_date)} ({formatPrecision(provenance.event_date_precision)})
                  </span>
                </span>
              )}
            </div>
            <p className="text-sm font-medium text-[#2C2623] dark:text-[#F7F3EE] leading-relaxed">
              &ldquo;{provenance.content}&rdquo;
            </p>
          </div>

          {/* Section 1: Linked Artifacts & Source Excerpts */}
          <div>
            <h4 className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-[#7C6E64] dark:text-[#A89C94] mb-3">
              <FileText className="w-4 h-4 text-[#D96B43]" />
              <span>Attributed Sources ({provenance.sources.length})</span>
            </h4>

            {provenance.sources.length === 0 ? (
              <p className="text-xs text-[#A89C94] italic p-3 bg-white dark:bg-[#201D1B] rounded-xl border border-[#EAE2D8] dark:border-[#332E2A]">
                Extracted directly during live dialogue with HER (no external uploaded artifact).
              </p>
            ) : (
              <div className="space-y-3">
                {provenance.sources.map((src, i) => (
                  <div
                    key={src.source_id || i}
                    className="p-4 rounded-2xl bg-white dark:bg-[#201D1B] border border-[#EAE2D8] dark:border-[#38332E] shadow-2xs space-y-2.5"
                  >
                    <div className="flex flex-wrap items-center justify-between gap-2 text-xs">
                      <div className="flex items-center gap-2">
                        <span className="font-semibold text-[#2C2623] dark:text-[#F7F3EE] capitalize">
                          {src.source_type}
                        </span>
                        {src.source_location && (
                          <span className="px-2 py-0.5 rounded-md bg-[#FAF2EB] text-[#D96B43] font-mono text-[10px]">
                            {src.source_location}
                          </span>
                        )}
                      </div>
                      <span className="text-[11px] text-[#A89C94]">
                        Recorded {formatDate(src.created_at)}
                      </span>
                    </div>

                    {/* Excerpt Quote */}
                    {src.excerpt && (
                      <div className="p-3 rounded-xl bg-[#FAF7F2] dark:bg-[#181615] border-l-2 border-[#D96B43] text-xs text-[#4A4039] dark:text-[#D1C6BD] italic leading-relaxed">
                        <Quote className="w-3 h-3 text-[#D96B43] inline mr-1 opacity-70" />
                        {src.excerpt}
                      </div>
                    )}

                    {/* Artifact Details */}
                    {src.artifact && (
                      <div className="pt-2 border-t border-[#F2ECE3] dark:border-[#2D2926] flex flex-wrap items-center justify-between gap-2 text-[11px] text-[#8C7E74]">
                        <span className="flex items-center gap-1 font-mono">
                          <FileCode className="w-3 h-3 text-[#D96B43]" />
                          <span>{src.artifact.filename}</span>
                        </span>
                        <span
                          className="font-mono text-[10px] text-[#A89C94] truncate max-w-[200px]"
                          title={src.artifact.checksum_sha256}
                        >
                          SHA-256: {src.artifact.checksum_sha256.substring(0, 16)}...
                        </span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Section 2: Version History Lineage */}
          <div>
            <h4 className="flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-[#7C6E64] dark:text-[#A89C94] mb-3">
              <GitCommit className="w-4 h-4 text-[#D96B43]" />
              <span>Version Lineage & Corrections ({provenance.history.length})</span>
            </h4>

            {provenance.history.length === 0 ? (
              <p className="text-xs text-[#A89C94] italic p-3 bg-white dark:bg-[#201D1B] rounded-xl border border-[#EAE2D8] dark:border-[#332E2A]">
                Original version (v1). No user corrections have been submitted.
              </p>
            ) : (
              <div className="space-y-2">
                {provenance.history.map((hist) => (
                  <div
                    key={hist.memory_id}
                    className="p-3 rounded-xl bg-white dark:bg-[#201D1B] border border-[#EAE2D8] dark:border-[#38332E] text-xs flex items-center justify-between gap-3"
                  >
                    <div className="flex items-center gap-2.5">
                      <div className="w-6 h-6 rounded-lg bg-[#FAF2EB] text-[#D96B43] flex items-center justify-center font-bold text-[11px]">
                        v{hist.version}
                      </div>
                      <div>
                        <div className="font-medium text-[#2C2623] dark:text-[#F7F3EE]">
                          {hist.status === 'active' ? 'Current Version' : 'Superseded'}
                        </div>
                        {hist.superseded_reason && (
                          <div className="text-[11px] text-[#8C7E74]">
                            Reason: {hist.superseded_reason}
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="text-right text-[11px] text-[#A89C94]">
                      <div>{formatDate(hist.created_at)}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Privacy & Provenance Guarantee Note */}
          <div className="p-3.5 rounded-2xl bg-[#EBF3EF] dark:bg-[#1E2B25] border border-[#C5DDD2] dark:border-[#2D4238] flex items-start gap-2.5 text-xs text-[#3D6652] dark:text-[#A3D3BD]">
            <ShieldCheck className="w-4 h-4 shrink-0 mt-0.5" />
            <p className="leading-relaxed">
              HER AI adheres to strict data immutability for past versions. Corrections create new active versions while retaining the prior factual audit trail.
            </p>
          </div>
        </div>
      )}
    </Modal>
  );
}
