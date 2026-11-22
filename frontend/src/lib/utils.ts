/**
 * Utility functions for HER AI Frontend
 */

export function cn(...classes: (string | undefined | null | false)[]): string {
  return classes.filter(Boolean).join(' ');
}

export function formatDate(dateString?: string | null): string {
  if (!dateString) return 'Undated';
  try {
    const d = new Date(dateString);
    if (isNaN(d.getTime())) return dateString;
    return d.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  } catch {
    return dateString;
  }
}

export function formatDateTime(dateTimeString?: string | null): string {
  if (!dateTimeString) return '';
  try {
    const d = new Date(dateTimeString);
    if (isNaN(d.getTime())) return dateTimeString;
    return d.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    });
  } catch {
    return dateTimeString;
  }
}

export function formatPrecision(precision?: string): string {
  switch (precision?.toLowerCase()) {
    case 'day':
      return 'Exact Day';
    case 'month':
      return 'Specific Month';
    case 'year':
      return 'Year Level';
    case 'decade':
      return 'Decade Era';
    default:
      return 'Unspecified';
  }
}

export function getEmotionColor(emotion?: string): {
  bg: string;
  text: string;
  border: string;
  dot: string;
} {
  const norm = emotion?.toLowerCase() || '';
  if (['happiness', 'excitement', 'motivation', 'gratitude'].includes(norm)) {
    return {
      bg: 'bg-amber-50 dark:bg-amber-950/40',
      text: 'text-amber-800 dark:text-amber-300',
      border: 'border-amber-200 dark:border-amber-800',
      dot: 'bg-amber-500',
    };
  }
  if (['affection', 'love'].includes(norm)) {
    return {
      bg: 'bg-rose-50 dark:bg-rose-950/40',
      text: 'text-rose-800 dark:text-rose-300',
      border: 'border-rose-200 dark:border-rose-800',
      dot: 'bg-rose-500',
    };
  }
  if (['sadness', 'loneliness', 'disappointment'].includes(norm)) {
    return {
      bg: 'bg-sky-50 dark:bg-sky-950/40',
      text: 'text-sky-800 dark:text-sky-300',
      border: 'border-sky-200 dark:border-sky-800',
      dot: 'bg-sky-500',
    };
  }
  if (['stress', 'anxiety', 'frustration', 'confusion'].includes(norm)) {
    return {
      bg: 'bg-orange-50 dark:bg-orange-950/40',
      text: 'text-orange-800 dark:text-orange-300',
      border: 'border-orange-200 dark:border-orange-800',
      dot: 'bg-orange-500',
    };
  }
  return {
    bg: 'bg-stone-50 dark:bg-stone-900',
    text: 'text-stone-700 dark:text-stone-300',
    border: 'border-stone-200 dark:border-stone-800',
    dot: 'bg-stone-400',
  };
}

export function formatBytes(bytes: number, decimals = 1): string {
  if (!bytes) return '0 B';
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(dm))} ${sizes[i]}`;
}
