import { apiRequest } from './client';
import type { AvailableModelsResponse, ProviderTokenStatus, ProviderWithModels } from '../types/dominio';

export interface EmailVerificationStatus {
  verified: boolean;
  email: string;
  expiresInSeconds: number | null;
  resendInSeconds: number;
}

export function getEmailVerification() {
  return apiRequest<EmailVerificationStatus>('/technical-profile/email-verification');
}

export function requestEmailVerification() {
  return apiRequest<EmailVerificationStatus>('/technical-profile/email-verification/request', { method: 'POST' });
}

export function confirmEmailVerification(code: string) {
  return apiRequest<EmailVerificationStatus>('/technical-profile/email-verification/confirm', {
    method: 'POST',
    body: JSON.stringify({ code })
  });
}

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
