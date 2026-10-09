import { FormEvent, useEffect, useRef, useState } from 'react';
import { completeGoogleRegistration, consumeGoogleSession } from '../api/auth';
import { AuthLayout } from '../components/auth/AuthLayout';
import { navigateTo } from '../app/navigation';

type PendingRegistration = {
  registrationToken: string;
  missingFields: string[];
  prefilledFields: Record<string, unknown>;
};

export function GoogleCallback() {
  const [pending, setPending] = useState<PendingRegistration | null>(null);
  const [error, setError] = useState('');
  const [age, setAge] = useState(18);
  const [profession, setProfession] = useState('');
  const [loading, setLoading] = useState(true);
  const [pendingSubmit, setPendingSubmit] = useState(false);
  const hasLoaded = useRef(false);
  const submitInFlight = useRef(false);

  useEffect(() => {
    if (hasLoaded.current) return;
    hasLoaded.current = true;
    const params = new URLSearchParams(window.location.search);
    const callbackError = params.get('error');
    if (callbackError) {
      setError(callbackError === 'configuration'
        ? 'El acceso con Google todavía no está configurado. Ingresá con tu correo y contraseña o consultá al administrador.'
        : callbackError === 'state'
          ? 'La solicitud de acceso con Google venció. Volvé al acceso e intentá nuevamente.'
          : 'Google no pudo completar el acceso. Intentá nuevamente.');
      setLoading(false);
      return;
    }
    consumeGoogleSession()
      .then((result) => {
        if ('accessToken' in result) {
          navigateTo('/', true);
          return;
        }
        setPending(result);
      })
      .catch(() => setError('No se pudo recuperar la sesión de Google. Intentá nuevamente.'))
      .finally(() => setLoading(false));
  }, []);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!pending || submitInFlight.current) return;
    submitInFlight.current = true;
    setPendingSubmit(true);
    setError('');
    try {
      await completeGoogleRegistration(pending.registrationToken, age, profession);
      navigateTo('/', true);
    } catch {
      setError('No se pudieron completar tus datos. Revisalos e intentá de nuevo.');
    } finally {
      submitInFlight.current = false;
      setPendingSubmit(false);
    }
  }

  return (
    <AuthLayout>
      <section className="auth-intro">
        <p className="provider-eyebrow">ACCESO CON GOOGLE</p>
        <h1>{pending ? 'Completá tu perfil' : error ? 'No se pudo completar el acceso' : 'Conectando con Google'}</h1>
        {loading && <p className="bloq-reading">Estamos verificando tu cuenta.</p>}
        {error && !pending && <><p className="bloq-error" role="alert">{error}</p><a className="bloq-button" data-primary="true" href="/login">Volver al acceso</a></>}
      </section>
      {pending && (
        <form className="bloq-form auth-form" onSubmit={submit} aria-busy={pendingSubmit}>
          <p className="bloq-status-line">Usaremos {String(pending.prefilledFields.mail ?? 'tu correo de Google')} para esta cuenta.</p>
          {pending.missingFields.includes('age') && <label>Edad<input type="number" min={1} value={age} onChange={(event) => setAge(Number(event.target.value))} required disabled={pendingSubmit} /></label>}
          {pending.missingFields.includes('profession') && <label>Profesión<input value={profession} onChange={(event) => setProfession(event.target.value)} required disabled={pendingSubmit} /></label>}
          {error && <p className="bloq-error" role="alert">{error}</p>}
          <button type="submit" data-primary="true" disabled={pendingSubmit}>{pendingSubmit ? 'Completando perfil…' : 'Completar perfil'}</button>
        </form>
      )}
    </AuthLayout>
  );
}
