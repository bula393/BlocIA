import { getAccessToken } from '../../api/client';
import type { ChatModelOption } from './types';

export const DEFAULT_CHAT_MODEL: ChatModelOption = {
  key: 'groq:openai/gpt-oss-20b',
  providerId: 'groq',
  providerName: 'Groq',
  modelId: 'openai/gpt-oss-20b',
  displayName: 'GPT-OSS 20B',
};

export function isDefaultChatModel(model: ChatModelOption) {
  return model.providerId === 'groq' && ['openai/gpt-oss-20b', 'open/gpt-oss-20b'].includes(model.modelId);
}

function preferenceKey() {
  const payload = getAccessToken()?.split('.')[1];
  if (!payload) return null;
  try {
    const base64 = payload.replace(/-/g, '+').replace(/_/g, '/').padEnd(Math.ceil(payload.length / 4) * 4, '=');
    const { sub } = JSON.parse(atob(base64)) as { sub?: unknown };
    // The subject only scopes this display preference; authorization stays on the server.
    return typeof sub === 'string' && sub ? `bloqia.chat-model.v1:${encodeURIComponent(sub)}` : null;
  } catch {
    return null;
  }
}

export function readModelPreference(): ChatModelOption | null {
  try {
    const key = preferenceKey();
    const stored = key ? window.sessionStorage.getItem(key) : null;
    if (!stored) return null;
    const model = JSON.parse(stored) as Partial<ChatModelOption>;
    if (['key', 'providerId', 'providerName', 'modelId', 'displayName'].some((field) => typeof model[field as keyof ChatModelOption] !== 'string')) return null;
    return model.key === `${model.providerId}:${model.modelId}` ? model as ChatModelOption : null;
  } catch {
    return null;
  }
}

export function saveModelPreference(model: ChatModelOption) {
  try {
    const key = preferenceKey();
    if (key) window.sessionStorage.setItem(key, JSON.stringify(model));
  } catch {
    // Model selection still works when browser storage is unavailable.
  }
}
