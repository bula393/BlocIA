import { Notice } from '../components/Notice';
import { FormEvent, useState } from 'react';
import { ProfessionField } from '../components/auth/ProfessionField';
import { AuthLayout } from '../components/auth/AuthLayout';
import { PasswordField } from '../components/auth/PasswordField';
import { useMobileViewport } from '../components/mobile/useMobileViewport';
import { Icon } from '../mockup/brand';
import { useRegister } from '../features/usuario/useRegister';
import { startGoogleLogin } from '../api/auth';
import { authErrorMessage } from '../components/auth/authErrorMessage';

function strongPasswordHint(password: string) {
  const valid = password.length >= 10 && /[A-Za-z]/.test(password) && /\d/.test(password) && /[^A-Za-z0-9]/.test(password);
  return valid ? 'Contraseña segura' : 'Mínimo 10 caracteres, una letra, un número y un símbolo';
}

export function Register() {
  const mobile = useMobileViewport();
  const [mail, setMail] = useState('');
  const [password, setPassword] = useState('');
  const [age, setAge] = useState(18);
  const [profession, setProfession] = useState('');
  const register = useRegister();

  function submit(event: FormEvent) {
    event.preventDefault();
    register.mutate({ mail, password, age, profession });
  }

  return <AuthLayout>
    <section className="auth-intro">
      <p className="provider-eyebrow">EMPEZÁ POR UNA PREGUNTA</p>
      <h1>Crear cuenta</h1>
      <p>Un perfil breve ayuda a dar contexto a tus conversaciones.</p>
    </section>
    <button className="auth-google-button" type="button" onClick={startGoogleLogin}><span className="auth-google-mark" aria-hidden="true">G</span>Registrarme con Google<Icon name="arrow-up-right" size={16} /></button>
    <div className="auth-divider"><span>{mobile ? 'o registrate con' : 'o con tu correo'}</span></div>
    <form className="bloq-form auth-form" onSubmit={submit}>
      <label>Correo electrónico<input autoComplete="email" type="email" value={mail} onChange={(event) => setMail(event.target.value)} required /></label>
      <PasswordField value={password} onChange={setPassword} autoComplete="new-password" />
      <small className="auth-password-hint" data-valid={password.length >= 10 && /[A-Za-z]/.test(password) && /\d/.test(password) && /[^A-Za-z0-9]/.test(password)}>{strongPasswordHint(password)}</small>
      <div className="auth-field-pair">
        <label>Edad<input type="number" min={1} value={age} onChange={(event) => setAge(Number(event.target.value))} required /></label>
        <ProfessionField value={profession} onChange={setProfession} required />
      </div>
      <button type="submit" data-primary="true" disabled={register.isPending}>{register.isPending ? 'Creando cuenta…' : 'Crear cuenta'}<Icon name="arrow" size={17} /></button>
    </form>
    {register.isError && <Notice key={register.submittedAt} className="bloq-error auth-feedback" role="alert">{authErrorMessage(register.error, 'register')}</Notice>}
    {register.data && <Notice key={register.submittedAt} className="bloq-success auth-feedback" role="status">Cuenta creada para {register.data.user.mail}</Notice>}
    <p className="auth-secondary"><span>¿Ya tenés cuenta?</span><a href="/login">Iniciar sesión</a></p>
  </AuthLayout>;
}
