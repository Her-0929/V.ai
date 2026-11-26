'use client';

import React, { useState, useEffect } from 'react';
import { Cake, Sparkles } from 'lucide-react';

export function BirthdayCountdownTimer() {
  const [timeLeft, setTimeLeft] = useState<{
    days: number;
    hours: number;
    minutes: number;
    seconds: number;
    isBirthday: boolean;
  }>({ days: 0, hours: 0, minutes: 0, seconds: 0, isBirthday: false });

  useEffect(() => {
    const calculateTime = () => {
      const now = new Date();
      const currentYear = now.getFullYear();

      // November is month index 10 (0-indexed)
      let bday = new Date(currentYear, 10, 29, 0, 0, 0);

      if (now.getTime() > bday.getTime() + 24 * 60 * 60 * 1000) {
        bday = new Date(currentYear + 1, 10, 29, 0, 0, 0);
      }

      const diff = bday.getTime() - now.getTime();

      if (now.getMonth() === 10 && now.getDate() === 29) {
        setTimeLeft({ days: 0, hours: 0, minutes: 0, seconds: 0, isBirthday: true });
        return;
      }

      if (diff <= 0) {
        setTimeLeft({ days: 0, hours: 0, minutes: 0, seconds: 0, isBirthday: true });
        return;
      }

      const days = Math.floor(diff / (1000 * 60 * 60 * 24));
      const hours = Math.floor((diff / (1000 * 60 * 60)) % 24);
      const minutes = Math.floor((diff / 1000 / 60) % 60);
      const seconds = Math.floor((diff / 1000) % 60);

      setTimeLeft({ days, hours, minutes, seconds, isBirthday: false });
    };

    calculateTime();
    const interval = setInterval(calculateTime, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex flex-col items-center justify-center p-5 rounded-3xl bg-gradient-to-br from-blue-600/10 via-indigo-600/10 to-sky-500/10 border border-blue-200/80 dark:border-blue-900/50 relative overflow-hidden h-full shadow-2xs">
      <div className="flex items-center gap-2 mb-2">
        <Cake className="w-4 h-4 text-blue-600 dark:text-blue-400 animate-bounce" />
        <span className="text-[11px] font-bold uppercase tracking-wider text-blue-700 dark:text-blue-300">
          Birthday Countdown
        </span>
        <Sparkles className="w-3.5 h-3.5 text-amber-400" />
      </div>

      <div className="text-center mb-3">
        <h4 className="font-serif text-lg font-bold text-slate-900 dark:text-blue-50">
          {timeLeft.isBirthday ? "Happy Birthday, My Queen! 🎉" : "Counting Down to Nov 29 ✨"}
        </h4>
        <p className="text-[11px] text-slate-600 dark:text-blue-200/70">
          {timeLeft.isBirthday
            ? "Today the whole world celebrates you!"
            : "Every second closer to celebrating your existence"}
        </p>
      </div>

      <div className="grid grid-cols-4 gap-2 w-full max-w-[280px]">
        {[
          { label: 'Days', val: timeLeft.days },
          { label: 'Hours', val: timeLeft.hours },
          { label: 'Mins', val: timeLeft.minutes },
          { label: 'Secs', val: timeLeft.seconds },
        ].map((unit, i) => (
          <div
            key={i}
            className="flex flex-col items-center justify-center py-2 px-1 rounded-2xl bg-white/90 dark:bg-slate-900/80 border border-blue-100 dark:border-blue-950 shadow-2xs backdrop-blur-xs"
          >
            <span className="font-serif text-lg sm:text-xl font-bold text-blue-600 dark:text-blue-400">
              {String(unit.val).padStart(2, '0')}
            </span>
            <span className="text-[9px] uppercase tracking-wider text-slate-500 dark:text-slate-400 font-semibold">
              {unit.label}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
