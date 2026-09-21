import { apiRequest } from './client';
import type { ProviderTokenStatus, ProviderWithModels } from '../types/dominio';

export function listTechnicalProviders() {
  return apiRequest<{ providers: ProviderWithModels[] }>('/technical-profile/providers');
}

export function saveProviderToken(providerId: string, token: string) {
  return apiRequest<ProviderTokenStatus>('/technical-profile/tokens', {
    method: 'POST',
    body: JSON.stringify({ providerId, token })
  });
}

export function removeProviderToken(providerId: string) {
  return apiRequest<void>(`/technical-profile/tokens/${providerId}`, { method: 'DELETE' });
}
