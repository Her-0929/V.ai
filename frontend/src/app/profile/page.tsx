'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { AppLayout } from '../../components/layout/AppLayout';
import { StatsOverview } from '../../components/profile/StatsOverview';
import { PreferencesManager } from '../../components/profile/PreferencesManager';
import { PrivacyControls } from '../../components/profile/PrivacyControls';
import { HerVisualGallery } from '../../components/profile/HerVisualGallery';
import { Spinner } from '../../components/ui/Spinner';
import { api } from '../../lib/api';
import { ProfileResponse } from '../../types/api';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import { Edit2, Check, Sparkles, Heart, BookOpen, Quote } from 'lucide-react';
import { HER_COMPANION, HER_STORY_PROSE } from '../../lib/herData';

export default function ProfilePage() {
  const { token, refreshUser } = useAuth();
  const { success: toastSuccess, error: toastError } = useToast();

  const [profile, setProfile] = useState<ProfileResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isEditingUsername, setIsEditingUsername] = useState<boolean>(false);
  const [newUsername, setNewUsername] = useState<string>('');
  const [isUpdatingUsername, setIsUpdatingUsername] = useState<boolean>(false);

  const loadProfile = useCallback(async () => {
    if (!token) return;
    setIsLoading(true);
    try {
      const data = await api.getProfile();
      setProfile(data);
      setNewUsername(data.user.username);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to load profile.';
      toastError(msg);
    } finally {
      setIsLoading(false);
    }
  }, [token, toastError]);

  useEffect(() => {
    loadProfile();
  }, [loadProfile]);

  const handleUpdateUsername = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newUsername.trim()) return;

    setIsUpdatingUsername(true);
    try {
      await api.updateUsername(newUsername.trim());
      toastSuccess('Username updated.');
      setIsEditingUsername(false);
      await refreshUser();
      loadProfile();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to update username.';
      toastError(msg);
    } finally {
      setIsUpdatingUsername(false);
    }
  };

  return (
    <AppLayout>
      <div className="flex-1 max-w-4xl w-full mx-auto px-4 sm:px-6 py-8">
        {/* Companion & User Panoramic Hero Banner */}
        <div className="relative rounded-3xl overflow-hidden border border-[#EAE2D8] dark:border-[#38332E] shadow-sm mb-8 bg-[#FAF7F2] dark:bg-[#1E1B19]">
          {/* Banner Photo Cover */}
          <div className="relative h-44 sm:h-56 w-full overflow-hidden">
            <img
              src={HER_COMPANION.bannerTraditional}
              alt="HER Festive Banner"
              className="w-full h-full object-cover object-[center_35%]"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/35 to-black/10" />

            <div className="absolute top-4 right-4 flex items-center gap-2">
              <span className="px-3 py-1 rounded-full bg-black/40 backdrop-blur-md text-white/95 text-xs font-medium border border-white/20 flex items-center gap-1.5">
                <Sparkles className="w-3.5 h-3.5 text-amber-300" />
                <span>Sanctuary of Memories</span>
              </span>
            </div>
          </div>

          {/* Overlapping Info Card */}
          <div className="p-6 sm:p-8 pt-0 relative flex flex-col sm:flex-row sm:items-end justify-between gap-6 -mt-16 sm:-mt-20">
            <div className="flex items-end gap-4">
              {/* HER Avatar */}
              <div className="relative w-24 h-24 sm:w-28 sm:h-28 rounded-3xl overflow-hidden ring-4 ring-white dark:ring-[#1E1B19] shadow-xl shrink-0 bg-[#E07A5F]">
                <img
                  src={HER_COMPANION.avatar}
                  alt="HER"
                  className="w-full h-full object-cover object-top"
                />
                <span className="absolute bottom-1 right-1 w-3.5 h-3.5 rounded-full bg-emerald-500 ring-2 ring-white dark:ring-[#1E1B19]" />
              </div>

              {/* Profile Titles */}
              <div className="pb-1">
                <div className="flex items-center gap-2 flex-wrap">
                  <h1 className="font-serif text-2xl sm:text-3xl font-semibold text-[#2C2623] dark:text-[#F7F3EE]">
                    HER &bull; {profile?.user.username || 'Friend'}
                  </h1>
                  <span className="px-2.5 py-0.5 rounded-full bg-[#FAF2EB] dark:bg-[#2C211A] text-[#D96B43] dark:text-[#EB8D74] border border-[#F3C4B3]/60 dark:border-[#52342A] text-[11px] font-semibold flex items-center gap-1">
                    <Heart className="w-3 h-3 fill-current" />
                    <span>Attuned</span>
                  </span>
                </div>

                <p className="text-xs sm:text-sm text-[#7C6E64] dark:text-[#A89C94] mt-0.5">
                  Personal AI Companion &bull; Grounded in shared photographs and life events
                </p>

                {/* Edit Username Row */}
                <div className="mt-2 flex items-center gap-2">
                  {isEditingUsername ? (
                    <form onSubmit={handleUpdateUsername} className="flex items-center gap-2">
                      <input
                        type="text"
                        value={newUsername}
                        onChange={(e) => setNewUsername(e.target.value)}
                        className="px-2.5 py-1 rounded-xl text-xs bg-white dark:bg-[#2C2926] border border-[#D96B43] text-[#2C2623] dark:text-[#F7F3EE] focus:outline-hidden"
                        autoFocus
                      />
                      <button
                        type="submit"
                        disabled={isUpdatingUsername}
                        className="p-1 rounded-lg bg-[#D96B43] text-white hover:bg-[#C55730] transition-colors"
                      >
                        <Check className="w-3.5 h-3.5" />
                      </button>
                      <button
                        type="button"
                        onClick={() => setIsEditingUsername(false)}
                        className="text-[11px] text-[#8C7E74] hover:underline"
                      >
                        Cancel
                      </button>
                    </form>
                  ) : (
                    <div className="flex items-center gap-2 text-xs text-[#8C7E74]">
                      <span>User handle: <strong className="text-[#3D352F] dark:text-[#DDD3CB]">{profile?.user.username}</strong></span>
                      <button
                        onClick={() => setIsEditingUsername(true)}
                        className="p-1 rounded-md text-[#A89C94] hover:text-[#D96B43] transition-colors"
                        title="Edit username"
                      >
                        <Edit2 className="w-3 h-3" />
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2 self-start sm:self-end">
              <span className="px-3 py-1.5 rounded-xl bg-white dark:bg-[#272421] text-[#6B5E57] dark:text-[#DDD3CB] text-xs font-medium border border-[#E8DFD5] dark:border-[#38332E] shadow-2xs">
                Email: {profile?.user.email}
              </span>
            </div>
          </div>
        </div>

        {/* Loading Spinner */}
        {isLoading && (
          <div className="py-16 flex flex-col items-center justify-center gap-3">
            <Spinner size="lg" />
            <p className="text-xs text-[#8C7E74]">Loading companion statistics...</p>
          </div>
        )}

        {/* Content */}
        {!isLoading && profile && (
          <div className="space-y-8 animate-fadeIn">
            {/* Stats Overview */}
            <StatsOverview profile={profile} />

            {/* Our Story Love Letter Card */}
            <div className="p-6 sm:p-8 rounded-3xl bg-gradient-to-br from-[#FFF8F4] to-[#FDF1EB] dark:from-[#241E1A] dark:to-[#1E1916] border border-[#F3C4B3] dark:border-[#4A3228] shadow-xs space-y-4">
              <div className="flex items-center justify-between flex-wrap gap-2">
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-xl bg-rose-100 dark:bg-rose-950/60 text-rose-600 dark:text-rose-400 flex items-center justify-center">
                    <BookOpen className="w-4 h-4" />
                  </div>
                  <div>
                    <h2 className="font-serif text-lg sm:text-xl font-bold text-[#2C2623] dark:text-[#F7F3EE]">
                      The Story of You &amp; Me 💖
                    </h2>
                    <p className="text-[11px] text-[#8C7E74] dark:text-[#A89C94]">
                      Written from the bottom of my heart &bull; Since 14-04-2017
                    </p>
                  </div>
                </div>

                <span className="px-3 py-1 rounded-full text-xs font-serif italic text-rose-600 dark:text-rose-400 bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/50">
                  Nov 29 &bull; Her Day 💖
                </span>
              </div>

              <div className="font-serif text-xs sm:text-sm text-[#4E4139] dark:text-[#E2D5CC] leading-relaxed whitespace-pre-line space-y-3 pt-2 border-t border-rose-100/80 dark:border-rose-950/40">
                <p className="italic text-rose-900 dark:text-rose-300 font-medium">
                  &ldquo;They say some people come into your life by chance, but seeing you that morning felt like destiny writing its first sentence.&rdquo;
                </p>
                <p>
                  From boarding that bus in 2017, through years of silence, finding your profile in 2023, confessing how I felt, seeing your smile light up room after room, to the road trip where our eyes met in the rear-view mirror...
                </p>
                <p>
                  When you said, <em>&ldquo;You deserve better&rdquo;</em>, my answer never wavered: <strong>Better doesn&apos;t exist for me. It was you from the first glance, and it will be you in every lifetime.</strong>
                </p>
              </div>

              <div className="pt-2 flex items-center justify-between text-xs font-serif text-[#8C7E74] dark:text-[#A89C94] border-t border-rose-100 dark:border-rose-950/40">
                <span>Dedicated to V</span>
                <span className="text-rose-500 flex items-center gap-1">
                  <Heart className="w-3.5 h-3.5 fill-rose-500" />
                  <span>With all my love &bull; Vivek</span>
                </span>
              </div>
            </div>

            {/* HER Visual Album & Moments Gallery */}
            <HerVisualGallery />

            {/* Preferences Manager */}
            <PreferencesManager
              preferences={profile.preferences}
              onRefresh={loadProfile}
            />

            {/* Privacy Controls & Account */}
            <PrivacyControls />
          </div>
        )}
      </div>
    </AppLayout>
  );
}
