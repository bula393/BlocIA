import type { ChatController } from '../useChatController';
import { classificationLabels as labelNames } from '../helpers';

export function PersonalResponseConfirmation({ chat }: { chat: ChatController }) {
  const { confirmation, sending, personalLimit, personalRemaining, confirmButton, confirmPersonalResponse, usageLock, cancelPersonalResponse } = chat;
  return <>
            {confirmation && !sending && <section className="chat-personal-confirmation" aria-labelledby="personal-confirmation-title">
              <h2 id="personal-confirmation-title">{confirmation.accepted ? 'Tu respuesta quedó pendiente' : `¿Querés usar 1 de tus ${personalLimit} respuestas personales diarias?`}</h2>
              <p>Tu consulta se clasificó como <strong>{labelNames[confirmation.classification.label].toLocaleLowerCase('es-AR')}</strong>. Te quedan {personalRemaining} de {personalLimit} respuestas personales.</p>
              {confirmation.accepted && <p>Podés reintentar con el mismo botón sin gastar otra respuesta.</p>}
              <div className="chat-confirmation-actions">
                <button ref={confirmButton} type="button" data-primary="true" onClick={() => void confirmPersonalResponse()} disabled={Boolean(usageLock?.blocked) && !confirmation.accepted}>{confirmation.accepted ? 'Reintentar respuesta' : 'Usar 1 respuesta'}</button>
                {!confirmation.accepted && <button type="button" onClick={cancelPersonalResponse}>Cancelar</button>}
              </div>
            </section>}
  </>;
}
