import { act, renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import type { FormEvent, ReactNode } from 'react';
import { vi } from 'vitest';
import { createConversation, getChatStatus, getConversation, getMessageProgress, listConversations, sendMessage } from '../../src/api/chat';
import { setAccessToken } from '../../src/api/client';
import { listAvailableModels, listTechnicalProviders } from '../../src/api/technicalProfile';
import { getUsageLimits } from '../../src/api/usage';
import { createSessionJwt } from '../../src/app/routeGuard';
import { useChatController } from '../../src/features/chat/useChatController';
import type { AvailableModelsResponse } from '../../src/types/dominio';

vi.mock('../../src/api/chat', () => ({
  createConversation: vi.fn(), deleteConversation: vi.fn(), getChatStatus: vi.fn(), getConversation: vi.fn(), getMessageProgress: vi.fn(),
  listConversations: vi.fn(), sendMessage: vi.fn(),
}));
vi.mock('../../src/api/usage', () => ({ getUsageLimits: vi.fn() }));
vi.mock('../../src/api/technicalProfile', () => ({ listAvailableModels: vi.fn(), listTechnicalProviders: vi.fn() }));

const usageLock = { blocked: false, reasonCodes: [], lockUntil: null, usageSeconds: 0, usageLimitSeconds: 10800, personalQuestions: 0, personalQuestionLimit: 3 };
const conversation = { id: 'a43c8552-75c9-4a20-a149-b17bbd188aff', title: 'Consulta', createdAt: '2026-10-09T12:00:00Z', updatedAt: '2026-10-09T12:00:00Z' };
const groqCatalog: AvailableModelsResponse = { providerId: 'groq', source: 'default', message: 'Listo', models: [
  { modelId: 'openai/gpt-oss-20b', displayName: 'openai/gpt-oss-20b', availabilityStatus: 'available', capabilities: ['chat'] },
] };
const googleCatalog: AvailableModelsResponse = { providerId: 'google', source: 'default', message: 'Listo', models: [
  { modelId: 'gemini-flash', displayName: 'Gemini Flash', availabilityStatus: 'available', capabilities: ['chat'] },
] };

function renderController(client = new QueryClient({ defaultOptions: { queries: { retry: false } } })) {
  function wrapper({ children }: { children: ReactNode }) {
    return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
  }
  return { ...renderHook(useChatController, { wrapper }), client };
}

beforeEach(() => {
  vi.resetAllMocks();
  window.sessionStorage.clear();
  setAccessToken(createSessionJwt('one@example.com'));
  window.history.replaceState({}, '', '/nuevo-chat');
  vi.mocked(getChatStatus).mockResolvedValue({
    ready: true, classifierReady: true, mode: 'classification', model: 'test-classifier', maxInputCharacters: 4000,
    usageLock, freeModels: [], training: { examples: 1000, macroF1: .9, decisionRecall: .9 },
  });
  vi.mocked(listConversations).mockResolvedValue({ conversations: [] });
  vi.mocked(createConversation).mockResolvedValue(conversation);
  vi.mocked(getConversation).mockResolvedValue({ conversation, messages: [], usageLock });
  vi.mocked(getMessageProgress).mockResolvedValue({ phase: 'classifying', state: 'completed' });
  vi.mocked(getUsageLimits).mockResolvedValue(usageLock);
  vi.mocked(sendMessage).mockResolvedValue({ conversation, messages: [], usageLock });
  vi.mocked(listTechnicalProviders).mockResolvedValue({ providers: ['google', 'groq'].map((providerId) => ({
    providerId, name: providerId, status: 'available', models: [], defaultTokenAvailable: true,
    tokenStatus: { providerId, status: 'not-configured' },
  })) });
  vi.mocked(listAvailableModels).mockImplementation(async (provider) => provider === 'groq' ? groqCatalog : googleCatalog);
});

afterEach(() => setAccessToken(null));

test('keeps Groq as the default while its catalog loads and sends its official model ID', async () => {
  let resolveGroq!: (catalog: AvailableModelsResponse) => void;
  vi.mocked(listAvailableModels).mockImplementation((provider) => provider === 'groq'
    ? new Promise((resolve) => { resolveGroq = resolve; })
    : Promise.resolve(googleCatalog));
  const { result } = renderController();
  await waitFor(() => expect(result.current.modelOptions).toHaveLength(1));
  expect(result.current.selectedModel).toBe('groq:openai/gpt-oss-20b');
  expect(result.current.selectedModelAvailable).toBe(false);
  await act(async () => resolveGroq(groqCatalog));
  await waitFor(() => expect(result.current.selectedModelAvailable).toBe(true));
  act(() => result.current.setDraft('Explicá la fotosíntesis'));
  await act(async () => result.current.submit({ preventDefault: vi.fn() } as unknown as FormEvent));
  expect(sendMessage).toHaveBeenCalledWith(conversation.id, 'Explicá la fotosíntesis', expect.any(String), { providerId: 'groq', modelId: 'openai/gpt-oss-20b' }, false);
});

test('never falls back to Gemini or sends without an explicit model when the Groq catalog fails', async () => {
  vi.mocked(listAvailableModels).mockImplementation(async (provider) => {
    if (provider === 'groq') throw new Error('Groq no responde');
    return googleCatalog;
  });
  const { result } = renderController();
  await waitFor(() => expect(result.current.modelsLoading).toBe(false));
  expect(result.current.selectedModel).toBe('groq:openai/gpt-oss-20b');
  expect(result.current.selectedModelAvailable).toBe(false);
  expect(result.current.modelSelectionMessage).toContain('es tu modelo predeterminado, pero no está disponible');
  act(() => result.current.setDraft('Explicá la fotosíntesis'));
  await act(async () => result.current.submit({ preventDefault: vi.fn() } as unknown as FormEvent));
  expect(createConversation).not.toHaveBeenCalled();
  expect(sendMessage).not.toHaveBeenCalled();
});

test('retains an explicit choice through catalog changes and page remounts without sharing it with another account', async () => {
  const first = renderController();
  await waitFor(() => expect(first.result.current.modelsLoading).toBe(false));
  act(() => first.result.current.selectModel('google:gemini-flash'));
  expect(first.result.current.selectedModel).toBe('google:gemini-flash');
  act(() => { first.client.setQueryData(['chat-models', 'google'], { ...googleCatalog, models: [] }); });
  expect(first.result.current.selectedModel).toBe('google:gemini-flash');
  await waitFor(() => expect(first.result.current.selectedModelAvailable).toBe(false));
  act(() => { first.client.setQueryData(['chat-models', 'google'], googleCatalog); });
  await waitFor(() => expect(first.result.current.selectedModelAvailable).toBe(true));
  first.unmount();

  const restored = renderController();
  await waitFor(() => expect(restored.result.current.modelsLoading).toBe(false));
  expect(restored.result.current.selectedModel).toBe('google:gemini-flash');
  restored.unmount();

  setAccessToken(createSessionJwt('two@example.com'));
  const otherAccount = renderController();
  await waitFor(() => expect(otherAccount.result.current.modelsLoading).toBe(false));
  expect(otherAccount.result.current.selectedModel).toBe('groq:openai/gpt-oss-20b');
});
