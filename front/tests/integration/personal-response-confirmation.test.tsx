import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { vi } from 'vitest';
import { createConversation, getChatStatus, getMessageProgress, listConversations, sendMessage, type ConversationDetail, type MessageResult, type PersonalResponseConfirmation, type UsageLock } from '../../src/api/chat';
import { getUsageLimits } from '../../src/api/usage';
import { listAvailableModels, listTechnicalProviders } from '../../src/api/technicalProfile';
import { NuevoChat } from '../../src/pages/NuevoChat';

vi.mock('../../src/api/chat', () => ({
  createConversation: vi.fn(), deleteConversation: vi.fn(), getChatStatus: vi.fn(), getConversation: vi.fn(), getMessageProgress: vi.fn(),
  listConversations: vi.fn(), sendMessage: vi.fn(),
}));
vi.mock('../../src/api/usage', () => ({ getTodayUsage: vi.fn(), getUsageLimits: vi.fn() }));
vi.mock('../../src/api/technicalProfile', () => ({ listAvailableModels: vi.fn(), listTechnicalProviders: vi.fn() }));

const conversation = { id: 'a43c8552-75c9-4a20-a149-b17bbd188aff', title: 'Ordenar mis ideas', createdAt: '2026-10-08T12:00:00Z', updatedAt: '2026-10-08T12:00:00Z' };
const prompt = '¿Qué factores debería considerar antes de cambiar de trabajo?';
const classification = { label: 'personal_informativa' as const, group: 'personal', confidence: .95, status: 'aceptada' as const, needs_human_review: false };
const initialUsage: UsageLock = { blocked: false, reasonCodes: [], lockUntil: null, usageSeconds: 0, usageLimitSeconds: 10800, personalQuestions: 0, personalQuestionLimit: 3, lockDurationMinutes: 15, personalQuestionsRemaining: 3 };

function preview(usageLock = initialUsage): PersonalResponseConfirmation {
  return { conversation, messages: [], confirmationRequired: true, classification, usageLock };
}

function answer(usageLock: UsageLock = { ...initialUsage, personalQuestions: 1, personalQuestionsRemaining: 2 }): ConversationDetail {
  return { conversation, usageLock, messages: [
    { id: 'question-1', role: 'user', content: prompt, createdAt: conversation.createdAt, requestId: 'request-1', classification: null },
    { id: 'answer-1', role: 'assistant', content: 'Considerá tus prioridades y las condiciones del trabajo.', createdAt: conversation.createdAt, requestId: 'request-1', classification, providerId: 'local', modelId: 'other-local' },
  ] };
}

function renderChat() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return { ...render(<QueryClientProvider client={client}><NuevoChat /></QueryClientProvider>), client };
}

async function submitPersonalPrompt() {
  const input = screen.getByLabelText('Mensaje para BloqIA');
  const modelPicker = screen.getByRole('combobox', { name: 'Modelo de respuesta' });
  await waitFor(() => expect(modelPicker).toBeEnabled());
  fireEvent.click(modelPicker);
  fireEvent.click(await screen.findByRole('option', { name: /Otro modelo local/ }));
  await act(async () => {
    fireEvent.change(input, { target: { value: prompt } });
    fireEvent.click(screen.getByRole('button', { name: 'Enviar mensaje' }));
  });
}

beforeEach(() => {
  vi.resetAllMocks();
  window.history.replaceState({}, '', '/nuevo-chat');
  Element.prototype.scrollIntoView = vi.fn();
  vi.mocked(getChatStatus).mockResolvedValue({
    ready: true, classifierReady: true, mode: 'classification', model: 'test-classifier', maxInputCharacters: 4000,
    usageLock: initialUsage, freeModels: [
      { providerId: 'local', providerName: 'En tu equipo', modelId: 'qwen3-local', displayName: 'Qwen local' },
      { providerId: 'local', providerName: 'En tu equipo', modelId: 'other-local', displayName: 'Otro modelo local' },
    ], training: { examples: 1000, macroF1: .9, decisionRecall: .9 },
  });
  vi.mocked(listConversations).mockResolvedValue({ conversations: [] });
  vi.mocked(createConversation).mockResolvedValue(conversation);
  vi.mocked(getMessageProgress).mockResolvedValue({ phase: 'classifying', state: 'completed' });
  vi.mocked(listTechnicalProviders).mockResolvedValue({ providers: [] });
  vi.mocked(listAvailableModels).mockReset();
  vi.mocked(getUsageLimits).mockResolvedValue(initialUsage);
});

