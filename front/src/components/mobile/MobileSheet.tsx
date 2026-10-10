import { useEffect, useId, useRef, type ReactNode } from 'react';
import { createPortal } from 'react-dom';
import { Icon } from '../../mockup/brand';

export function MobileSheet({ open, onClose, title, children }: { open: boolean; onClose: () => void; title: string; children: ReactNode }) {
  const dialog = useRef<HTMLDialogElement>(null);
  const titleId = useId();

  useEffect(() => {
    const element = dialog.current;
    if (!open || !element) return;
    const previousFocus = document.activeElement as HTMLElement | null;
    const previousOverflow = document.body.style.overflow;
    element.showModal();
    document.body.style.overflow = 'hidden';
    return () => {
      element.close();
      document.body.style.overflow = previousOverflow;
      if (previousFocus?.isConnected) previousFocus.focus({ preventScroll: true });
    };
  }, [open]);

  if (!open) return null;
  return createPortal(<dialog ref={dialog} className="mobile-sheet" aria-labelledby={titleId}
    onCancel={(event) => { event.preventDefault(); onClose(); }}
    onClick={(event) => { if (event.target === event.currentTarget) onClose(); }}>
    <div className="mobile-sheet-surface">
      <span className="mobile-sheet-handle" aria-hidden="true" />
      <header className="mobile-sheet-heading"><h2 id={titleId}>{title}</h2><button type="button" aria-label="Cerrar panel" onClick={onClose}><Icon name="close" /></button></header>
      <div className="mobile-sheet-content">{children}</div>
    </div>
  </dialog>, document.body);
}
