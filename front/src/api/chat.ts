import { apiRequest } from './client';

export interface Classification {
  label: 'no_personal' | 'personal_informativa' | 'personal_decision';
  group: string;
  confidence: number;
  status: 'aceptada' | 'baja_confianza' | 'revision_manual';
  needs_human_review: boolean;
}

export interface Conversation { id: string; title: string; createdAt: string; updatedAt: string }
export interface Message { id: string; role: 'user' | 'assistant'; content: string; createdAt: string; requestId: string; classification: Classification | null }
export interface ConversationDetail { conversation: Conversation; messages: Message[] }
export interface ChatStatus { ready: boolean; classifierReady: boolean; mode: 'classification'; model: string; maxInputCharacters: number; training: { examples: number | null; macroF1: number | null; decisionRecall: number | null } }

export const getChatStatus = (signal?: AbortSignal) => apiRequest<ChatStatus>('/api/chat/status', { signal });
export const listConversations = (signal?: AbortSignal) => apiRequest<{ conversations: Conversation[] }>('/api/chat/conversations', { signal });
export const createConversation = () => apiRequest<Conversation>('/api/chat/conversations', { method: 'POST' });
export const getConversation = (id: string, signal?: AbortSignal) => apiRequest<ConversationDetail>(`/api/chat/conversations/${id}`, { signal });
export const deleteConversation = (id: string) => apiRequest<void>(`/api/chat/conversations/${id}`, { method: 'DELETE' });
export const sendMessage = (id: string, prompt: string, requestId: string) => apiRequest<ConversationDetail>(`/api/chat/conversations/${id}/messages`, { method: 'POST', body: JSON.stringify({ prompt, requestId }) });
