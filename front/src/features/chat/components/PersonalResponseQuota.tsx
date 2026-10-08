import type { ChatController } from '../useChatController';

export function PersonalResponseQuota({ chat }: { chat: ChatController }) {
  const { usageLock, personalRemaining, personalLimit, personalUsed } = chat;
  return <>
            <aside className="chat-personal-quota" data-blocked={personalRemaining === 0} aria-label="Cupo de respuestas personales">
            {usageLock ? <>
              <p aria-live="polite">Te quedan <strong>{personalRemaining} de {personalLimit}</strong> respuestas personales.</p>
              <div className="chat-quota-track" role="progressbar" aria-label="Respuestas personales usadas antes del bloqueo" aria-valuemin={0} aria-valuemax={personalLimit} aria-valuenow={personalUsed} aria-valuetext={`${personalUsed} usadas; ${personalRemaining} disponibles de ${personalLimit}`}><span style={{ transform: `scaleX(${personalUsed / personalLimit})` }} /></div>
              <small>{personalUsed} de {personalLimit} usadas · últimas 24 h</small>
            </> : <p role="status">Consultando tu cupo…</p>}
            </aside>
  </>;
}
