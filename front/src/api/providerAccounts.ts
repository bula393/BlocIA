import { apiRequest } from './client';
import type { GoogleConnectionStatus } from '../types/dominio';

export interface GoogleProject { projectId: string; name: string }

export const getGoogleConnection = () => apiRequest<GoogleConnectionStatus>('/technical-profile/google');
export const startGoogleConnection = () => apiRequest<{ authorizationUrl: string }>('/technical-profile/google/start', { method: 'POST' });
export const getGoogleProjects = () => apiRequest<{ projects: GoogleProject[] }>('/technical-profile/google/projects');
export const selectGoogleProject = (projectId: string) => apiRequest<GoogleConnectionStatus>('/technical-profile/google/project', { method: 'POST', body: JSON.stringify({ projectId }) });
export const disconnectGoogle = () => apiRequest<{ disconnected: boolean; revoked: boolean }>('/technical-profile/google', { method: 'DELETE' });
