import { useEffect, useRef, useState, type FormEvent } from 'react';
import { ChasisBloqIA } from '../components/chasis/ChasisBloqIA';
import { createConversation, deleteConversation, getChatStatus, getConversation, listConversations, sendMessage, type ChatStatus, type Conversation, type Message } from '../api/chat';

const labelNames = { no_personal: 'Consulta general', personal_informativa: 'Análisis personal', personal_decision: 'Decisión personal' };
const ideas = [
  { title: 'Entender un tema', prompt: 'Explicame qué es una API con un ejemplo sencillo.' },
  { title: 'Ordenar mis ideas', prompt: '¿Qué factores debería considerar antes de cambiar de trabajo?' },
  { title: 'Evaluar una decisión', prompt: '¿Debería estudiar programación o diseño?' }
];

function ChatMessage({ message }: { message: Message }) {
  const [copied, setCopied] = useState(false);
  const [copyError, setCopyError] = useState(false);
  const classification = message.classification;
  return <article className={`chat-message chat-message--${message.role}`} aria-label={message.role === 'user' ? 'Tu mensaje' : 'Clasificación de BloqIA'}>
    {message.role === 'user' ? <div className="chat-markdown" style={{ whiteSpace: 'pre-wrap' }}>{message.content}</div> : <>
      <div className="chat-author"><span className="chat-avatar" aria-hidden="true">B</span><strong>BloqIA · Clasificador</strong></div>
      {classification ? <div className="chat-classification-result">
        <h2>{labelNames[classification.label]}</h2>
        <p><code>{classification.label}</code></p>
        <p>Confianza: <strong>{Math.round(classification.confidence * 100)} %</strong></p>
        <p>{classification.status === 'aceptada' ? 'Clasificación aceptada' : classification.status === 'baja_confianza' ? 'Clasificación con baja confianza' : 'Necesita una aclaración o revisión'}</p>
        <p data-review={classification.needs_human_review}>{classification.needs_human_review ? 'Revisión humana requerida' : 'No requiere revisión humana'}</p>
        <button type="button" className="chat-text-button" onClick={() => {
          navigator.clipboard.writeText(JSON.stringify(classification, null, 2)).then(() => { setCopied(true); setCopyError(false); }).catch(() => setCopyError(true));
        }}>{copied ? 'Copiado' : 'Copiar clasificación'}</button>
        {copyError && <small role="status">No se pudo copiar.</small>}
      </div> : <p>Este mensaje anterior no tiene una clasificación guardada.</p>}
    </>}
  </article>;
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
  const inFlight = useRef(false);
  const failedRequest = useRef<{ id: string; prompt: string; conversationId: string } | null>(null);
  const end = useRef<HTMLDivElement>(null);
  const textarea = useRef<HTMLTextAreaElement>(null);
  const limit = status?.maxInputCharacters ?? 4000;

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

  useEffect(() => { end.current?.scrollIntoView({ behavior: 'smooth', block: 'end' }); }, [messages, sending]);
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
    if (!prompt || inFlight.current || !status?.ready || loading) return;
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
      const result = await sendMessage(conversationId, prompt, requestId);
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
        <button className="chat-new-button" type="button" onClick={() => selectConversation(null)} disabled={sending}>＋ Nuevo chat</button>
        <div className="chat-history-list">
          {historyLoading && <p role="status">Cargando historial…</p>}
          {!historyLoading && conversations.length === 0 && <p className="chat-muted">Tus chats aparecerán acá.</p>}
          {conversations.map((item) => <div className="chat-history-item" data-active={activeId === item.id} key={item.id}>
            <button type="button" title={item.title} onClick={() => selectConversation(item.id)} disabled={sending || loading} aria-current={activeId === item.id ? 'page' : undefined}>{item.title}</button>
            <button type="button" className="chat-delete" aria-label={`Eliminar ${item.title}`} onClick={() => void removeConversation(item.id)} disabled={sending || deleting !== null}>×</button>
          </div>)}
          {historyError && <p className="bloq-error" role="alert">{historyError}</p>}
        </div>
        <div className="chat-local-note"><span className="chat-status-dot" data-ready={status?.ready} /><div><strong>En tu equipo</strong><small>Clasificación local</small></div></div>
      </aside>
      <section className="chat-main" aria-label="Chat con BloqIA">
        <header className="chat-toolbar"><button type="button" className="chat-mobile-toggle chat-text-button" onClick={() => setHistoryOpen(!historyOpen)} aria-expanded={historyOpen}>☰ Historial</button><span>BloqIA <small>· Local</small></span><button type="button" className="chat-text-button" onClick={() => selectConversation(null)} disabled={sending}>Nuevo chat</button></header>
        <div className="chat-scroll">
          {!loading && messages.length === 0 && !sending && <div className="chat-welcome">
            <div className="chat-welcome-mark" aria-hidden="true"><span /><span /></div>
            <p className="provider-eyebrow">Clasificador de preguntas</p>
            <h1>Clasificá tu consulta.</h1>
            <p>Escribí una consulta para conocer su categoría, confianza y si requiere revisión humana.</p>
            <div className="chat-ideas">{ideas.map((idea) => <button type="button" key={idea.title} onClick={() => { setDraft(idea.prompt); textarea.current?.focus(); }}><span>{idea.title}</span><small>{idea.prompt}</small><span aria-hidden="true">↗</span></button>)}</div>
          </div>}
          {loading && <p className="chat-loading" role="status">Cargando conversación…</p>}
          <div className="chat-transcript" role="log" aria-label="Mensajes de la conversación" aria-live="polite">
            {messages.map((message) => <ChatMessage key={message.id} message={message} />)}
            {sending && <><article className="chat-message chat-message--user"><div className="chat-markdown">{pendingPrompt}</div></article><div className="chat-thinking" role="status"><span className="chat-avatar">B</span><span>BloqIA está clasificando<span className="chat-thinking-dots">…</span></span></div></>}
          </div>
          <div ref={end} />
        </div>
        <div className="chat-composer-area">
          {error && <p className="bloq-error chat-error" role="alert">{error}</p>}
          {status && !status.ready && <p className="bloq-status-line" data-state="attention">El modelo local todavía no está listo para clasificar.</p>}
          <form className="chat-composer" onSubmit={submit}>
            <label className="chat-input-label" htmlFor="chat-prompt">Mensaje para BloqIA</label>
            <textarea id="chat-prompt" ref={textarea} value={draft} onChange={(event) => setDraft(event.target.value)} placeholder="Escribí tu mensaje…" rows={2} maxLength={limit} disabled={sending || loading} onKeyDown={(event) => { if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing) { event.preventDefault(); event.currentTarget.form?.requestSubmit(); } }} />
            <div className="chat-composer-bottom"><small>{sending ? 'Clasificando en tu equipo…' : draft.length > limit * 0.8 ? `${draft.length} / ${limit}` : 'Enter para enviar · Shift + Enter para un salto'}</small><button type="submit" className="chat-send" data-primary="true" aria-label="Enviar mensaje" disabled={!draft.trim() || sending || loading || !status?.ready}><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 19V5m-6 6 6-6 6 6" /></svg></button></div>
          </form>
          <p className="chat-footnote">El historial se guarda en este equipo. Cada consulta se clasifica por separado.</p>
        </div>
      </section>
    </div>
  </ChasisBloqIA>;
}
