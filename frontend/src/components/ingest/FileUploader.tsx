'use client';

import React, { useState, useRef } from 'react';
import { UploadCloud, CheckCircle2 } from 'lucide-react';
import { Button } from '../ui/Button';
import { api } from '../../lib/api';
import { MemoryArtifactJobResponse } from '../../types/api';
import { useToast } from '../../context/ToastContext';
import { formatBytes } from '../../lib/utils';

interface FileUploaderProps {
  onJobCreated: (job: MemoryArtifactJobResponse) => void;
}

export function FileUploader({ onJobCreated }: FileUploaderProps) {
  const { success: toastSuccess, error: toastError } = useToast();

  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [artifactType, setArtifactType] = useState<string>('document');
  const [contextNotes, setContextNotes] = useState<string>('');
  const [isUploading, setIsUploading] = useState<boolean>(false);
  const [isDragging, setIsDragging] = useState<boolean>(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelected = (file: File) => {
    const validExtensions = ['.pdf', '.txt'];
    const hasValidExt = validExtensions.some((ext) =>
      file.name.toLowerCase().endsWith(ext)
    );
    if (!hasValidExt) {
      toastError('Only PDF (.pdf) and Plain Text (.txt) files are supported.');
      return;
    }
    // Max 25 MB limit
    if (file.size > 26_214_400) {
      toastError('File size exceeds the 25 MB maximum limit.');
      return;
    }
    setSelectedFile(file);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) return;

    setIsUploading(true);
    try {
      const job = await api.uploadFile(selectedFile, artifactType, contextNotes);
      toastSuccess(`Uploaded "${selectedFile.name}". Ingestion job started!`);
      onJobCreated(job);
      setSelectedFile(null);
      setContextNotes('');
      if (fileInputRef.current) fileInputRef.current.value = '';
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Upload failed.';
      toastError(msg);
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Drag & Drop Zone */}
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={handleFileDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`p-8 border-2 border-dashed rounded-3xl text-center cursor-pointer transition-all ${
          isDragging
            ? 'border-[#D96B43] bg-[#FDEEE9]/50 dark:bg-[#38241D]/30'
            : selectedFile
            ? 'border-emerald-300 dark:border-emerald-800 bg-emerald-50/40 dark:bg-emerald-950/20'
            : 'border-[#E2D8CC] dark:border-[#38332E] hover:border-[#D96B43]/50 bg-white/60 dark:bg-[#201D1B]/60'
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.txt"
          className="hidden"
          onChange={(e) => {
            if (e.target.files && e.target.files[0]) {
              handleFileSelected(e.target.files[0]);
            }
          }}
        />

        {selectedFile ? (
          <div className="flex flex-col items-center gap-2">
            <div className="w-12 h-12 rounded-2xl bg-emerald-100 dark:bg-emerald-900/40 text-emerald-700 dark:text-emerald-300 flex items-center justify-center">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <div>
              <div className="font-semibold text-sm text-[#2C2623] dark:text-[#F7F3EE]">
                {selectedFile.name}
              </div>
              <div className="text-xs text-[#8C7E74]">
                {formatBytes(selectedFile.size)} · Ready to ingest
              </div>
            </div>
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                setSelectedFile(null);
              }}
              className="mt-1 text-xs text-rose-600 hover:underline"
            >
              Choose different file
            </button>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2.5">
            <div className="w-12 h-12 rounded-2xl bg-[#FAF2EB] dark:bg-[#2C221A] text-[#D96B43] flex items-center justify-center">
              <UploadCloud className="w-6 h-6" />
            </div>
            <div>
              <div className="font-semibold text-sm text-[#2C2623] dark:text-[#F7F3EE]">
                Click or drag & drop documents here
              </div>
              <div className="text-xs text-[#8C7E74] mt-1">
                Supported formats: <strong>PDF (.pdf)</strong> and <strong>Plain Text (.txt)</strong>
              </div>
              <div className="text-[11px] text-[#A89C94] mt-0.5">Maximum size: 25 MiB</div>
            </div>
          </div>
        )}
      </div>

      {/* Artifact Type & Context Options */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div>
          <label className="block text-xs font-semibold text-[#6B5E57] dark:text-[#A89C94] mb-1.5">
            Document Category
          </label>
          <select
            value={artifactType}
            onChange={(e) => setArtifactType(e.target.value)}
            className="w-full px-3.5 py-2.5 rounded-xl text-sm bg-white dark:bg-[#201D1B] border border-[#E8DFD5] dark:border-[#38332E] text-[#2C2623] dark:text-[#F7F3EE] focus:outline-hidden focus:border-[#D96B43]"
          >
            <option value="document">Document / PDF</option>
            <option value="letter">Personal Letter</option>
            <option value="note">Journal Note</option>
          </select>
        </div>

        <div>
          <label className="block text-xs font-semibold text-[#6B5E57] dark:text-[#A89C94] mb-1.5">
            Context Notes (Optional)
          </label>
          <input
            type="text"
            value={contextNotes}
            onChange={(e) => setContextNotes(e.target.value)}
            placeholder="e.g. Summer vacation memories, letters from 2020"
            className="w-full px-3.5 py-2.5 rounded-xl text-sm bg-white dark:bg-[#201D1B] border border-[#E8DFD5] dark:border-[#38332E] text-[#2C2623] dark:text-[#F7F3EE] placeholder-[#A39489] focus:outline-hidden focus:border-[#D96B43]"
          />
        </div>
      </div>

      <div className="flex justify-end pt-2">
        <Button
          type="submit"
          variant="primary"
          isLoading={isUploading}
          disabled={!selectedFile}
        >
          <UploadCloud className="w-4 h-4 mr-1.5" />
          <span>Start Ingestion</span>
        </Button>
      </div>
    </form>
  );
}
