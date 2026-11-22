'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { AppLayout } from '../../components/layout/AppLayout';
import { StatsOverview } from '../../components/profile/StatsOverview';
import { PreferencesManager } from '../../components/profile/PreferencesManager';
import { PrivacyControls } from '../../components/profile/PrivacyControls';
import { Spinner } from '../../components/ui/Spinner';
import { api } from '../../lib/api';
import { ProfileResponse } from '../../types/api';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import { Edit2, Check } from 'lucide-react';

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
        {/* User Hero Banner */}
        <div className="p-6 sm:p-8 rounded-3xl bg-white dark:bg-[#201D1B] border border-[#EAE2D8] dark:border-[#38332E] shadow-2xs mb-8 flex flex-col sm:flex-row sm:items-center justify-between gap-6">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-3xl bg-[#E07A5F] text-white flex items-center justify-center font-serif text-2xl font-semibold shadow-md shadow-[#E07A5F]/20">
              {(profile?.user.username || 'V')[0].toUpperCase()}
            </div>

            <div>
              {isEditingUsername ? (
                <form
                  onSubmit={handleUpdateUsername}
                  className="flex items-center gap-2 mb-1"
                >
                  <input
                    type="text"
                    value={newUsername}
                    onChange={(e) => setNewUsername(e.target.value)}
                    className="px-2.5 py-1 rounded-xl text-sm bg-[#F7F2EC] dark:bg-[#2C2926] border border-[#D96B43] text-[#2C2623] dark:text-[#F7F3EE] focus:outline-hidden"
                    autoFocus
                  />
                  <button
                    type="submit"
                    disabled={isUpdatingUsername}
                    className="p-1.5 rounded-lg bg-[#D96B43] text-white hover:bg-[#C55730] transition-colors"
                  >
                    <Check className="w-4 h-4" />
                  </button>
                  <button
                    type="button"
                    onClick={() => setIsEditingUsername(false)}
                    className="text-xs text-[#8C7E74] hover:underline"
                  >
                    Cancel
                  </button>
                </form>
              ) : (
                <div className="flex items-center gap-2">
                  <h2 className="font-serif text-2xl font-medium text-[#2C2623] dark:text-[#F7F3EE]">
                    {profile?.user.username || 'Loading...'}
                  </h2>
                  <button
                    onClick={() => setIsEditingUsername(true)}
                    className="p-1 rounded-md text-[#A89C94] hover:text-[#D96B43] transition-colors"
                    title="Edit username"
                  >
                    <Edit2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              )}
              <p className="text-xs text-[#8C7E74]">{profile?.user.email}</p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="px-3 py-1.5 rounded-full bg-[#FAF2EB] text-[#D96B43] text-xs font-medium border border-[#F3C4B3]/60">
              Personal Companion Mode
            </span>
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
