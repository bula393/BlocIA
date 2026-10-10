import { Notice } from '../components/Notice';
import { FormEvent, useEffect, useState } from 'react';
import { AuthLayout } from '../components/auth/AuthLayout';
import { PasswordField } from '../components/auth/PasswordField';
import { useMobileViewport } from '../components/mobile/useMobileViewport';
import { Icon } from '../mockup/brand';
import { useLogin } from '../features/usuario/useLogin';
import { startGoogleLogin } from '../api/auth';
import { navigateTo } from '../app/navigation';
import { authErrorMessage } from '../components/auth/authErrorMessage';

export function Login() {
  const mobile = useMobileViewport();
  const [mail, setMail] = useState('');
  const [password, setPassword] = useState('');
  const login = useLogin();

  useEffect(() => {
    if (login.data) navigateTo('/', true);
  }, [login.data]);

  function submit(event: FormEvent) {
    event.preventDefault();
    login.mutate({ mail, password });
  }

  return <AuthLayout>
    <section className="auth-intro">
      <p className="provider-eyebrow">VOLVÉ A TU ESPACIO</p>
      <h1>Iniciar sesión</h1>
      <p>Recuperá tus conversaciones, tu perfil y tus herramientas.</p>
    </section>
    <button className="auth-google-button" type="button" onClick={startGoogleLogin}><span className="auth-google-mark" aria-hidden="true">G</span>Continuar con Google<Icon name="arrow-up-right" size={16} /></button>
    <div className="auth-divider"><span>{mobile ? 'o continuá con' : 'o con correo electrónico'}</span></div>
    <form className="bloq-form auth-form" onSubmit={submit}>
      <label>Correo electrónico<input autoComplete="email" value={mail} onChange={(event) => setMail(event.target.value)} type="email" required /></label>
      <PasswordField value={password} onChange={setPassword} autoComplete="current-password" />
      <button type="submit" data-primary="true" disabled={login.isPending}>{login.isPending ? 'Ingresando…' : 'Iniciar sesión'}<Icon name="arrow" size={17} /></button>
    </form>
    {login.isError && <Notice key={login.submittedAt} className="bloq-error auth-feedback" role="alert">{authErrorMessage(login.error, 'login')}</Notice>}
    {login.data && <Notice key={login.submittedAt} className="bloq-success auth-feedback" role="status">Sesión iniciada para {login.data.user.mail}</Notice>}
    <p className="auth-secondary"><span>¿Todavía no tenés cuenta?</span><a href="/register">Crear cuenta</a></p>
  </AuthLayout>;
}
