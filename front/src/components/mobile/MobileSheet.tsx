import { useId, useRef, type ReactNode } from 'react';
import { createPortal } from 'react-dom';
import { Icon } from '../../mockup/brand';
import { useSheetMotion } from './useSheetMotion';

export function MobileSheet({ open, onClose, title, children }: { open: boolean; onClose: () => void; title: string; children: ReactNode }) {
  const dialog = useRef<HTMLDialogElement>(null);
  const titleId = useId();
  const { present, dismiss, ...gesture } = useSheetMotion(dialog, open, onClose);
  const backdropPressed = useRef(false);

  if (!present) return null;
  return createPortal(<dialog ref={dialog} className="mobile-sheet" aria-labelledby={titleId}
    onCancel={(event) => { event.preventDefault(); dismiss(); }}
    onPointerDown={(event) => { backdropPressed.current = event.target === event.currentTarget; }}
    onClick={(event) => { if (backdropPressed.current && event.target === event.currentTarget) dismiss(); backdropPressed.current = false; }}>
    <div className="mobile-sheet-surface">
      <div className="mobile-sheet-grab" aria-hidden="true" {...gesture}><span className="mobile-sheet-handle" /></div>
      <header className="mobile-sheet-heading"><h2 id={titleId}>{title}</h2><button type="button" aria-label="Cerrar panel" onClick={dismiss}><Icon name="close" /></button></header>
      <div className="mobile-sheet-content">{children}</div>
    </div>
  </dialog>, document.body);
}
