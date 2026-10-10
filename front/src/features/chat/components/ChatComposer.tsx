import type { ChatController } from '../useChatController';
import { Icon } from '../../../mockup/brand';
import { ChatModelPicker } from './ChatModelPicker';
import { ChatUsageLock } from './ChatUsageLock';
import { PersonalResponseConfirmation } from './PersonalResponseConfirmation';
import { PersonalResponseQuota } from './PersonalResponseQuota';

export function ChatComposer({ chat }: { chat: ChatController }) {
  const { usageLock, error, status, submit, textarea, draft, setDraft, limit, confirmation, interactionPending, loading, sending, sendPhase, modelsLoading, selectedModelAvailable } = chat;
  return <div className={`chat-composer-area${usageLock?.blocked ? ' chat-composer-area--locked' : ''}`}>
    {error && <p className="bloq-error chat-error" role="alert">{error}</p>}
    {status && !status.ready && <p className="bloq-status-line" data-state="attention">El clasificador todavía no está listo.</p>}
    <form className="chat-composer" onSubmit={submit}>
      <PersonalResponseConfirmation chat={chat} />
      <label className="chat-input-label" htmlFor="chat-prompt">Mensaje para BloqIA</label>
      <ChatUsageLock chat={chat} />
      <textarea id="chat-prompt" ref={textarea} value={draft} onChange={(event) => setDraft(event.target.value)} placeholder={usageLock?.blocked ? '' : 'Escribí tu mensaje…'} rows={2} maxLength={limit} hidden={confirmation !== null} disabled={interactionPending || loading || usageLock?.blocked} onKeyDown={(event) => { if (event.key === 'Enter' && !event.shiftKey && !event.nativeEvent.isComposing) { event.preventDefault(); event.currentTarget.form?.requestSubmit(); } }} />
      <ChatModelPicker chat={chat} />
      {!usageLock?.blocked && <div className="chat-composer-bottom" data-show-hint={sending || confirmation !== null || modelsLoading || draft.length > limit * 0.8}><small>{sending ? sendPhase === 'waiting_model' ? 'Esperando la respuesta…' : 'Clasificando tu consulta…' : confirmation ? confirmation.accepted ? 'Reintentá la respuesta pendiente' : 'Confirmá o cancelá la consulta pendiente' : modelsLoading ? 'Cargando modelos…' : draft.length > limit * 0.8 ? `${draft.length} / ${limit}` : 'Enter para enviar, Shift + Enter para un salto'}</small><button type="submit" className="chat-send" data-primary="true" aria-label="Enviar mensaje" title="Enviar mensaje" disabled={!draft.trim() || interactionPending || loading || modelsLoading || !selectedModelAvailable || !status?.ready}><Icon name="send" size={19} /></button></div>}
      <PersonalResponseQuota chat={chat} />
    </form>
    <p className="chat-footnote">Para adaptar las respuestas usamos tu nombre visible, edad, profesión y los intercambios recientes de este chat. Si elegís un proveedor externo, se le envía ese contexto junto con tu consulta. Las conversaciones se guardan en tu cuenta.</p>
  </div>;
}
