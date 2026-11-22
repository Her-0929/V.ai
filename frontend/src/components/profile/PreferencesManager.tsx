'use client';

import React, { useState } from 'react';
import { Sliders, Plus, Trash2 } from 'lucide-react';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { api } from '../../lib/api';
import { PreferenceResponse } from '../../types/api';
import { useToast } from '../../context/ToastContext';

interface PreferencesManagerProps {
  preferences: PreferenceResponse[];
  onRefresh: () => void;
}

export function PreferencesManager({
  preferences,
  onRefresh,
}: PreferencesManagerProps) {
  const { success: toastSuccess, error: toastError } = useToast();

  const [newKey, setNewKey] = useState('');
  const [newValue, setNewValue] = useState('');
  const [isAdding, setIsAdding] = useState(false);

  const handleAddPreference = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newKey.trim()) return;

    setIsAdding(true);
    try {
      let parsedValue: Record<string, unknown>;
      try {
        parsedValue = JSON.parse(newValue);
      } catch {
        parsedValue = { value: newValue };
      }

      await api.setPreference(newKey.trim(), parsedValue);
      toastSuccess(`Preference "${newKey}" updated.`);
      setNewKey('');
      setNewValue('');
      onRefresh();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to save preference.';
      toastError(msg);
    } finally {
      setIsAdding(false);
    }
  };

  const handleDelete = async (key: string) => {
    try {
      await api.deletePreference(key);
      toastSuccess(`Preference "${key}" removed.`);
      onRefresh();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to delete preference.';
      toastError(msg);
    }
  };

  return (
    <div className="p-6 sm:p-8 rounded-3xl bg-white dark:bg-[#201D1B] border border-[#EAE2D8] dark:border-[#38332E] shadow-2xs mb-8 space-y-6">
      <div className="flex items-center gap-2 pb-4 border-b border-[#F2ECE3] dark:border-[#2D2926]">
        <Sliders className="w-5 h-5 text-[#D96B43]" />
        <div>
          <h3 className="font-serif text-lg font-medium text-[#2C2623] dark:text-[#F7F3EE]">
            Companion Preferences
          </h3>
          <p className="text-xs text-[#7C6E64] dark:text-[#A89C94]">
            Custom guidelines, tone variations, or behavioral hints for HER.
          </p>
        </div>
      </div>

      {/* Existing Preferences List */}
      <div className="space-y-2">
        {preferences.length === 0 ? (
          <p className="text-xs text-[#A89C94] italic p-4 text-center bg-[#FAF7F2] dark:bg-[#181615] rounded-2xl border border-[#E8DFD5] dark:border-[#2C2926]">
            No custom preferences set yet. Default Samantha personality profile is active.
          </p>
        ) : (
          preferences.map((pref) => (
            <div
              key={pref.id}
              className="p-3.5 rounded-2xl bg-[#FAF7F2] dark:bg-[#181615] border border-[#E8DFD5] dark:border-[#2C2926] flex items-center justify-between gap-3 text-xs"
            >
              <div className="min-w-0">
                <span className="font-semibold text-[#D96B43] dark:text-[#EB8D74] font-mono mr-2">
                  {pref.key}:
                </span>
                <span className="text-[#3D352F] dark:text-[#D1C6BD] font-mono">
                  {JSON.stringify(pref.value)}
                </span>
              </div>
              <button
                onClick={() => handleDelete(pref.key)}
                className="p-1 rounded-lg text-[#A89C94] hover:text-rose-600 hover:bg-rose-50 dark:hover:bg-rose-950/40 transition-colors"
                title="Delete preference"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          ))
        )}
      </div>

      {/* Add New Preference Form */}
      <form onSubmit={handleAddPreference} className="pt-4 border-t border-[#F2ECE3] dark:border-[#2D2926] space-y-3">
        <div className="text-xs font-semibold uppercase tracking-wider text-[#7C6E64] dark:text-[#A89C94]">
          Add / Update Preference
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <Input
            placeholder="Key (e.g. tone, response_length)"
            value={newKey}
            onChange={(e) => setNewKey(e.target.value)}
            required
          />
          <Input
            placeholder='Value (e.g. "warm", "thoughtful")'
            value={newValue}
            onChange={(e) => setNewValue(e.target.value)}
            required
          />
        </div>
        <div className="flex justify-end">
          <Button
            type="submit"
            variant="secondary"
            size="sm"
            isLoading={isAdding}
            disabled={!newKey.trim() || !newValue.trim()}
          >
            <Plus className="w-3.5 h-3.5 mr-1 text-[#D96B43]" />
            <span>Save Preference</span>
          </Button>
        </div>
      </form>
    </div>
  );
}
