'use client';

import React, { useState } from 'react';
import { Download, ShieldCheck, LogOut, KeyRound } from 'lucide-react';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { Modal } from '../ui/Modal';
import { api } from '../../lib/api';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';

export function PrivacyControls() {
  const { user, logout, login, register } = useAuth();
  const { success: toastSuccess, error: toastError } = useToast();

  const [isExporting, setIsExporting] = useState(false);
  const [isSwitchModalOpen, setIsSwitchModalOpen] = useState(false);
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');

  const [authUsername, setAuthUsername] = useState('');
  const [authEmail, setAuthEmail] = useState('');
  const [authPassword, setAuthPassword] = useState('');
  const [isAuthSubmitting, setIsAuthSubmitting] = useState(false);

  const handleDownloadGDPR = async () => {
    setIsExporting(true);
    try {
      const dump = await api.getPrivacyExport();
      const blob = new Blob([JSON.stringify(dump, null, 2)], {
        type: 'application/json',
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `her_ai_gdpr_export_${user?.username || 'user'}_${new Date()
        .toISOString()
        .substring(0, 10)}.json`;
      a.click();
      URL.revokeObjectURL(url);
      toastSuccess('GDPR privacy archive downloaded.');
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Privacy export failed.';
      toastError(msg);
    } finally {
      setIsExporting(false);
    }
  };

  const handleAuthSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsAuthSubmitting(true);
    try {
      if (authMode === 'login') {
        const ok = await login(authUsername, authPassword);
        if (ok) {
          toastSuccess(`Logged in as ${authUsername}!`);
          setIsSwitchModalOpen(false);
        } else {
          toastError('Invalid username or password.');
        }
      } else {
        const ok = await register(authUsername, authEmail, authPassword);
        if (ok) {
          toastSuccess(`Registered and logged in as ${authUsername}!`);
          setIsSwitchModalOpen(false);
        } else {
          toastError('Registration failed.');
        }
      }
    } finally {
      setIsAuthSubmitting(false);
    }
  };

  const handleQuickVivekLogin = async () => {
    setIsAuthSubmitting(true);
    try {
      await login('vivek', 'HerAiVivekSecure2026!');
      toastSuccess('Logged in as tenant Vivek!');
      setIsSwitchModalOpen(false);
    } catch {
      toastError('Could not login as Vivek.');
    } finally {
      setIsAuthSubmitting(false);
    }
  };

  return (
    <div className="p-6 sm:p-8 rounded-3xl bg-white dark:bg-[#201D1B] border border-[#EAE2D8] dark:border-[#38332E] shadow-2xs space-y-6">
      <div className="flex items-center gap-2 pb-4 border-b border-[#F2ECE3] dark:border-[#2D2926]">
        <ShieldCheck className="w-5 h-5 text-emerald-600 dark:text-emerald-400" />
        <div>
          <h3 className="font-serif text-lg font-medium text-[#2C2623] dark:text-[#F7F3EE]">
            Privacy, Compliance & Account
          </h3>
          <p className="text-xs text-[#7C6E64] dark:text-[#A89C94]">
            Data ownership, tenant isolation and authentication sessions.
          </p>
        </div>
      </div>

      <div className="space-y-4">
        {/* GDPR Privacy Export Button */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-2xl bg-[#FAF7F2] dark:bg-[#181615] border border-[#E8DFD5] dark:border-[#2C2926]">
          <div>
            <div className="font-semibold text-xs text-[#2C2623] dark:text-[#F7F3EE]">
              Full GDPR Data Export
            </div>
            <div className="text-[11px] text-[#8C7E74]">
              Download complete archive of your profile, preferences, and all memories with source provenance.
            </div>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={handleDownloadGDPR}
            isLoading={isExporting}
          >
            <Download className="w-3.5 h-3.5 mr-1" />
            <span>Download Archive</span>
          </Button>
        </div>

        {/* User Account Controls */}
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 p-4 rounded-2xl bg-[#FAF7F2] dark:bg-[#181615] border border-[#E8DFD5] dark:border-[#2C2926]">
          <div>
            <div className="font-semibold text-xs text-[#2C2623] dark:text-[#F7F3EE]">
              Current Identity: {user?.username} ({user?.email})
            </div>
            <div className="text-[11px] text-[#8C7E74]">
              Authenticated with Argon2id and JWT bearer token.
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="secondary"
              size="sm"
              onClick={() => setIsSwitchModalOpen(true)}
            >
              <KeyRound className="w-3.5 h-3.5 mr-1 text-[#D96B43]" />
              <span>Switch User</span>
            </Button>
            <Button variant="ghost" size="sm" onClick={logout}>
              <LogOut className="w-3.5 h-3.5 mr-1" />
              <span>Sign Out</span>
            </Button>
          </div>
        </div>
      </div>

      {/* Switch User / Login / Register Modal */}
      <Modal
        isOpen={isSwitchModalOpen}
        onClose={() => setIsSwitchModalOpen(false)}
        title={authMode === 'login' ? 'Sign In to HER AI' : 'Create New Account'}
        description="Authenticate to access your isolated memories and conversations."
        maxWidth="sm"
      >
        <div className="space-y-4">
          {/* Quick Vivek Demo Button */}
          <div className="p-3 rounded-xl bg-[#FAF2EB] dark:bg-[#2C211A] border border-[#F3C4B3]/60 dark:border-[#52342A] flex items-center justify-between gap-2">
            <div>
              <div className="font-semibold text-xs text-[#D96B43]">
                Tenant Vivek (31 Ingested Memories)
              </div>
              <div className="text-[10px] text-[#8C7E74]">
                Instant one-click demo login
              </div>
            </div>
            <button
              type="button"
              onClick={handleQuickVivekLogin}
              disabled={isAuthSubmitting}
              className="px-2.5 py-1 rounded-lg bg-[#D96B43] text-white text-xs font-medium hover:bg-[#C55730] transition-colors cursor-pointer"
            >
              Log in as Vivek
            </button>
          </div>

          <div className="flex items-center gap-2">
            <div className="flex-1 h-px bg-[#E8DFD5] dark:bg-[#332E2A]" />
            <span className="text-[10px] uppercase text-[#A89C94] font-medium">Or</span>
            <div className="flex-1 h-px bg-[#E8DFD5] dark:bg-[#332E2A]" />
          </div>

          <form onSubmit={handleAuthSubmit} className="space-y-3">
            <Input
              label="Username or Email"
              value={authUsername}
              onChange={(e) => setAuthUsername(e.target.value)}
              required
            />
            {authMode === 'register' && (
              <Input
                label="Email Address"
                type="email"
                value={authEmail}
                onChange={(e) => setAuthEmail(e.target.value)}
                required
              />
            )}
            <Input
              label="Password"
              type="password"
              value={authPassword}
              onChange={(e) => setAuthPassword(e.target.value)}
              required
            />

            <div className="pt-2 flex flex-col gap-2">
              <Button type="submit" variant="primary" isLoading={isAuthSubmitting}>
                {authMode === 'login' ? 'Sign In' : 'Create Account'}
              </Button>

              <button
                type="button"
                onClick={() =>
                  setAuthMode(authMode === 'login' ? 'register' : 'login')
                }
                className="text-xs text-[#7C6E64] hover:text-[#D96B43] text-center"
              >
                {authMode === 'login'
                  ? "Don't have an account? Create one"
                  : 'Already registered? Sign In'}
              </button>
            </div>
          </form>
        </div>
      </Modal>
    </div>
  );
}
