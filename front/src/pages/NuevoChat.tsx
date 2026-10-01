import { useEffect, useRef, useState, type FormEvent } from 'react';
import { useQueries, useQuery } from '@tanstack/react-query';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { ChasisBloqIA } from '../components/chasis/ChasisBloqIA';
import { createConversation, deleteConversation, getChatStatus, getConversation, listConversations, sendMessage, type ChatStatus, type Conversation, type Message } from '../api/chat';
import { listAvailableModels, listTechnicalProviders } from '../api/technicalProfile';

const labelNames = { no_personal: 'Consulta general', personal_informativa: 'Análisis personal', personal_decision: 'Decisión personal' };
const ideas = [
  { title: 'Entender un tema', prompt: 'Explicame qué es una API con un ejemplo sencillo.' },
  { title: 'Ordenar mis ideas', prompt: '¿Qué factores debería considerar antes de cambiar de trabajo?' },
  { title: 'Evaluar una decisión', prompt: '¿Debería estudiar programación o diseño?' }
];

function ChatMessage({ message }: { message: Message }) {
  const classification = message.classification;
  if (message.role === 'user') {
    return <article className="chat-message chat-message--user" aria-label="Tu mensaje"><div className="chat-markdown">{message.content}</div></article>;
  }

  let content = message.content;
  // Older conversations stored the classifier JSON as the assistant message.
  if (!message.modelId && classification && content.startsWith('{')) {
    try {
      const legacy = JSON.parse(content) as { label?: string };
      if (legacy.label && legacy.label in labelNames) content = `Esta consulta fue clasificada como **${labelNames[legacy.label as keyof typeof labelNames]}**.`;
    } catch { /* Display non-JSON assistant content as written. */ }
  }

  return <div className="chat-response-row">
    <article className="chat-message chat-message--assistant" data-classification={classification?.label ?? 'no_personal'} data-needs-review={classification?.needs_human_review ?? false} aria-label="Respuesta de BloqIA">
      <div className="chat-author"><span className="chat-avatar" aria-hidden="true">B</span><strong>BloqIA</strong>{(message.providerId === 'local' || message.modelId) && <span className="chat-author-model">Modelo: {message.providerId === 'local' ? 'Qwen3-0.6B local' : message.modelId}</span>}</div>
      <div className="chat-markdown"><ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown></div>
    </article>
    {classification && <details className="chat-classification">
      <summary>Ver clasificación</summary>
      <div className="chat-classification-details" id={`classification-${message.id}`}>
        <strong>Clasificación del mensaje</strong>
        <p>Categoría: <b>{labelNames[classification.label]}</b></p>
        <p><code>{classification.label}</code></p>
        <p>Confianza: <b>{Math.round(classification.confidence * 100)} %</b></p>
        <p>{classification.status === 'aceptada' ? 'Clasificación aceptada' : classification.status === 'baja_confianza' ? 'Clasificación con baja confianza' : 'Necesita una aclaración o revisión'}</p>
        <p data-review={classification.needs_human_review}>{classification.needs_human_review ? 'Revisión humana requerida' : 'No requiere revisión humana'}</p>
        {classification.probabilities && <div className="chat-classification-probabilities"><span>Probabilidades</span>{Object.entries(classification.probabilities).map(([label, probability]) => <small key={label}>{label}: {Math.round(probability * 100)} %</small>)}</div>}
      </div>
    </details>}
  </div>;
}

interface ChatModelOption { key: string; providerId: string; providerName: string; modelId: string; displayName: string }

function providerLabel(providerId: string, fallback: string) {
  const known: Record<string, string> = { local: 'En tu equipo', google: 'Google AI', groq: 'Groq', openrouter: 'OpenRouter', openai: 'OpenAI', anthropic: 'Anthropic' };
  return known[providerId] ?? fallback.replace(/\s*·\s*/g, ', ');
}

