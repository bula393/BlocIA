import { useState } from 'react';
import type { ChatController } from '../useChatController';
import { Icon } from '../../../mockup/brand';
import { MobileSheet } from '../../../components/mobile/MobileSheet';
import { useMobileViewport } from '../../../components/mobile/useMobileViewport';

export function ChatHistory({ chat }: { chat: ChatController }) {
  const { historyOpen, setHistoryOpen, selectConversation, interactionPending, historyLoading, conversations, activeId, loading, removeConversation, deleting, historyError, status } = chat;
  const mobile = useMobileViewport();
  const [query, setQuery] = useState('');
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const visibleConversations = mobile ? conversations.filter((item) => item.title.toLocaleLowerCase('es-AR').includes(query.trim().toLocaleLowerCase('es-AR'))) : conversations;
  return <>
      <aside className="chat-history" data-open={historyOpen} aria-label="Tus conversaciones">
        <div className="chat-history-heading"><strong>Tus conversaciones</strong><button className="chat-mobile-toggle chat-text-button" onClick={() => setHistoryOpen(false)} aria-label="Cerrar conversaciones"><Icon name="close" size={19} /></button></div>
        <div className="chat-mobile-history-intro"><h1>Tus conversaciones.</h1><p>Las ideas siguen donde las dejaste.</p><label className="chat-history-search"><Icon name="search" size={19} /><input type="search" aria-label="Buscar conversaciones" placeholder="Buscar una conversación" value={query} onChange={(event) => setQuery(event.target.value)} /></label></div>
        <button className="chat-new-button" type="button" onClick={() => selectConversation(null)} disabled={interactionPending}><Icon name="plus" size={19} /><span>Nuevo chat</span></button>
        <div className="chat-history-list">
          {historyLoading && <p role="status">Cargando conversaciones…</p>}
          {!historyLoading && conversations.length === 0 && <p className="chat-muted">Tus chats aparecerán acá.</p>}
          {visibleConversations.map((item) => <div className="chat-history-item" data-active={activeId === item.id} key={item.id}>
            <button type="button" title={item.title} onClick={() => selectConversation(item.id)} disabled={interactionPending || loading} aria-current={activeId === item.id ? 'page' : undefined}><span>{item.title}</span><small className="chat-mobile-history-date">{new Intl.DateTimeFormat('es-AR', { day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit' }).format(new Date(item.updatedAt))}</small></button>
            <button type="button" className="chat-delete" aria-label={`Eliminar ${item.title}`} onClick={() => { if (mobile) setDeleteId(item.id); else void removeConversation(item.id); }} disabled={interactionPending || deleting !== null}><Icon name="trash" size={17} /></button>
          </div>)}
          {mobile && query.trim() && !visibleConversations.length && !historyLoading && <p role="status">No encontramos ese chat. Probá con otra palabra.</p>}
          {historyError && <p className="bloq-error" role="alert">{historyError}</p>}
        </div>
        <div className="chat-local-note"><div><strong>En tu equipo</strong><small>{status ? status.ready ? 'Clasificación local lista' : 'Clasificador local no disponible' : 'Conectando con el clasificador'}</small></div></div>
      </aside>
      {mobile && <MobileSheet open={deleteId !== null} onClose={() => setDeleteId(null)} title="¿Eliminar este chat?">
        <p>Se eliminará la conversación y sus mensajes de tu cuenta.</p>
        <button type="button" className="mobile-sheet-primary mobile-sheet-danger" onClick={() => { if (deleteId) void removeConversation(deleteId, true); setDeleteId(null); }} disabled={interactionPending || deleting !== null}>Eliminar conversación</button>
        <button type="button" className="mobile-sheet-secondary" onClick={() => setDeleteId(null)}>Conservar chat</button>
      </MobileSheet>}
  </>;
}