test('prefers Groq gpt-oss-20b when available and filters the searchable model list', async () => {
  vi.mocked(listTechnicalProviders).mockResolvedValue({ providers: [{
    providerId: 'groq', name: 'Groq', status: 'available',
    tokenStatus: { providerId: 'groq', status: 'configured' }, models: [],
  }] });
  vi.mocked(listAvailableModels).mockResolvedValue({ providerId: 'groq', source: 'token', message: 'Listo', models: [
    { modelId: 'open/gpt-oss-20b', displayName: 'open/gpt-oss-20b', availabilityStatus: 'available', capabilities: ['chat'] },
    { modelId: 'llama-3.3-70b-versatile', displayName: 'Llama 3.3 70B', availabilityStatus: 'available', capabilities: ['chat'] },
  ] });

  renderChat();
  const modelPicker = await screen.findByRole('combobox', { name: 'Modelo de respuesta' });
  await waitFor(() => expect(modelPicker).toHaveTextContent('open/gpt-oss-20b'));
  expect(modelPicker).toHaveTextContent('Groq');

  fireEvent.click(modelPicker);
  fireEvent.change(screen.getByRole('searchbox', { name: 'Buscar un modelo' }), { target: { value: 'gpt-oss' } });
  expect(await screen.findByRole('option', { name: /open\/gpt-oss-20b/ })).toBeInTheDocument();
  expect(screen.queryByRole('option', { name: /Llama 3.3 70B/ })).not.toBeInTheDocument();
});

test('asks only after classification, then reuses the prompt, model and request identifier on acceptance', async () => {
  let resolveClassification!: (result: MessageResult) => void;
  let resolveAnswer!: (result: MessageResult) => void;
  vi.mocked(sendMessage).mockImplementationOnce(() => new Promise((resolve) => { resolveClassification = resolve; }))
    .mockImplementationOnce(() => new Promise((resolve) => { resolveAnswer = resolve; }));
  const { client, container } = renderChat();
  await submitPersonalPrompt();
  await waitFor(() => expect(sendMessage).toHaveBeenCalledTimes(1));
  expect(screen.queryByRole('button', { name: 'Usar 1 respuesta' })).not.toBeInTheDocument();
  expect(screen.getByText('Estamos clasificando tu consulta')).toBeInTheDocument();
  await act(async () => resolveClassification(preview()));
  expect(await screen.findByRole('heading', { name: '¿Querés usar 1 de tus 3 respuestas personales diarias?' })).toBeInTheDocument();
  const composer = container.querySelector('.chat-composer');
  expect(screen.getByRole('heading', { name: '¿Querés usar 1 de tus 3 respuestas personales diarias?' }).closest('form')).toBe(composer);
  expect(screen.getByLabelText('Cupo de respuestas personales').parentElement).toBe(composer);
  expect(composer?.lastElementChild).toBe(screen.getByLabelText('Cupo de respuestas personales'));
  expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '0');
  expect(screen.getByLabelText('Mensaje para BloqIA')).toBeDisabled();
  expect(screen.getByRole('combobox', { name: 'Modelo de respuesta' })).toBeDisabled();
  screen.getAllByRole('button', { name: 'Nuevo chat', exact: true }).forEach((button) => expect(button).toBeDisabled());
  expect(screen.queryByRole('article', { name: 'Respuesta de BloqIA' })).not.toBeInTheDocument();
  fireEvent.click(screen.getByRole('button', { name: 'Usar 1 respuesta' }));
  await waitFor(() => expect(sendMessage).toHaveBeenCalledTimes(2));
  const firstCall = vi.mocked(sendMessage).mock.calls[0];
  expect(firstCall).toEqual([conversation.id, prompt, expect.any(String), { providerId: 'local', modelId: 'other-local' }, false]);
  expect(vi.mocked(sendMessage).mock.calls[1]).toEqual([...firstCall.slice(0, 4), true]);
  expect(screen.getByText('Consulta clasificada; esperando la respuesta del modelo')).toBeInTheDocument();
  expect(screen.queryByText('Estamos clasificando tu consulta')).not.toBeInTheDocument();
  await act(async () => resolveAnswer(answer()));
  expect(await screen.findByRole('article', { name: 'Respuesta de BloqIA' })).toHaveTextContent('Considerá tus prioridades');
  expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '1');
  expect(client.getQueryData<UsageLock>(['usage-lock'])?.personalQuestionsRemaining).toBe(2);
  expect(screen.getByLabelText('Mensaje para BloqIA')).toBeEnabled();
});

test('cancelling restores the editable prompt without sending acceptance or consuming a response', async () => {
  vi.mocked(sendMessage).mockResolvedValue(preview());
  renderChat();
  await submitPersonalPrompt();
  fireEvent.click(await screen.findByRole('button', { name: 'Cancelar' }));
  expect(sendMessage).toHaveBeenCalledTimes(1);
  expect(screen.getByLabelText('Mensaje para BloqIA')).toBeEnabled();
  expect(screen.getByLabelText('Mensaje para BloqIA')).toHaveValue(prompt);
  expect(screen.getByLabelText('Mensaje para BloqIA')).not.toHaveAttribute('hidden');
  expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '0');
  expect(screen.queryByRole('article', { name: 'Tu consulta pendiente' })).not.toBeInTheDocument();
  expect(screen.queryByRole('article', { name: 'Respuesta de BloqIA' })).not.toBeInTheDocument();
});

