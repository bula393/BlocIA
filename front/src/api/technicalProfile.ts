import { apiRequest } from './client';
import type { AvailableModelsResponse, ProviderTokenStatus, ProviderWithModels } from '../types/dominio';

export function listTechnicalProviders() {
  return apiRequest<{ providers: ProviderWithModels[] }>('/technical-profile/providers');
}

export function listAvailableModels(providerId: string) {
  return apiRequest<AvailableModelsResponse>(`/technical-profile/providers/${providerId}/models`);
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
