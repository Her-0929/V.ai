import React from 'react';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'warm' | 'sage' | 'dusk' | 'amber' | 'outline';
  size?: 'sm' | 'md';
  className?: string;
}

export function Badge({
  children,
  variant = 'default',
  size = 'md',
  className = '',
}: BadgeProps) {
  const variantStyles = {
    default:
      'bg-[#EFE7DC] dark:bg-[#2C2926] text-[#6B5E57] dark:text-[#C4B7AE] border border-transparent',
    warm: 'bg-[#FDEEE9] dark:bg-[#38241D] text-[#D96B43] dark:text-[#EB8D74] border border-[#F3C4B3] dark:border-[#52342A]',
    sage: 'bg-[#EBF3EF] dark:bg-[#1E2B25] text-[#4F7A65] dark:text-[#81B29A] border border-[#C5DDD2] dark:border-[#2D4238]',
    dusk: 'bg-[#EFF3F6] dark:bg-[#1C2429] text-[#4F6C7A] dark:text-[#88A6B5] border border-[#CDE0E9] dark:border-[#2C3E49]',
    amber:
      'bg-[#FEF6E9] dark:bg-[#332515] text-[#B87A2B] dark:text-[#F4A261] border border-[#F9E2BE] dark:border-[#523C20]',
    outline:
      'bg-transparent border border-[#E8DFD5] dark:border-[#38332E] text-[#6B5E57] dark:text-[#B8ACA4]',
  };

  const sizeStyles = {
    sm: 'text-[11px] px-2 py-0.5 rounded-full font-medium',
    md: 'text-xs px-2.5 py-1 rounded-full font-medium',
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 transition-colors ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
    >
      {children}
    </span>
  );
}
