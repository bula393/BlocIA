import type { ChatController } from '../useChatController';
import { ChatComposer } from './ChatComposer';
import { ChatHistory } from './ChatHistory';
import { ChatTranscript } from './ChatTranscript';

export function ChatWorkspace({ chat }: { chat: ChatController }) {
  const { historyOpen, setHistoryOpen, selectConversation, interactionPending } = chat;
  return <div className="chat-layout">
    <ChatHistory chat={chat} />
    <section className="chat-main" aria-label="Chat con BloqIA">
      <header className="chat-toolbar"><button type="button" className="chat-mobile-toggle chat-text-button" onClick={() => setHistoryOpen(!historyOpen)} aria-expanded={historyOpen}>Conversaciones</button><span>BloqIA <small>Servicio local</small></span><button type="button" className="chat-text-button chat-toolbar-new" onClick={() => selectConversation(null)} disabled={interactionPending}>Nuevo chat</button></header>
      <ChatTranscript chat={chat} />
      <ChatComposer chat={chat} />
    </section>
  </div>;
}
