import type { ChatController } from '../useChatController';
import { Icon } from '../../../mockup/brand';
import { chatIdeas as ideas } from '../helpers';
import { ChatMessage } from './ChatMessage';

export function ChatTranscript({ chat }: { chat: ChatController }) {
  const { usageLock, loading, messages, interactionPending, setDraft, textarea, sending, pendingPrompt, sendPhase, pendingModel, end } = chat;
  return <>
        <div className="chat-scroll">
          {!usageLock?.blocked && !loading && messages.length === 0 && !interactionPending && <div className="chat-welcome">
            <div className="chat-welcome-mark" aria-hidden="true"><span /><span /><span /></div>
            <p className="chat-welcome-label">Clasificador de preguntas</p>
            <h1>Clasificá tu <em>consulta.</em></h1>
            <p>Escribí una consulta para ver su clasificación. Las consultas generales e informativas también reciben una respuesta del modelo elegido.</p>
            <div className="chat-ideas">{ideas.map((idea) => <button type="button" key={idea.title} onClick={() => { setDraft(idea.prompt); textarea.current?.focus(); }}><span>{idea.title}</span><small>{idea.prompt}</small><Icon name="arrow-up-right" size={16} /></button>)}</div>
          </div>}
          {loading && <p className="chat-loading" role="status">Cargando conversación…</p>}
          <div className="chat-transcript" role="log" aria-label="Mensajes de la conversación" aria-live="polite">
            {messages.map((message) => <ChatMessage key={message.id} message={message} />)}
            {interactionPending && <>
              <article className="chat-message chat-message--user" aria-label="Tu consulta pendiente"><div className="chat-markdown">{pendingPrompt}</div></article>
              {sending && <div className="chat-progress-card" role="status" aria-live="polite">
                <strong>{sendPhase === 'waiting_model' ? 'Consulta clasificada; esperando la respuesta del modelo' : 'Estamos clasificando tu consulta'}</strong>
                <p>{sendPhase === 'waiting_model'
                  ? `Esperando a ${pendingModel?.displayName ?? 'el modelo'} ${pendingModel?.providerId === 'local' ? 'en este equipo' : 'en la nube'}.`
                  : 'Las consultas informativas personales te piden confirmación antes de pasar al modelo.'}</p>
              </div>}
            </>}
          </div>
          <div ref={end} />
        </div>
  </>;
}
