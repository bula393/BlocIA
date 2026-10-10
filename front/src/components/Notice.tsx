import { useState, type ReactNode } from 'react';
import { Icon } from '../mockup/brand';
import './notice.css';

/** Closing a notice only hides its feedback; it never changes the underlying request state. */
export function Notice({ children, className = 'bloq-error', role = 'alert', id, onDismiss }: {
  children: ReactNode;
  className?: string;
  role?: 'alert' | 'status';
  id?: string;
  onDismiss?: () => void;
}) {
  const [dismissed, setDismissed] = useState(false);
  if (dismissed) return null;
  return <div id={id} className={`bloq-notice ${className}`} role={role}>
    <div className="bloq-notice-content">{children}</div>
    <button type="button" className="bloq-notice-close" aria-label="Cerrar aviso" title="Cerrar aviso"
      onClick={() => { setDismissed(true); onDismiss?.(); }}><Icon name="close" size={18} /></button>
  </div>;
}
