import type { Classification } from '../../api/chat';

export interface ChatModelOption { key: string; providerId: string; providerName: string; modelId: string; displayName: string }
export interface MessageRequest { id: string; prompt: string; conversationId: string; model?: { providerId: string; modelId: string; displayName: string } }
export interface PendingConfirmation { request: MessageRequest; classification: Classification; accepted: boolean }
