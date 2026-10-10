import { useState } from 'react';
import { Icon } from '../../../mockup/brand';
import { MobileSheet } from '../../../components/mobile/MobileSheet';
import type { ChatController } from '../useChatController';

export const chatPrivacyDescription = 'Para adaptar las respuestas usamos tu nombre visible, edad, profesión y los intercambios recientes de este chat. Si elegís un proveedor externo, se le envía ese contexto junto con tu consulta. Las conversaciones se guardan en tu cuenta.';

export function ChatComposerInfo({ chat }: { chat: ChatController }) {
  const [open, setOpen] = useState(false);
  return <>
    <button type="button" className="chat-composer-info" aria-label="Información del chat" title="Información del chat" aria-haspopup="dialog" onClick={() => setOpen(true)}><Icon name="info" size={20} /></button>
    <MobileSheet open={open} onClose={() => setOpen(false)} title="Información del chat">
      <h3>Modelo seleccionado</h3>
      <p>{chat.selectedModelDisplay.displayName} · {chat.selectedModelDisplay.providerName}</p>
      <h3>Respuestas personales</h3>
      <p>Te quedan {chat.personalRemaining} de {chat.personalLimit} respuestas personales en las últimas 24 horas. Te pedimos confirmación después de clasificar la consulta y antes de enviarla al modelo.</p>
      <h3>Datos que compartís</h3>
      <p>{chatPrivacyDescription}</p>
    </MobileSheet>
  </>;
}
