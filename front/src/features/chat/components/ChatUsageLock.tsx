import type { ChatController } from '../useChatController';
import { Icon } from '../../../mockup/brand';

export function ChatUsageLock({ chat }: { chat: ChatController }) {
  const { usageLock, lockDuration, blockedReasons } = chat;
  return <>
            {usageLock?.blocked && <section className="chat-lock-panel" role="alert" aria-live="assertive">
              <div className="chat-lock-side chat-lock-side--reason">
                <p className="chat-lock-eyebrow">Pausa de seguridad · {lockDuration}</p>
                <h2>Bloqueo activo</h2>
                {usageLock.reasonCodes.map((reason) => <p className="chat-lock-reason" key={reason}>{blockedReasons[reason] ?? 'Se alcanzó un límite de uso.'}</p>)}
              </div>
              <span className="chat-lock-icon"><Icon name="lock" size={23} /></span>
              <div className="chat-lock-side chat-lock-side--until">
                <p className="chat-lock-eyebrow">Se habilita</p>
                {usageLock.lockUntil
                  ? <time dateTime={usageLock.lockUntil}>{new Intl.DateTimeFormat('es-AR', { dateStyle: 'long', timeStyle: 'short' }).format(new Date(usageLock.lockUntil))}</time>
                  : <strong>Dentro de {lockDuration}</strong>}
                <small>Hasta entonces, el envío permanece bloqueado.</small>
              </div>
            </section>}
  </>;
}