export function NuevoChat() {
  const initialId = new URLSearchParams(window.location.search).get('chat');
  const [activeId, setActiveId] = useState<string | null>(initialId && /^[a-f\d-]{36}$/i.test(initialId) ? initialId : null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [status, setStatus] = useState<ChatStatus | null>(null);
  const [draft, setDraft] = useState('');
  const [pendingPrompt, setPendingPrompt] = useState('');
  const [sending, setSending] = useState(false);
  const [loading, setLoading] = useState(false);
  const [historyLoading, setHistoryLoading] = useState(true);
  const [historyOpen, setHistoryOpen] = useState(false);
  const [error, setError] = useState('');
  const [historyError, setHistoryError] = useState('');
  const [deleting, setDeleting] = useState<string | null>(null);
  const [selectedModel, setSelectedModel] = useState('');
  const inFlight = useRef(false);
  const failedRequest = useRef<{ id: string; prompt: string; conversationId: string } | null>(null);
  const end = useRef<HTMLDivElement>(null);
  const textarea = useRef<HTMLTextAreaElement>(null);
  const limit = status?.maxInputCharacters ?? 4000;
  const providerQuery = useQuery({ queryKey: ['chat-providers'], queryFn: listTechnicalProviders });
  const configuredProviders = (providerQuery.data?.providers ?? []).filter((provider) => provider.status === 'available' && provider.tokenStatus.status === 'configured');
  const modelCatalogQueries = useQueries({
    queries: configuredProviders.map((provider) => ({
      queryKey: ['chat-models', provider.providerId],
      queryFn: () => listAvailableModels(provider.providerId),
      retry: false
    }))
  });
  const modelCatalogQueryByProvider = new Map(configuredProviders.map((provider, index) => [provider.providerId, modelCatalogQueries[index]]));
  const modelOptions: ChatModelOption[] = [
    ...configuredProviders.flatMap((provider) => {
      const catalog = modelCatalogQueryByProvider.get(provider.providerId)?.data;
      if (!catalog || catalog.source !== 'token') return [];
      return catalog.models.filter((model) => model.availabilityStatus === 'available').map((model) => ({ key: `${provider.providerId}:${model.modelId}`, providerId: provider.providerId, providerName: providerLabel(provider.providerId, provider.name), modelId: model.modelId, displayName: model.displayName }));
    }),
    ...(status?.freeModels ?? []).map((model) => ({ ...model, key: `${model.providerId}:${model.modelId}`, providerName: providerLabel(model.providerId, model.providerName) }))
  ];
  const selectedModelOption = modelOptions.find((model) => model.key === selectedModel);
  const modelsLoading = !status || providerQuery.isLoading || modelCatalogQueries.some((query) => query.isLoading);
  const providerTokenAvailable = configuredProviders.length > 0;
  const failedCatalogs = configuredProviders.flatMap((provider, index) => {
    const query = modelCatalogQueries[index];
    if (!query?.isError) return [];
    const reason = query.error instanceof Error ? query.error.message : 'No se pudo consultar el catálogo.';
    return [`${provider.name}: ${reason}`];
  });

  useEffect(() => {
    if (!modelOptions.length) {
      if (selectedModel) setSelectedModel('');
    } else if (!modelOptions.some((model) => model.key === selectedModel)) {
      setSelectedModel(modelOptions[0].key);
    }
  }, [modelOptions, selectedModel]);

  useEffect(() => {
    const controller = new AbortController();
    getChatStatus(controller.signal).then(setStatus).catch((failure: Error) => { if (!controller.signal.aborted) setError(failure.message); });
    listConversations(controller.signal).then((result) => setConversations(result.conversations))
      .catch((failure: Error) => { if (!controller.signal.aborted) setHistoryError(failure.message); })
      .finally(() => { if (!controller.signal.aborted) setHistoryLoading(false); });
    return () => controller.abort();
  }, []);

  useEffect(() => {
    const url = activeId ? `/nuevo-chat?chat=${encodeURIComponent(activeId)}` : '/nuevo-chat';
    window.history.replaceState({}, '', url);
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
    if (messages.length > 0 || sending) end.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [messages, sending]);
  useEffect(() => {
    if (textarea.current) {
      textarea.current.style.height = 'auto';
      textarea.current.style.height = `${Math.min(textarea.current.scrollHeight, 160)}px`;
    }
  }, [draft]);

  function selectConversation(id: string | null) {
    if (inFlight.current) return;
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

  async function submit(event: FormEvent) {
    event.preventDefault();
    const prompt = draft.trim();
    if (!prompt || inFlight.current || !status?.ready || loading || modelsLoading) return;
    inFlight.current = true;
    setSending(true);
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
      const requestId = previous?.prompt === prompt && previous.conversationId === conversationId ? previous.id : crypto.randomUUID();
      failedRequest.current = { id: requestId, prompt, conversationId };
      const result = await sendMessage(conversationId, prompt, requestId, selectedModelOption ? { providerId: selectedModelOption.providerId, modelId: selectedModelOption.modelId } : undefined);
      setMessages(result.messages);
      setConversations((previous) => [result.conversation, ...previous.filter((item) => item.id !== result.conversation.id)]);
      failedRequest.current = null;
    } catch (failure) {
      setError(failure instanceof Error ? failure.message : 'No se pudo enviar el mensaje.');
      setDraft(prompt);
    } finally {
      inFlight.current = false;
      setSending(false);
      setPendingPrompt('');
      window.setTimeout(() => textarea.current?.focus(), 0);
    }
  }

  async function removeConversation(id: string) {
    if (!window.confirm('¿Eliminar este chat y sus mensajes?')) return;
    setDeleting(id);
    try {
      await deleteConversation(id);
      setConversations((previous) => previous.filter((item) => item.id !== id));
      if (activeId === id) selectConversation(null);
    } catch (failure) { setHistoryError(failure instanceof Error ? failure.message : 'No se pudo eliminar el chat.'); }
    finally { setDeleting(null); }
  }

  return <ChasisBloqIA title="Chat" activePath="/nuevo-chat">
    <div className="chat-layout">
      <aside className="chat-history" data-open={historyOpen} aria-label="Historial de conversaciones">
        <div className="chat-history-heading"><strong>Tus conversaciones</strong><button className="chat-mobile-toggle chat-text-button" onClick={() => setHistoryOpen(false)} aria-label="Cerrar historial">✕</button></div>
        <button className="chat-new-button" type="button" onClick={() => selectConversation(null)} disabled={sending}>Nuevo chat</button>
        <div className="chat-history-list">
          {historyLoading && <p role="status">Cargando historial…</p>}
          {!historyLoading && conversations.length === 0 && <p className="chat-muted">Tus chats aparecerán acá.</p>}
          {conversations.map((item) => <div className="chat-history-item" data-active={activeId === item.id} key={item.id}>
            <button type="button" title={item.title} onClick={() => selectConversation(item.id)} disabled={sending || loading} aria-current={activeId === item.id ? 'page' : undefined}>{item.title}</button>
            <button type="button" className="chat-delete" aria-label={`Eliminar ${item.title}`} onClick={() => void removeConversation(item.id)} disabled={sending || deleting !== null}>×</button>
          </div>)}
          {historyError && <p className="bloq-error" role="alert">{historyError}</p>}
        </div>
        <div className="chat-local-note"><div><strong>En tu equipo</strong><small>{status ? status.ready ? 'Clasificación local lista' : 'Clasificador local no disponible' : 'Conectando con el clasificador'}</small></div></div>
      </aside>
      <section className="chat-main" aria-label="Chat con BloqIA">
        <header className="chat-toolbar"><button type="button" className="chat-mobile-toggle chat-text-button" onClick={() => setHistoryOpen(!historyOpen)} aria-expanded={historyOpen}>Historial</button><span>BloqIA <small>Servicio local</small></span><button type="button" className="chat-text-button chat-toolbar-new" onClick={() => selectConversation(null)} disabled={sending}>Nuevo chat</button></header>
        <div className="chat-scroll">
          {!loading && messages.length === 0 && !sending && <div className="chat-welcome">
            <div className="chat-welcome-mark" aria-hidden="true"><span /><span /></div>
            <p className="chat-welcome-label">Clasificador de preguntas</p>
            <h1>Clasificá tu consulta.</h1>
            <p>Escribí una consulta para ver su clasificación. Las consultas generales e informativas también reciben una respuesta del modelo elegido.</p>
            <div className="chat-ideas">{ideas.map((idea) => <button type="button" key={idea.title} onClick={() => { setDraft(idea.prompt); textarea.current?.focus(); }}><span>{idea.title}</span><small>{idea.prompt}</small></button>)}</div>
          </div>}
          {loading && <p className="chat-loading" role="status">Cargando conversación…</p>}
          <div className="chat-transcript" role="log" aria-label="Mensajes de la conversación" aria-live="polite">
            {messages.map((message) => <ChatMessage key={message.id} message={message} />)}
            {sending && <>
              <article className="chat-message chat-message--user"><div className="chat-markdown">{pendingPrompt}</div></article>
              <div className="chat-progress-card" role="status" aria-live="polite">
                <strong>Estamos clasificando tu consulta</strong>
                <p>{selectedModelOption ? `Si corresponde, ${selectedModelOption.displayName} generará la respuesta.` : 'Si corresponde, el modelo disponible generará la respuesta.'}</p>
              </div>
            </>}
          </div>
          <div ref={end} />
        </div>
        <div className="chat-composer-area">
          {error && <p className="bloq-error chat-error" role="alert">{error}</p>}
          {status && !status.ready && <p className="bloq-status-line" data-state="attention">El modelo local todavía no está listo para clasificar.</p>}
          <form className="chat-composer" onSubmit={submit}>
            <label className="chat-input-label" htmlFor="chat-prompt">Mensaje para BloqIA</label>
            <textarea id="chat-prompt" ref={textarea} value={draft} onChange={(event) => setDraft(event.target.value)} placeholder="Escribí tu mensaje…" rows={2} maxLength={limit} disabled={sending || loading} onKeyDown={(event) => { if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing) { event.preventDefault(); event.currentTarget.form?.requestSubmit(); } }} />
            <div className="chat-model-picker">
              <label htmlFor="chat-model">Modelo de respuesta</label>
              <select id="chat-model" value={selectedModel} onChange={(event) => setSelectedModel(event.target.value)} disabled={!modelOptions.length || sending || loading}>
                {modelOptions.length === 0 && <option value="">Sin modelo conectado</option>}
                {modelOptions.map((model) => <option value={model.key} key={model.key}>{model.displayName} — {model.providerName}</option>)}
              </select>
              {modelOptions.length === 0 && <small>{modelsLoading ? 'Buscando modelos…' : providerQuery.isError ? 'No se pudieron cargar tus proveedores.' : providerTokenAvailable ? 'No hay modelos disponibles para las claves conectadas. Revisá tu Perfil técnico.' : <>Conectá un proveedor desde <a href="/perfil-tecnico">Perfil técnico</a> para generar respuestas.</>}</small>}
              {failedCatalogs.length > 0 && <small className="bloq-error">No se pudieron cargar modelos. {failedCatalogs.join('; ')} Podés usar Qwen local si está instalado.</small>}
            </div>
            <div className="chat-composer-bottom"><small>{sending ? 'Clasificando en tu equipo…' : modelsLoading ? 'Cargando modelos…' : draft.length > limit * 0.8 ? `${draft.length} / ${limit}` : 'Enter para enviar, Shift + Enter para un salto'}</small><button type="submit" className="chat-send" data-primary="true" aria-label="Enviar mensaje" disabled={!draft.trim() || sending || loading || modelsLoading || !status?.ready}><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 19V5m-6 6 6-6 6 6" /></svg></button></div>
          </form>
          <p className="chat-footnote">Para adaptar las respuestas usamos tu nombre visible, edad, profesión y los intercambios recientes de este chat. Si elegís un proveedor externo, se le envía ese contexto junto con tu consulta. El historial se guarda en este equipo.</p>
        </div>
      </section>
    </div>
  </ChasisBloqIA>;
}
