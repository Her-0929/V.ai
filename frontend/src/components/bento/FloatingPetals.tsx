'use client';

import React, { useEffect, useState } from 'react';

export function FloatingPetals() {
  const [petals, setPetals] = useState<
    { id: number; left: number; delay: number; duration: number; size: number; emoji: string }[]
  >([]);

  useEffect(() => {
    // Royal blue sparkle and blue heart accents along with stars & blooms
    const symbols = ['💙', '✨', '💎', '💫', '🌟', '🩵'];
    const items = Array.from({ length: 18 }).map((_, i) => ({
      id: i,
      left: Math.random() * 95,
      delay: Math.random() * 8,
      duration: 12 + Math.random() * 10,
      size: 14 + Math.random() * 12,
      emoji: symbols[Math.floor(Math.random() * symbols.length)],
    }));
    setPetals(items);
  }, []);

  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden z-20">
      {petals.map((petal) => (
        <span
          key={petal.id}
          className="absolute opacity-35 select-none animate-floatDown"
          style={{
            left: `${petal.left}%`,
            top: '-50px',
            fontSize: `${petal.size}px`,
            animationDelay: `${petal.delay}s`,
            animationDuration: `${petal.duration}s`,
            animationIterationCount: 'infinite',
          }}
        >
          {petal.emoji}
        </span>
      ))}
    </div>
  );
}
