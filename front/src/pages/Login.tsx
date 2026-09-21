import { FormEvent, useEffect, useState } from 'react';
import { startGoogleLogin } from '../api/auth';
import { ChasisBloqIA } from '../components/chasis/ChasisBloqIA';
import { useLogin } from '../features/usuario/useLogin';
import { navigateTo } from '../app/navigation';

export function Login() {
  const [mail, setMail] = useState('');
  const [password, setPassword] = useState('');
  const login = useLogin();

  useEffect(() => {
    if (login.data) navigateTo('/perfil', true);
  }, [login.data]);

  function submit(event: FormEvent) {
    event.preventDefault();
    login.mutate({ mail, password });
  }

  return (
    <ChasisBloqIA title="Acceso" activePath="/login">
      <section className="auth-intro">
        <h1>Iniciar sesión</h1>
        <p className="bloq-reading">Usá tu cuenta para recuperar tu perfil y tus herramientas.</p>
      </section>
      <form className="bloq-form" onSubmit={submit}>
        <label>
          Correo electrónico
          <input value={mail} onChange={(event) => setMail(event.target.value)} type="email" required />
        </label>
        <label>
          Contraseña
          <input value={password} onChange={(event) => setPassword(event.target.value)} type="password" required />
        </label>
        <div className="bloq-actions">
          <button type="button" className="google-button" onClick={startGoogleLogin}>
            <svg className="google-mark" viewBox="0 0 18 18" aria-hidden="true">
              <path fill="#EA4335" d="M17.64 9.205c0-.638-.057-1.252-.164-1.841H9v3.483h4.844a4.14 4.14 0 0 1-1.797 2.716v2.258h2.91c1.704-1.57 2.683-3.88 2.683-6.616Z" />
              <path fill="#4285F4" d="M9 18c2.43 0 4.467-.806 5.957-2.179l-2.91-2.258c-.806.54-1.837.86-3.047.86-2.343 0-4.326-1.582-5.035-3.708H.956v2.332A9 9 0 0 0 9 18Z" />
              <path fill="#FBBC05" d="M3.965 10.715A5.41 5.41 0 0 1 3.683 9c0-.595.102-1.174.282-1.715V4.953H.956A9 9 0 0 0 0 9c0 1.452.348 2.827.956 4.047l3.009-2.332Z" />
              <path fill="#34A853" d="M9 3.578c1.321 0 2.508.454 3.442 1.345l2.582-2.582C13.463.891 11.425 0 9 0A9 9 0 0 0 .956 4.953l3.009 2.332C4.674 5.16 6.657 3.578 9 3.578Z" />
            </svg>
            Continuar con Google
          </button>
          <button type="submit" data-primary="true">Iniciar sesión</button>
        </div>
      </form>
      {login.isError && <p className="bloq-error">No se pudo iniciar sesión. Revisá tus datos e intentá de nuevo.</p>}
      {login.data && <p className="bloq-success">Sesión iniciada para {login.data.user.mail}</p>}
      <p className="auth-secondary"><span>¿Todavía no tenés cuenta?</span><a href="/register">Crear cuenta</a></p>
    </ChasisBloqIA>
  );
}
