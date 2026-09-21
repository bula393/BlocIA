import { FormEvent, useEffect, useRef, useState } from 'react';
import { completeGoogleRegistration, consumeGoogleSession } from '../api/auth';
import { ChasisBloqIA } from '../components/chasis/ChasisBloqIA';
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
  const hasLoaded = useRef(false);

  useEffect(() => {
    if (hasLoaded.current) return;
    hasLoaded.current = true;
    const params = new URLSearchParams(window.location.search);
    if (params.get('error')) {
      setError('Google no pudo completar el acceso. Intentá nuevamente.');
      setLoading(false);
      return;
    }
    consumeGoogleSession()
      .then((result) => {
        if ('accessToken' in result) {
          navigateTo('/perfil', true);
          return;
        }
        setPending(result);
      })
      .catch(() => setError('No se pudo recuperar la sesión de Google. Intentá nuevamente.'))
      .finally(() => setLoading(false));
  }, []);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!pending) return;
    try {
      await completeGoogleRegistration(pending.registrationToken, age, profession);
      navigateTo('/perfil', true);
    } catch {
      setError('No se pudieron completar tus datos. Revisalos e intentá de nuevo.');
    }
  }

  return (
    <ChasisBloqIA title="Acceso con Google" activePath="/login">
      <section className="auth-intro">
        <h1>{pending ? 'Completá tu perfil' : 'Conectando con Google'}</h1>
        {loading && <p className="bloq-reading">Estamos verificando tu cuenta.</p>}
        {error && <><p className="bloq-error">{error}</p><a className="bloq-button" data-primary="true" href="/login">Volver al acceso</a></>}
      </section>
      {pending && !error && (
        <form className="bloq-form" onSubmit={submit}>
          <p className="bloq-status-line">Usaremos {String(pending.prefilledFields.mail ?? 'tu correo de Google')} para esta cuenta.</p>
          {pending.missingFields.includes('age') && <label>Edad<input type="number" min={1} value={age} onChange={(event) => setAge(Number(event.target.value))} required /></label>}
          {pending.missingFields.includes('profession') && <label>Profesión<input value={profession} onChange={(event) => setProfession(event.target.value)} required /></label>}
          <div className="bloq-actions"><button type="submit" data-primary="true">Completar perfil</button></div>
        </form>
      )}
    </ChasisBloqIA>
  );
}
