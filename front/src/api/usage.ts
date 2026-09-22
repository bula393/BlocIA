import { apiRequest } from './client';
import type { UsageSummary } from '../types/dominio';

export function getTodayUsage() {
  return apiRequest<UsageSummary>('/usage/today');
}
