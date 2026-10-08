import type { ChatController } from '../useChatController';

export function ChatHistory({ chat }: { chat: ChatController }) {
  const { historyOpen, setHistoryOpen, selectConversation, interactionPending, historyLoading, conversations, activeId, loading, removeConversation, deleting, historyError, status } = chat;
  return <>
      <aside className="chat-history" data-open={historyOpen} aria-label="Tus conversaciones">
        <div className="chat-history-heading"><strong>Tus conversaciones</strong><button className="chat-mobile-toggle chat-text-button" onClick={() => setHistoryOpen(false)} aria-label="Cerrar conversaciones">✕</button></div>
        <button className="chat-new-button" type="button" onClick={() => selectConversation(null)} disabled={interactionPending}>Nuevo chat</button>
        <div className="chat-history-list">
          {historyLoading && <p role="status">Cargando conversaciones…</p>}
          {!historyLoading && conversations.length === 0 && <p className="chat-muted">Tus chats aparecerán acá.</p>}
          {conversations.map((item) => <div className="chat-history-item" data-active={activeId === item.id} key={item.id}>
            <button type="button" title={item.title} onClick={() => selectConversation(item.id)} disabled={interactionPending || loading} aria-current={activeId === item.id ? 'page' : undefined}>{item.title}</button>
            <button type="button" className="chat-delete" aria-label={`Eliminar ${item.title}`} onClick={() => void removeConversation(item.id)} disabled={interactionPending || deleting !== null}>×</button>
          </div>)}
          {historyError && <p className="bloq-error" role="alert">{historyError}</p>}
        </div>
        <div className="chat-local-note"><div><strong>En tu equipo</strong><small>{status ? status.ready ? 'Clasificación local lista' : 'Clasificador local no disponible' : 'Conectando con el clasificador'}</small></div></div>
      </aside>
  </>;
}
