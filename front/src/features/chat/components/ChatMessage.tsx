import { useState } from 'react';
import type { Message } from '../../../api/chat';
import { MarkdownContent } from '../../../components/MarkdownContent';
import { Icon } from '../../../mockup/brand';
import { classificationLabels as labelNames } from '../helpers';
import { MobileSheet } from '../../../components/mobile/MobileSheet';
import { useMobileViewport } from '../../../components/mobile/useMobileViewport';

export function ChatMessage({ message }: { message: Message }) {
  const mobile = useMobileViewport();
  const [classificationOpen, setClassificationOpen] = useState(false);
  const classification = message.classification;
  if (message.role === 'user') {
    return <article className="chat-message chat-message--user" aria-label="Tu mensaje"><div className="chat-markdown">{message.content}</div></article>;
  }

  let content = message.content;
  // Older conversations stored the classifier JSON as the assistant message.
  if (!message.modelId && classification && content.startsWith('{')) {
    try {
      const legacy = JSON.parse(content) as { label?: string };
      if (legacy.label && legacy.label in labelNames) content = `Esta consulta fue clasificada como **${labelNames[legacy.label as keyof typeof labelNames]}**.`;
    } catch { /* Display non-JSON assistant content as written. */ }
  }

  const classificationDetails = classification && <div className="chat-classification-details" id={`classification-${message.id}`}>
    <strong>Clasificación del mensaje</strong>
    <p>Categoría: <b>{labelNames[classification.label]}</b></p><p><code>{classification.label}</code></p>
    <p>Confianza: <b>{Math.round(classification.confidence * 100)} %</b></p>
    <p>{classification.status === 'aceptada' ? 'Clasificación aceptada' : classification.status === 'baja_confianza' ? 'Clasificación con baja confianza' : 'Necesita una aclaración o revisión'}</p>
    <p data-review={classification.needs_human_review}>{classification.needs_human_review ? 'Revisión humana requerida' : 'No requiere revisión humana'}</p>
    {classification.probabilities && <div className="chat-classification-probabilities"><span>Probabilidades</span>{Object.entries(classification.probabilities).map(([label, probability]) => <small key={label}>{label}: {Math.round(probability * 100)} %</small>)}</div>}
  </div>;

  return <div className="chat-response-row">
    <article className="chat-message chat-message--assistant" data-classification={classification?.label ?? 'no_personal'} data-needs-review={classification?.needs_human_review ?? false} aria-label="Respuesta de BloqIA">
      <div className="chat-author"><span className="chat-avatar" aria-hidden="true">B</span><strong>BloqIA</strong>{(message.providerId === 'local' || message.modelId) && <span className="chat-author-model">Modelo: {message.providerId === 'local' ? 'Qwen3-0.6B local' : message.modelId}</span>}</div>
      <div className="chat-markdown"><MarkdownContent content={content} /></div>
    </article>
    {classification && (mobile ? <div className="chat-classification-mobile"><button type="button" onClick={() => setClassificationOpen(true)}><Icon name="layers" size={16} /><span>{labelNames[classification.label]} · Ver clasificación</span><Icon name="chevron-down" size={16} /></button><MobileSheet open={classificationOpen} onClose={() => setClassificationOpen(false)} title="Antes de responder">{classificationDetails}{classification.label === 'personal_decision' && <p>Las decisiones personales quedan en tus manos. Esta consulta no se envía al generador.</p>}<button type="button" className="mobile-sheet-primary" onClick={() => setClassificationOpen(false)}>Volver a la conversación</button></MobileSheet></div> : <details className="chat-classification">
      <summary>Ver clasificación<Icon name="chevron" size={15} /></summary>
      {classificationDetails}
    </details>)}
  </div>;
}
