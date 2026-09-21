import { FormEvent, useState } from 'react';
import { ChasisBloqIA } from '../components/chasis/ChasisBloqIA';
import { useRegister } from '../features/usuario/useRegister';

function strongPasswordHint(password: string) {
  const valid = password.length >= 10 && /[A-Za-z]/.test(password) && /\d/.test(password) && /[^A-Za-z0-9]/.test(password);
  return valid ? 'Contrasenia segura' : 'Minimo 10 caracteres, una letra, un numero y un simbolo';
}

export function Register() {
  const [mail, setMail] = useState('');
  const [password, setPassword] = useState('');
  const [age, setAge] = useState(18);
  const [profession, setProfession] = useState('');
  const register = useRegister();

  function submit(event: FormEvent) {
    event.preventDefault();
    register.mutate({ mail, password, age, profession });
  }

  return (
    <ChasisBloqIA title="Registro" activePath="/login">
      <section className="auth-intro">
        <h1>Crear cuenta</h1>
        <p className="bloq-reading">Completá estos datos para definir tu espacio de estudio o trabajo.</p>
      </section>
      <form className="bloq-form" onSubmit={submit}>
        <label>Correo electrónico<input type="email" value={mail} onChange={(event) => setMail(event.target.value)} required /></label>
        <label>Contraseña<input type="password" value={password} onChange={(event) => setPassword(event.target.value)} required /></label>
        <small>{strongPasswordHint(password)}</small>
        <label>Edad<input type="number" min={1} value={age} onChange={(event) => setAge(Number(event.target.value))} required /></label>
        <label>Profesión<input value={profession} onChange={(event) => setProfession(event.target.value)} required /></label>
        <div className="bloq-actions">
          <button type="submit" data-primary="true">Crear cuenta</button>
        </div>
      </form>
      {register.isError && <p className="bloq-error">No se pudo crear la cuenta. Revisá correo, contraseña, edad y profesión.</p>}
      {register.data && <p className="bloq-success">Cuenta creada para {register.data.user.mail}</p>}
      <p className="auth-secondary"><span>¿Ya tenés cuenta?</span><a href="/login">Iniciar sesión</a></p>
    </ChasisBloqIA>
  );
}
