import { FormEvent, useEffect, useState } from 'react';
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
          <button type="submit" data-primary="true">Iniciar sesión</button>
        </div>
      </form>
      {login.isError && <p className="bloq-error">No se pudo iniciar sesión. Revisá tus datos e intentá de nuevo.</p>}
      {login.data && <p className="bloq-success">Sesión iniciada para {login.data.user.mail}</p>}
      <p className="auth-secondary"><span>¿Todavía no tenés cuenta?</span><a href="/register">Crear cuenta</a></p>
    </ChasisBloqIA>
  );
}