test('keeps acceptance and the same request when retrying a failed response after the last allowance was consumed', async () => {
  const twoUsed = { ...initialUsage, personalQuestions: 2, personalQuestionsRemaining: 1 };
  const thirdUsed: UsageLock = { ...twoUsed, blocked: true, personalQuestions: 3, personalQuestionsRemaining: 0, reasonCodes: ['personal_questions'] };
  vi.mocked(getUsageLimits).mockResolvedValue(twoUsed);
  vi.mocked(sendMessage).mockResolvedValueOnce(preview(twoUsed)).mockRejectedValueOnce(new Error('No se pudo contactar al modelo.')).mockResolvedValueOnce(answer(thirdUsed));
  const { client } = renderChat();
  await submitPersonalPrompt();
  fireEvent.click(await screen.findByRole('button', { name: 'Usar 1 respuesta' }));
  expect(await screen.findByRole('alert')).toHaveTextContent('No se pudo contactar al modelo.');
  expect(screen.getByLabelText('Mensaje para BloqIA')).toBeDisabled();
  await act(async () => { client.setQueryData(['usage-lock'], thirdUsed); });
  expect(screen.getByRole('button', { name: 'Reintentar respuesta' })).toBeEnabled();
  fireEvent.click(screen.getByRole('button', { name: 'Reintentar respuesta' }));
  expect(await screen.findByRole('article', { name: 'Respuesta de BloqIA' })).toBeInTheDocument();
  expect(sendMessage).toHaveBeenCalledTimes(3);
  expect(vi.mocked(sendMessage).mock.calls[2]).toEqual(vi.mocked(sendMessage).mock.calls[1]);
  expect(vi.mocked(sendMessage).mock.calls[2][4]).toBe(true);
  expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '3');
});

test('fills the bar and applies the configurable lock immediately after the third response', async () => {
  const twoUsed = { ...initialUsage, personalQuestions: 2, personalQuestionsRemaining: 1 };
  const thirdUsed: UsageLock = { ...twoUsed, blocked: true, personalQuestions: 3, personalQuestionsRemaining: 0, reasonCodes: ['personal_questions'], lockDurationMinutes: 15 };
  vi.mocked(getUsageLimits).mockResolvedValue(twoUsed);
  vi.mocked(sendMessage).mockResolvedValueOnce(preview(twoUsed)).mockResolvedValueOnce(answer(thirdUsed));
  const { container } = renderChat();
  await submitPersonalPrompt();
  fireEvent.click(await screen.findByRole('button', { name: 'Usar 1 respuesta' }));
  expect(await screen.findByRole('heading', { name: 'Bloqueo activo' })).toBeInTheDocument();
  expect(screen.getByText('Pausa de seguridad · 15 minutos')).toBeInTheDocument();
  expect(screen.getByText('Dentro de 15 minutos')).toBeInTheDocument();
  expect(screen.getByLabelText('Cupo de respuestas personales')).toHaveTextContent('Te quedan 0 de 3 respuestas personales.');
  expect(screen.getByRole('progressbar')).toHaveAttribute('aria-valuenow', '3');
  expect(container.querySelector('.chat-quota-track > span')).toHaveStyle({ transform: 'scaleX(1)' });
  expect(screen.getByLabelText('Mensaje para BloqIA')).toBeDisabled();
  expect(screen.queryByRole('button', { name: 'Enviar mensaje' })).not.toBeInTheDocument();
});

test('general responses appear directly and old usage responses retain the quota fallback', async () => {
  const { personalQuestionsRemaining: _remaining, lockDurationMinutes: _duration, ...legacyUsage } = initialUsage;
  vi.mocked(getUsageLimits).mockResolvedValue({ ...legacyUsage, personalQuestions: 1 });
  vi.mocked(sendMessage).mockResolvedValue({ ...answer({ ...legacyUsage, personalQuestions: 1 }), messages: answer().messages.map((message) => ({ ...message, classification: message.role === 'assistant' ? { ...classification, label: 'no_personal' } : null })) });
  renderChat();
  await submitPersonalPrompt();
  expect(await screen.findByRole('article', { name: 'Respuesta de BloqIA' })).toBeInTheDocument();
  expect(sendMessage).toHaveBeenCalledTimes(1);
  expect(screen.queryByRole('button', { name: 'Usar 1 respuesta' })).not.toBeInTheDocument();
  expect(screen.getByLabelText('Cupo de respuestas personales')).toHaveTextContent('Te quedan 2 de 3 respuestas personales.');
});

test('refreshes the allowance when the lock expiration arrives', async () => {
  const expiringLock: UsageLock = { ...initialUsage, blocked: true, reasonCodes: ['usage_time'], lockUntil: new Date(Date.now() + 500).toISOString(), lockDurationMinutes: 1 };
  vi.mocked(getUsageLimits).mockResolvedValueOnce(expiringLock).mockResolvedValue(initialUsage);
  renderChat();
  expect(await screen.findByRole('heading', { name: 'Bloqueo activo' })).toBeInTheDocument();
  expect(screen.getByText('Pausa de seguridad · 1 minuto')).toBeInTheDocument();
  await waitFor(() => expect(screen.getByLabelText('Mensaje para BloqIA')).toBeEnabled(), { timeout: 2000 });
  expect(getUsageLimits).toHaveBeenCalledTimes(2);
  expect(screen.queryByRole('heading', { name: 'Bloqueo activo' })).not.toBeInTheDocument();
});
