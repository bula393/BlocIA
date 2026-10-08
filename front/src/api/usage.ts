import { apiRequest } from './client';
import type { UsageSummary } from '../types/dominio';
import type { UsageLock } from './chat';

export function getTodayUsage() {
  return apiRequest<UsageSummary>('/usage/today');
}

export interface UsageDashboard {
  limits: UsageLock;
  summary: {
    totalQueries: number;
    personalQueries: number;
    classifiedQueries: number;
    categoryCounts: Record<string, number>;
    providerCounts: Array<{ providerId: string; count: number }>;
    lastSevenDays: Array<{ date: string; count: number; personal: number }>;
  };
  activity: {
    items: Array<{
      prompt: string;
      createdAt: string;
      classification: { label: string; confidence?: number; status?: string; needs_human_review?: boolean } | null;
      providerId: string | null;
      modelId: string | null;
      durationSeconds: number;
      conversationId: string;
      conversationTitle: string;
    }>;
    total: number;
    offset: number;
    limit: number;
    hasMore: boolean;
  };
}

export function getUsageDashboard(limit = 40, offset = 0, signal?: AbortSignal) {
  return apiRequest<UsageDashboard>(`/usage/dashboard?limit=${limit}&offset=${offset}`, { signal });
}

export function getUsageLimits(signal?: AbortSignal) {
  return apiRequest<UsageLock>('/usage/limits', { signal, cache: 'no-store' });
}
