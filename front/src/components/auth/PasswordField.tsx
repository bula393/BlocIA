import { useId, useState } from 'react';
import { Icon } from '../../mockup/brand';

export function PasswordField({ value, onChange, autoComplete }: { value: string; onChange: (value: string) => void; autoComplete: 'current-password' | 'new-password' }) {
  const [visible, setVisible] = useState(false);
  const id = useId();
  return <div className="auth-password-field"><label htmlFor={id}>Contraseña</label><div><input id={id} autoComplete={autoComplete} type={visible ? 'text' : 'password'} value={value} onChange={(event) => onChange(event.target.value)} required /><button type="button" aria-label={visible ? 'Ocultar contraseña' : 'Mostrar contraseña'} aria-pressed={visible} onClick={() => setVisible(!visible)}><Icon name={visible ? 'eye-off' : 'eye'} size={20} /></button></div></div>;
}
