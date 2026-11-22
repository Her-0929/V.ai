'use client';

import React from 'react';
import { Sidebar } from './Sidebar';
import { Header } from './Header';

export function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen bg-[#FAF7F2] dark:bg-[#151413] text-[#2C2623] dark:text-[#F5EFEB]">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Header />
        <main className="flex-1 flex flex-col min-w-0">{children}</main>
      </div>
    </div>
  );
}
