'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Volume2, Music, Heart } from 'lucide-react';

export function RomanticMusicPlayer() {
  const [isPlaying, setIsPlaying] = useState(false);
  const audioCtxRef = useRef<AudioContext | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const startMusic = () => {
    try {
      const AudioCtx = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
      const ctx = new AudioCtx();
      audioCtxRef.current = ctx;

      const chords = [
        [174.61, 220.0, 261.63, 329.63], // Fmaj7
        [146.83, 220.0, 261.63, 311.13, 349.23], // Dm9
        [116.54, 174.61, 220.0, 261.63, 329.63], // Bbmaj7
        [130.81, 196.0, 261.63, 329.63, 392.0], // C6/9
      ];

      let chordIndex = 0;

      const playChord = () => {
        if (!audioCtxRef.current || audioCtxRef.current.state === 'closed') return;
        const now = audioCtxRef.current.currentTime;
        const chord = chords[chordIndex % chords.length];
        chordIndex++;

        chord.forEach((freq, i) => {
          if (!audioCtxRef.current) return;
          const osc = audioCtxRef.current.createOscillator();
          const gain = audioCtxRef.current.createGain();

          osc.type = i === 0 ? 'triangle' : 'sine';
          osc.frequency.setValueAtTime(freq, now);

          gain.gain.setValueAtTime(0.0001, now);
          gain.gain.linearRampToValueAtTime(0.05 / (i + 1), now + 0.8 + i * 0.1);
          gain.gain.exponentialRampToValueAtTime(0.0001, now + 3.8);

          osc.connect(gain);
          gain.connect(audioCtxRef.current.destination);

          osc.start(now);
          osc.stop(now + 4.0);
        });
      };

      playChord();
      intervalRef.current = setInterval(playChord, 3500);
      setIsPlaying(true);
    } catch {
      // Autoplay limitations
    }
  };

  const stopMusic = () => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    if (audioCtxRef.current) {
      audioCtxRef.current.close().catch(() => {});
      audioCtxRef.current = null;
    }
    setIsPlaying(false);
  };

  const toggleMusic = () => {
    if (isPlaying) {
      stopMusic();
    } else {
      startMusic();
    }
  };

  useEffect(() => {
    return () => {
      stopMusic();
    };
  }, []);

  return (
    <button
      onClick={toggleMusic}
      className={`relative px-4 py-2 rounded-2xl flex items-center gap-2.5 transition-all text-xs font-semibold backdrop-blur-md shadow-xs ${
        isPlaying
          ? 'bg-blue-600 text-white shadow-blue-500/25 animate-pulse'
          : 'bg-white/80 dark:bg-slate-800/80 text-blue-900 dark:text-blue-100 border border-blue-200 dark:border-blue-900/60 hover:bg-white dark:hover:bg-slate-800'
      }`}
      title={isPlaying ? 'Pause Melody' : 'Play Gentle Lofi Melody'}
    >
      <div className="flex items-center gap-1.5">
        {isPlaying ? (
          <>
            <Volume2 className="w-4 h-4 animate-bounce" />
            <span className="flex items-center gap-1">
              <span>Melody Playing</span>
              <Heart className="w-3 h-3 fill-current animate-ping text-blue-200" />
            </span>
          </>
        ) : (
          <>
            <Music className="w-4 h-4 text-blue-600 dark:text-blue-400" />
            <span>Play Sweet Melody</span>
          </>
        )}
      </div>
    </button>
  );
}
