import { apiRequest } from './client';
import type { UserProfile } from '../types/dominio';

export function getProfile() {
  return apiRequest<UserProfile>('/profile');
}

export function updateProfile(data: { age?: number; profession?: string; displayName?: string }) {
  return apiRequest<UserProfile>('/profile', {
    method: 'PATCH',
    body: JSON.stringify(data)
  });
}
