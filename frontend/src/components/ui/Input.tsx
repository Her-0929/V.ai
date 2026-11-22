import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export function Input({ label, error, className = '', ...props }: InputProps) {
  return (
    <div className="w-full">
      {label && (
        <label className="block text-xs font-medium text-[#6B5E57] dark:text-[#A89C94] mb-1.5">
          {label}
        </label>
      )}
      <input
        className={`w-full px-3.5 py-2.5 rounded-xl text-sm bg-white dark:bg-[#201D1B] border border-[#E8DFD5] dark:border-[#38332E] text-[#2C2623] dark:text-[#F7F3EE] placeholder-[#A39489] focus:outline-hidden focus:border-[#D96B43] focus:ring-1 focus:ring-[#D96B43]/30 transition-all ${
          error ? 'border-rose-400 focus:border-rose-500' : ''
        } ${className}`}
        {...props}
      />
      {error && <p className="mt-1 text-xs text-rose-600 dark:text-rose-400">{error}</p>}
    </div>
  );
}
