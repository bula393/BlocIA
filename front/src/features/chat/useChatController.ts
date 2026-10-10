import { useEffect, useRef, useState, type FormEvent } from 'react';
import { useQueries, useQuery, useQueryClient } from '@tanstack/react-query';
import { createConversation, deleteConversation, getChatStatus, getConversation, getMessageProgress, listConversations, sendMessage, type ChatStatus, type Classification, type Conversation, type Message, type UsageLock } from '../../api/chat';
import { getUsageLimits } from '../../api/usage';
import { listAvailableModels, listTechnicalProviders } from '../../api/technicalProfile';

import { providerLabel } from './helpers';
import { DEFAULT_CHAT_MODEL, isDefaultChatModel, readModelPreference, saveModelPreference } from './modelPreference';
import type { ChatModelOption, MessageRequest, PendingConfirmation } from './types';

export function useChatController() {
  const initialId = new URLSearchParams(window.location.search).get('chat');
  const [activeId, setActiveId] = useState<string | null>(initialId && /^[a-f\d-]{36}$/i.test(initialId) ? initialId : null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [status, setStatus] = useState<ChatStatus | null>(null);
  const [draft, setDraft] = useState('');
  const [pendingPrompt, setPendingPrompt] = useState('');
  const [confirmation, setConfirmation] = useState<PendingConfirmation | null>(null);
  const [sendPhase, setSendPhase] = useState<'classifying' | 'waiting_model'>('classifying');
  const [sending, setSending] = useState(false);
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [historyOpen, setHistoryOpen] = useState(() => new URLSearchParams(window.location.search).has('history'));
  const [error, setError] = useState('');
  const [historyError, setHistoryError] = useState('');
  const [deleting, setDeleting] = useState<string | null>(null);
  const [modelPreference, setModelPreference] = useState<ChatModelOption | null>(readModelPreference);
  const inFlight = useRef(false);
  const failedRequest = useRef<MessageRequest | null>(null);
  const end = useRef<HTMLDivElement>(null);
  const textarea = useRef<HTMLTextAreaElement>(null);
  const confirmButton = useRef<HTMLButtonElement>(null);
  const queryClient = useQueryClient();
  const limit = status?.maxInputCharacters ?? 4000;
  const providerQuery = useQuery({ queryKey: ['chat-providers'], queryFn: listTechnicalProviders });
  const usageLockQuery = useQuery({ queryKey: ['usage-lock'], queryFn: ({ signal }) => getUsageLimits(signal), refetchInterval: 30_000, retry: false });
  const usageLock = usageLockQuery.data ?? status?.usageLock;
  const personalLimit = Math.max(1, usageLock?.personalQuestionLimit ?? 3);
  const personalRemaining = Math.max(0, Math.min(personalLimit, usageLock?.personalQuestionsRemaining ?? personalLimit - (usageLock?.personalQuestions ?? 0)));
  const personalUsed = personalLimit - personalRemaining;
  const lockDurationMinutes = usageLock?.lockDurationMinutes ?? 1440;
  const lockDuration = lockDurationMinutes % 60 === 0 ? `${lockDurationMinutes / 60} ${lockDurationMinutes === 60 ? 'hora' : 'horas'}` : `${lockDurationMinutes} ${lockDurationMinutes === 1 ? 'minuto' : 'minutos'}`;
  const interactionPending = sending || confirmation !== null;
  const blockedReasons: Record<string, string> = {
    usage_time: `Alcanzaste el límite de ${(usageLock?.usageLimitSeconds ?? 10800) / 3600} horas de uso de IA.`,
    personal_questions: `Alcanzaste el límite de ${personalLimit} consultas personales durante las últimas 24 horas.`
  };
  const configuredProviders = (providerQuery.data?.providers ?? []).filter((provider) => provider.status === 'available' && (provider.tokenStatus.status === 'configured' || provider.defaultTokenAvailable));
  const modelCatalogQueries = useQueries({
    queries: configuredProviders.map((provider) => ({
      queryKey: ['chat-models', provider.providerId],
      queryFn: () => listAvailableModels(provider.providerId),
      retry: false
    }))
  });
  const modelCatalogQueryByProvider = new Map(configuredProviders.map((provider, index) => [provider.providerId, modelCatalogQueries[index]]));
  const configuredModelOptions: ChatModelOption[] = configuredProviders.flatMap((provider) => {
      const catalog = modelCatalogQueryByProvider.get(provider.providerId)?.data;
      if (!catalog || !['token', 'default'].includes(catalog.source)) return [];
      return catalog.models.filter((model) => model.availabilityStatus === 'available').map((model) => ({ key: `${provider.providerId}:${model.modelId}`, providerId: provider.providerId, providerName: providerLabel(provider.providerId, provider.name), modelId: model.modelId, displayName: model.displayName }));
    });
  const modelOptions: ChatModelOption[] = [
    ...configuredModelOptions,
    ...(status?.freeModels ?? []).map((model) => ({ ...model, key: `${model.providerId}:${model.modelId}`, providerName: providerLabel(model.providerId, model.providerName) }))
  ];
  const selectedModelOption = modelPreference
    ? modelOptions.find((model) => model.key === modelPreference.key || (isDefaultChatModel(modelPreference) && isDefaultChatModel(model)))
    : modelOptions.find((model) => model.key === DEFAULT_CHAT_MODEL.key) ?? modelOptions.find(isDefaultChatModel);
  const selectedModelDisplay = selectedModelOption ?? modelPreference ?? DEFAULT_CHAT_MODEL;
  const selectedModel = selectedModelDisplay.key;
  const selectedModelAvailable = Boolean(selectedModelOption);
  const modelsLoading = !status || providerQuery.isLoading || modelCatalogQueries.some((query) => query.isLoading);
  const modelSelectionMessage = !modelsLoading && !selectedModelAvailable
    ? `${selectedModelDisplay.displayName} de ${selectedModelDisplay.providerName} ${modelPreference ? 'no está disponible' : 'es tu modelo predeterminado, pero no está disponible'}. Revisá la conexión del proveedor o elegí otro modelo para responder.`
    : '';
  const providerTokenAvailable = configuredProviders.length > 0;
  const failedCatalogs = configuredProviders.flatMap((provider, index) => {
    const query = modelCatalogQueries[index];
    if (!query?.isError) return [];
    const reason = query.error instanceof Error ? query.error.message : 'No se pudo consultar el catálogo.';
    return [`${provider.name}: ${reason}`];
  });

  useEffect(() => {
    if (!usageLock?.blocked || !usageLock.lockUntil) return;
    const unlockAt = Date.parse(usageLock.lockUntil);
    if (!Number.isFinite(unlockAt)) return;
    const timer = window.setTimeout(() => void usageLockQuery.refetch(), Math.min(2_147_483_647, Math.max(0, unlockAt - Date.now()) + 100));
    return () => window.clearTimeout(timer);
  }, [usageLock?.blocked, usageLock?.lockUntil, usageLockQuery.refetch]);

  useEffect(() => {
    if (confirmation && !sending) confirmButton.current?.focus();
  }, [confirmation, sending]);

  useEffect(() => {
    const controller = new AbortController();
    getChatStatus(controller.signal).then(setStatus).catch((failure: Error) => { if (!controller.signal.aborted) setError(failure.message); });
    listConversations(controller.signal).then((result) => setConversations(result.conversations))
      .catch((failure: Error) => { if (!controller.signal.aborted) setHistoryError(failure.message); })
      .finally(() => { if (!controller.signal.aborted) setHistoryLoading(false); });
    return () => controller.abort();
  }, []);

  useEffect(() => {
    const params = new URLSearchParams();
    if (activeId) params.set('chat', activeId);
    if (historyOpen) params.set('history', '1');
    window.history.replaceState({}, '', `/nuevo-chat${params.size ? `?${params}` : ''}`);
  }, [activeId, historyOpen]);

  useEffect(() => {
    if (!activeId || inFlight.current) return;
    const controller = new AbortController();
    setLoading(true);
    setMessages([]);
    setError('');
    getConversation(activeId, controller.signal).then((result) => setMessages(result.messages))
      .catch((failure: Error) => { if (!controller.signal.aborted) setError(failure.message); })
      .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [activeId]);

  useEffect(() => {
    if (messages.length > 0 || interactionPending) end.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [messages, interactionPending]);
  useEffect(() => {
    if (textarea.current) {
      textarea.current.style.height = 'auto';
      textarea.current.style.height = `${Math.min(textarea.current.scrollHeight, 160)}px`;
    }
  }, [draft]);

  function selectConversation(id: string | null) {
    if (inFlight.current || confirmation) return;
    if (id !== null && id === activeId) {
      setHistoryOpen(false);
      return;
    }
    setActiveId(id);
    setMessages([]);
    setDraft('');
    setError('');
    setLoading(false);
    setHistoryOpen(false);
    failedRequest.current = null;
    textarea.current?.focus();
  }

  async function updateUsageLock(next?: UsageLock) {
    if (!next) {
      void usageLockQuery.refetch();
      return;
    }
    await queryClient.cancelQueries({ queryKey: ['usage-lock'] });
    queryClient.setQueryData(['usage-lock'], next);
  }

  async function performSend(request: MessageRequest, accepted = false) {
    const progressController = new AbortController();
    const progressWatcher = (async () => {
      while (!progressController.signal.aborted) {
        try {
          const progress = await getMessageProgress(request.conversationId, request.id, progressController.signal);
          if (progressController.signal.aborted) return;
          if (progress.phase === 'generating') {
            setSendPhase('waiting_model');
            return;
          }
          if (progress.state === 'completed') return;
        } catch {
          if (progressController.signal.aborted) return;
          // The first polls can arrive before the message has been reserved.
        }
        await new Promise((resolve) => window.setTimeout(resolve, 300));
      }
    })();
    try {
      const model = request.model ? { providerId: request.model.providerId, modelId: request.model.modelId } : undefined;
      const result = await sendMessage(request.conversationId, request.prompt, request.id, model, accepted);
      await updateUsageLock(result.usageLock);
      setMessages(result.messages);
      setConversations((previous) => [result.conversation, ...previous.filter((item) => item.id !== result.conversation.id)]);
      if (result.confirmationRequired) {
        setConfirmation({ request, classification: result.classification, accepted: false });
      } else {
        setConfirmation(null);
        setPendingPrompt('');
        failedRequest.current = null;
      }
    } finally {
      progressController.abort();
      // Showing the answer must not wait for the polling timer to finish.
      void progressWatcher;
    }
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    const prompt = draft.trim();
    if (!prompt || inFlight.current || confirmation || !status?.ready || loading || modelsLoading || !selectedModelOption || usageLock?.blocked) return;
    inFlight.current = true;
    setSending(true);
    setSendPhase('classifying');
    setPendingPrompt(prompt);
    setDraft('');
    setError('');
    let conversationId = activeId;
    try {
      if (!conversationId) {
        const created = await createConversation();
        conversationId = created.id;
        setConversations((previous) => [created, ...previous]);
        setActiveId(created.id);
      }
      const previous = failedRequest.current;
      const currentModel = { providerId: selectedModelOption.providerId, modelId: selectedModelOption.modelId, displayName: selectedModelOption.displayName };
      const request = previous?.prompt === prompt && previous.conversationId === conversationId && previous.model?.providerId === currentModel?.providerId && previous.model?.modelId === currentModel?.modelId
        ? previous
        : { id: crypto.randomUUID(), prompt, conversationId, model: currentModel };
      failedRequest.current = request;
      await performSend(request);
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : 'No se pudo enviar el mensaje.');
      setDraft(prompt);
      setPendingPrompt('');
      if (failure instanceof Error && 'status' in failure && failure.status === 423) void usageLockQuery.refetch();
    } finally {
      inFlight.current = false;
      setSending(false);
      setSendPhase('classifying');
      window.setTimeout(() => textarea.current?.focus(), 0);
    }
  }

  async function confirmPersonalResponse() {
    if (!confirmation || inFlight.current || (usageLock?.blocked && !confirmation.accepted)) return;
    inFlight.current = true;
    setConfirmation({ ...confirmation, accepted: true });
    setSending(true);
    setSendPhase('waiting_model');
    setError('');
    try {
      await performSend(confirmation.request, true);
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : 'No se pudo preparar la respuesta. Reintentá con el mismo botón.');
      if (failure instanceof Error && 'status' in failure && failure.status === 423) void usageLockQuery.refetch();
    } finally {
      inFlight.current = false;
      setSending(false);
      setSendPhase('classifying');
      window.setTimeout(() => textarea.current?.focus(), 0);
    }
  }

  function cancelPersonalResponse() {
    if (!confirmation || inFlight.current) return;
    setDraft(confirmation.request.prompt);
    setConfirmation(null);
    setPendingPrompt('');
    setError('');
    failedRequest.current = null;
    window.setTimeout(() => textarea.current?.focus(), 0);
  }

  async function removeConversation(id: string, confirmed = false) {
    if (inFlight.current || confirmation) return;
    if (!confirmed && !window.confirm('¿Eliminar este chat y sus mensajes?')) return;
    setDeleting(id);
    try {
      await deleteConversation(id);
      setConversations((previous) => previous.filter((item) => item.id !== id));
      if (activeId === id) selectConversation(null);
    } catch (failure) { setHistoryError(failure instanceof Error ? failure.message : 'No se pudo eliminar el chat.'); }
    finally { setDeleting(null); }
  }

  function selectModel(key: string) {
    const model = modelOptions.find((option) => option.key === key);
    if (!model) return;
    setModelPreference(model);
    saveModelPreference(model);
  }

  return {
    activeId, conversations, messages, status, draft, pendingPrompt, confirmation, sendPhase,
    sending, loading, historyLoading, historyOpen, error, historyError, deleting, selectedModel,
    limit, usageLock, personalLimit, personalRemaining, personalUsed, lockDuration, interactionPending,
    blockedReasons, modelOptions, modelsLoading, providerTokenAvailable, failedCatalogs,
    selectedModelDisplay, selectedModelAvailable, modelSelectionMessage,
    providerQueryError: providerQuery.isError, pendingModel: failedRequest.current?.model,
    textarea, confirmButton, end, setDraft, setHistoryOpen, selectModel, selectConversation,
    submit, confirmPersonalResponse, cancelPersonalResponse, removeConversation,
  };
}

export type ChatController = ReturnType<typeof useChatController>;
