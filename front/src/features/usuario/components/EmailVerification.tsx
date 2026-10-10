import { Notice } from '../../../components/Notice';
import { useEffect, useRef, useState, type FormEvent } from 'react';
import type { usePerfilTecnico } from '../usePerfilTecnico';
import { Icon } from '../../../mockup/brand';

type VerificationController = Pick<ReturnType<typeof usePerfilTecnico>, 'verification' | 'requestVerification' | 'confirmVerification'>;

function remainingTime(seconds: number) {
  return `${Math.floor(seconds / 60)}:${String(seconds % 60).padStart(2, '0')}`;
}

export function EmailVerification({ verification, requestVerification, confirmVerification }: VerificationController) {
  const [code, setCode] = useState('');
  const [now, setNow] = useState(Date.now);
  const codeInput = useRef<HTMLInputElement>(null);
  const status = verification.data;
  const elapsed = Math.max(0, Math.floor((now - verification.dataUpdatedAt) / 1000));
  const resendRemaining = Math.max(0, (status?.resendInSeconds ?? 0) - elapsed);
  const expiresRemaining = status?.expiresInSeconds == null ? null : Math.max(0, status.expiresInSeconds - elapsed);
  const pending = requestVerification.isPending || confirmVerification.isPending;
  const requestError = requestVerification.error instanceof Error ? requestVerification.error.message : '';
  const confirmError = confirmVerification.error instanceof Error ? confirmVerification.error.message : '';

  useEffect(() => {
    setNow(Date.now());
    if (!status || status.verified) return;
    const lifetime = Math.max(status.resendInSeconds, status.expiresInSeconds ?? 0);
    if (lifetime <= 0) return;
    const deadline = verification.dataUpdatedAt + lifetime * 1000;
    const timer = window.setInterval(() => {
      const current = Date.now();
      setNow(current);
      if (current >= deadline) window.clearInterval(timer);
    }, 1000);
    return () => window.clearInterval(timer);
  }, [verification.dataUpdatedAt, status]);

  function requestCode() {
    confirmVerification.reset();
    requestVerification.mutate(undefined, {
      onSuccess: () => {
        setCode('');
        window.setTimeout(() => codeInput.current?.focus(), 0);
      }
    });
  }

  function confirmCode(event: FormEvent) {
    event.preventDefault();
    if (!/^\d{6}$/.test(code) || pending || !expiresRemaining) return;
    requestVerification.reset();
    confirmVerification.mutate(code, { onSuccess: () => setCode('') });
  }

  return <section className="technical-email-verification" id="verificacion-correo" aria-labelledby="email-verification-title" data-verified={status?.verified ? 'true' : 'false'}>
    <div className="technical-email-verification__heading">
      <Icon name={status?.verified ? 'check' : 'mail'} size={20} />
      <h2 id="email-verification-title">{status?.verified ? 'Correo verificado' : 'Verificá tu correo para conectar una clave'}</h2>
    </div>
    {verification.isLoading && <p role="status">Comprobando la verificación de tu correo…</p>}
    {verification.isError && <div className="technical-email-verification__error"><Notice key={verification.errorUpdatedAt} className="bloq-error" role="alert">{verification.error instanceof Error ? verification.error.message : 'No pudimos comprobar tu correo. Volvé a intentarlo.'}</Notice><button type="button" onClick={() => void verification.refetch()} disabled={verification.isFetching}>Volver a comprobar</button></div>}
    {status && (status.verified ? <p role="status"><strong className="technical-email-address">{status.email}</strong> ya está verificado. Podés guardar o cambiar tus claves personales.</p> : <>
      <p>{expiresRemaining !== null ? 'Enviamos un código a ' : 'Enviaremos un código a '}<strong className="technical-email-address">{status.email}</strong> para confirmar que el correo es tuyo. Los tokens del proyecto siguen disponibles.</p>
      <div className="technical-email-verification__actions">
        <button type="button" onClick={requestCode} disabled={pending || resendRemaining > 0}>
          {requestVerification.isPending ? 'Enviando código…' : expiresRemaining !== null ? 'Reenviar código' : 'Enviar código'}
        </button>
        {resendRemaining > 0 && <small>Podés reenviarlo en {resendRemaining} s.</small>}
      </div>
      {expiresRemaining !== null && <form className="technical-email-code" onSubmit={confirmCode}>
        <label htmlFor="email-verification-code">Código de 6 dígitos</label>
        <div className="technical-email-code__controls">
          <input id="email-verification-code" ref={codeInput} value={code} onChange={(event) => setCode(event.target.value.replace(/\D/g, '').slice(0, 6))} type="text" inputMode="numeric" autoComplete="one-time-code" pattern="[0-9]{6}" maxLength={6} placeholder="000000" required disabled={pending || expiresRemaining === 0} aria-describedby={`email-verification-help${confirmError ? ' email-verification-error' : ''}`} aria-invalid={Boolean(confirmError)} />
          <button type="submit" data-primary="true" disabled={pending || !/^\d{6}$/.test(code) || expiresRemaining === 0}>{confirmVerification.isPending ? 'Verificando…' : 'Verificar correo'}</button>
        </div>
        <small id="email-verification-help">{expiresRemaining > 0 ? <>Ingresá el código recibido. Vence en <span className="technical-email-countdown">{remainingTime(expiresRemaining)}</span>. Revisá también el correo no deseado.</> : 'El código venció. Pedí uno nuevo para continuar.'}</small>
      </form>}
      {confirmError && <Notice key={confirmVerification.submittedAt} id="email-verification-error" className="bloq-error" role="alert">{confirmError}</Notice>}
      {requestError && <Notice key={requestVerification.submittedAt} className="bloq-error" role="alert">{requestError}</Notice>}
    </>)}
  </section>;
}
