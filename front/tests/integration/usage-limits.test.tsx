import { render, screen } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { vi } from 'vitest';
import { getChatStatus, listConversations } from '../../src/api/chat';
import { getUsageDashboard, getUsageLimits } from '../../src/api/usage';
import { listTechnicalProviders } from '../../src/api/technicalProfile';
import { NuevoChat } from '../../src/pages/NuevoChat';
import { Actividad } from '../../src/pages/Actividad';

vi.mock('../../src/api/chat', () => ({
  createConversation: vi.fn(), deleteConversation: vi.fn(), getChatStatus: vi.fn(), getConversation: vi.fn(), getMessageProgress: vi.fn(),
  listConversations: vi.fn(), sendMessage: vi.fn()
}));
vi.mock('../../src/api/usage', () => ({ getTodayUsage: vi.fn(), getUsageDashboard: vi.fn(), getUsageLimits: vi.fn() }));
vi.mock('../../src/api/technicalProfile', () => ({ listAvailableModels: vi.fn(), listTechnicalProviders: vi.fn() }));

const lockedUsage = { blocked: true, reasonCodes: ['usage_time'] as const, lockUntil: '2026-10-08T15:00:00+00:00', usageSeconds: 10800, usageLimitSeconds: 10800, personalQuestions: 1, personalQuestionLimit: 3 };
const dashboardFixture = {
  limits: { ...lockedUsage },
  summary: {
    totalQueries: 1, personalQueries: 1, classifiedQueries: 1,
    categoryCounts: { personal_informativa: 1 },
    providerCounts: [{ providerId: 'google', count: 1 }],
    lastSevenDays: [{ date: '2026-10-07', count: 1, personal: 1 }],
  },
  activity: {
    items: [{ prompt: 'Consulta demo', createdAt: '2026-10-07T12:00:00+00:00', classification: { label: 'personal_informativa', confidence: 0.94, needs_human_review: true }, providerId: 'google', modelId: 'gemini-flash', durationSeconds: 75, conversationId: 'conversation-1', conversationTitle: 'Consulta demo' }],
    total: 1, offset: 0, limit: 40, hasMore: false,
  },
};

function renderInApp(node: React.ReactNode) {
  return render(<QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>{node}</QueryClientProvider>);
}

beforeEach(() => {
  vi.mocked(getChatStatus).mockResolvedValue({
    ready: true, classifierReady: true, mode: 'classification', model: 'test-classifier', maxInputCharacters: 4000,
    usageLock: lockedUsage, freeModels: [{ providerId: 'local', providerName: 'En tu equipo', modelId: 'qwen3-local', displayName: 'Qwen local' }],
    training: { examples: 1000, macroF1: 0.9, decisionRecall: 0.9 },
  });
  vi.mocked(listConversations).mockResolvedValue({ conversations: [] });
  vi.mocked(listTechnicalProviders).mockResolvedValue({ providers: [] });
  vi.mocked(getUsageLimits).mockResolvedValue(lockedUsage);
  vi.mocked(getUsageDashboard).mockResolvedValue(dashboardFixture);
});

test('disables chat sending and explains the three-hour lock in the composer', async () => {
  const { container } = renderInApp(<NuevoChat />);
  expect(await screen.findByRole('heading', { name: 'Bloqueo activo' })).toBeInTheDocument();
  expect(screen.getByText('Alcanzaste el límite de 3 horas de uso de IA.')).toBeInTheDocument();
  expect(screen.getByLabelText('Mensaje para BloqIA')).toBeDisabled();
  expect(screen.queryByRole('button', { name: 'Envío bloqueado por límite de uso' })).not.toBeInTheDocument();
  const lockPanel = container.querySelector('.chat-lock-panel');
  expect(lockPanel?.parentElement).toHaveClass('chat-composer');
  expect(lockPanel?.children[1]).toHaveClass('chat-lock-icon');
  expect(screen.getByLabelText('Chat bloqueado')).toBeInTheDocument();
  expect(container.querySelector('.chat-welcome')).not.toBeInTheDocument();
  expect(screen.getByLabelText('Mensaje para BloqIA')).toHaveAttribute('placeholder', '');
  expect(container.querySelector('.chat-model-picker')).not.toBeInTheDocument();
  expect(container.querySelector('.chat-composer-bottom')).not.toBeInTheDocument();
});

test('shows the reason when three personal questions trigger the lock', async () => {
  const personalLock = { ...lockedUsage, reasonCodes: ['personal_questions'] as const, personalQuestions: 3 };
  vi.mocked(getChatStatus).mockResolvedValue({
    ready: true, classifierReady: true, mode: 'classification', model: 'test-classifier', maxInputCharacters: 4000,
    usageLock: personalLock, freeModels: [], training: { examples: 1000, macroF1: 0.9, decisionRecall: 0.9 },
  });
  vi.mocked(getUsageLimits).mockResolvedValue(personalLock);
  renderInApp(<NuevoChat />);
  expect(await screen.findByText('Alcanzaste el límite de 3 consultas personales durante las últimas 24 horas.')).toBeInTheDocument();
  expect(screen.queryByRole('button', { name: 'Envío bloqueado por límite de uso' })).not.toBeInTheDocument();
});

test('shows the category dashboard and full query details', async () => {
  renderInApp(<Actividad />);
  expect(await screen.findByRole('heading', { name: 'Actividad y límites' })).toBeInTheDocument();
  expect((await screen.findAllByText('Análisis personales')).length).toBeGreaterThan(0);
  expect(await screen.findAllByText('Consulta demo')).toHaveLength(2);
  expect(screen.getAllByText('Google AI').length).toBeGreaterThan(0);
  expect(screen.getByText('Revisión')).toBeInTheDocument();
});
