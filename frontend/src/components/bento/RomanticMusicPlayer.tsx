'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Volume2, VolumeX, Music, Heart, Disc } from 'lucide-react';

export function RomanticMusicPlayer() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [volume, setVolume] = useState<number>(0.6);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  useEffect(() => {
    // Create native HTML5 audio element
    const audio = new Audio('/audio/romantic_bgm.mp3');
    audio.loop = true;
    audio.volume = volume;
    audioRef.current = audio;

    const handleEnded = () => setIsPlaying(false);
    const handlePause = () => setIsPlaying(false);
    const handlePlay = () => setIsPlaying(true);

    audio.addEventListener('ended', handleEnded);
    audio.addEventListener('pause', handlePause);
    audio.addEventListener('play', handlePlay);

    return () => {
      audio.removeEventListener('ended', handleEnded);
      audio.removeEventListener('pause', handlePause);
      audio.removeEventListener('play', handlePlay);
      audio.pause();
      audio.src = '';
    };
  }, []);

  const toggleMusic = async () => {
    if (!audioRef.current) return;

    if (isPlaying) {
      audioRef.current.pause();
    } else {
      try {
        audioRef.current.volume = volume;
        await audioRef.current.play();
      } catch (err) {
        console.warn('Playback error:', err);
      }
    }
  };

  const handleVolumeChange = (newVol: number) => {
    setVolume(newVol);
    if (audioRef.current) {
      audioRef.current.volume = newVol;
    }
  };

  return (
    <div className="flex items-center gap-2">
      <button
        type="button"
        onClick={toggleMusic}
        className={`relative px-4 py-2 rounded-2xl flex items-center gap-2.5 transition-all text-xs font-semibold backdrop-blur-md shadow-xs select-none ${
          isPlaying
            ? 'bg-blue-600 text-white shadow-blue-500/30 ring-2 ring-blue-400'
            : 'bg-white/90 dark:bg-slate-900/90 text-blue-900 dark:text-blue-100 border border-blue-200 dark:border-blue-900/60 hover:bg-white dark:hover:bg-slate-800'
        }`}
        title={isPlaying ? 'Pause Romantic Music' : 'Play Romantic Background Music'}
      >
        <div className="flex items-center gap-2">
          {isPlaying ? (
            <>
              <Disc className="w-4 h-4 animate-spin text-blue-200" />
              <div className="flex flex-col text-left">
                <span className="flex items-center gap-1 font-bold">
                  <span>Romantic Piano BGM</span>
                  <Heart className="w-3 h-3 fill-current text-blue-200 animate-ping" />
                </span>
                <span className="text-[9px] text-blue-100 font-normal">
                  Playing for you 🎵
                </span>
              </div>
            </>
          ) : (
            <>
              <Music className="w-4 h-4 text-blue-600 dark:text-blue-400" />
              <span>Play Romantic BGM 🎵</span>
            </>
          )}
        </div>
      </button>

      {/* Quick Mute / Volume slider toggle */}
      {isPlaying && (
        <div className="hidden sm:flex items-center gap-1.5 px-3 py-1.5 rounded-2xl bg-white/80 dark:bg-slate-900/80 border border-blue-200 dark:border-blue-900/60 animate-fadeIn">
          <button
            type="button"
            onClick={() => handleVolumeChange(volume > 0 ? 0 : 0.6)}
            className="text-blue-600 dark:text-blue-400"
          >
            {volume === 0 ? <VolumeX className="w-3.5 h-3.5" /> : <Volume2 className="w-3.5 h-3.5" />}
          </button>
          <input
            type="range"
            min="0"
            max="1"
            step="0.05"
            value={volume}
            onChange={(e) => handleVolumeChange(parseFloat(e.target.value))}
            className="w-16 h-1.5 accent-blue-600 cursor-pointer bg-slate-200 rounded-lg"
            title="Adjust volume"
          />
        </div>
      )}
    </div>
  );
}
