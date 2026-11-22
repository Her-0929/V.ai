'use client';

import React, { useEffect } from 'react';
import { X } from 'lucide-react';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  children: React.ReactNode;
  maxWidth?: 'sm' | 'md' | 'lg' | 'xl';
}

export function Modal({
  isOpen,
  onClose,
  title,
  description,
  children,
  maxWidth = 'md',
}: ModalProps) {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    if (isOpen) {
      document.body.style.overflow = 'hidden';
      window.addEventListener('keydown', handleKeyDown);
    }
    return () => {
      document.body.style.overflow = 'auto';
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const maxWidthStyles = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-stone-900/50 backdrop-blur-xs transition-opacity"
        onClick={onClose}
      />

      {/* Modal Dialog */}
      <div
        className={`relative w-full ${maxWidthStyles[maxWidth]} rounded-3xl bg-[#FAF7F2] dark:bg-[#1E1B19] border border-[#E8DFD5] dark:border-[#38332E] shadow-2xl p-6 sm:p-8 max-h-[90vh] flex flex-col z-10 transition-all`}
      >
        <div className="flex items-start justify-between pb-4 border-b border-[#E8DFD5] dark:border-[#2C2926] shrink-0">
          <div>
            <h3 className="font-serif text-xl font-medium text-[#2C2623] dark:text-[#F7F3EE]">
              {title}
            </h3>
            {description && (
              <p className="mt-1 text-xs text-[#7C6E64] dark:text-[#A89C94]">
                {description}
              </p>
            )}
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-xl text-[#7C6E64] hover:bg-[#EFE7DC] dark:hover:bg-[#2C2926] transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto py-5 custom-scrollbar">
          {children}
        </div>
      </div>
    </div>
  );
}
