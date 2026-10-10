import { Notice } from '../components/Notice';
import { FormEvent, useEffect, useState } from 'react';
import { ProfessionField } from '../components/auth/ProfessionField';
import { ChasisBloqIA } from '../components/chasis/ChasisBloqIA';
import { CajonPerfil } from '../components/overlay/CajonPerfil';
import { usePerfil } from '../features/usuario/usePerfil';
import { logout } from '../api/auth';
import { navigateTo } from '../app/navigation';
import { Icon } from '../mockup/brand';
import type { LoginProviderStatus, TechnicalProfileStatus } from '../types/dominio';

const accessLabels: Record<LoginProviderStatus, string> = {
  password: 'Correo y contraseña',
  google: 'Cuenta de Google',
  'password-and-google': 'Correo y Google'
};

const technicalLabels: Record<TechnicalProfileStatus, string> = {
  'not-configured': 'Sin configurar',
  'partially-configured': 'Configuración parcial',
  configured: 'Configurado',
  'requires-attention': 'Requiere atención'
};

export function Perfil() {
  const { profile, update } = usePerfil();
  const [age, setAge] = useState('');
  const [profession, setProfession] = useState('');
  const [displayName, setDisplayName] = useState('');

  useEffect(() => {
    if (!profile.data) return;
    setAge(String(profile.data.age));
    setProfession(profile.data.profession);
    setDisplayName(profile.data.displayName ?? '');
  }, [profile.data]);

  const changed = !!profile.data && (
    age !== String(profile.data.age)
    || profession !== profile.data.profession
    || displayName !== (profile.data.displayName ?? '')
  );

  function submit(event: FormEvent) {
    event.preventDefault();
    if (!profile.data || !changed || update.isPending) return;
    update.mutate({ age: Number(age), profession, displayName: displayName.trim() });
  }

  async function signOut() {
    await logout();
    navigateTo('/', true);
  }

  return (
    <ChasisBloqIA title="Perfil" activePath="/perfil" contentClassName="profile-content">
      <div className="profile-page">
        <header className="profile-header">
          <div>
            <p className="profile-kicker">Tu espacio de BloqIA</p>
            <h1>Perfil</h1>
            <p className="bloq-reading">Mantené tus datos al día para recibir explicaciones ajustadas a tu contexto.</p>
          </div>
          {profile.data && <span className="profile-initial" aria-label={`Perfil de ${(profile.data.displayName || profile.data.mail).charAt(0).toUpperCase()}`}>
            {(profile.data.displayName || profile.data.mail).charAt(0).toUpperCase()}
          </span>}
        </header>

        {profile.isLoading && <p className="profile-loading" role="status">Cargando perfil…</p>}
        {profile.isError && <Notice key={profile.errorUpdatedAt} className="bloq-error" role="alert">No se pudo cargar el perfil. <button type="button" className="profile-retry" onClick={() => void profile.refetch()}>Reintentar</button></Notice>}

        <div className="profile-layout">
          <section className="profile-edit" aria-labelledby="profile-edit-title">
            <div className="profile-section-heading">
              <div>
                <h2 id="profile-edit-title">Información personal</h2>
                <p>Elegí cómo querés que BloqIA adapte sus respuestas.</p>
              </div>
            </div>
            <form className="bloq-form profile-form" onSubmit={submit}>
              <label>Nombre visible
                <input autoComplete="nickname" value={displayName} onChange={(event) => setDisplayName(event.target.value)} placeholder="¿Cómo querés que te llamemos?" maxLength={80} disabled={!profile.data || update.isPending} />
              </label>
              <div className="profile-field-pair">
                <ProfessionField value={profession} onChange={setProfession} required disabled={!profile.data || update.isPending} />
                <label>Edad
                  <input type="number" min={1} value={age} onChange={(event) => setAge(event.target.value)} required disabled={!profile.data || update.isPending} />
                </label>
              </div>
              <p className="profile-form-note">Usamos tu nombre, edad y profesión para contextualizar las respuestas del chat cuando correspondan.</p>
              <div className="bloq-actions profile-actions">
                <button type="submit" data-primary="true" disabled={!changed || update.isPending}>{update.isPending ? 'Guardando…' : 'Guardar cambios'}</button>
              </div>
              {update.isError && <Notice key={update.submittedAt} className="bloq-error" role="alert">No se guardaron los cambios. Revisá los datos e intentá de nuevo.</Notice>}
              {update.isSuccess && !changed && <Notice key={update.submittedAt} className="bloq-success" role="status">Perfil actualizado.</Notice>}
            </form>
          </section>

          <CajonPerfil>
            <div className="profile-section-heading profile-section-heading--summary">
              <div>
                <h2>Datos de tu cuenta</h2>
                <p>Información vinculada a tu acceso.</p>
              </div>
            </div>
            {profile.data ? <>
              <dl className="profile-details">
                <div><dt>Correo electrónico</dt><dd>{profile.data.mail}</dd></div>
                <div><dt>Método de acceso</dt><dd>{accessLabels[profile.data.loginProviderStatus]}</dd></div>
                <div><dt>Perfil técnico</dt><dd>{technicalLabels[profile.data.technicalProfileStatus]}</dd></div>
              </dl>
              <a className="profile-technical-link" href="/perfil-tecnico"><span>Administrar modelos y proveedores</span><Icon name="arrow-up-right" size={17} /></a>
              <button className="profile-logout" type="button" onClick={() => void signOut()}>Cerrar sesión</button>
            </> : <p className="profile-summary-placeholder">Los datos de tu cuenta aparecerán acá.</p>}
          </CajonPerfil>
        </div>
      </div>
    </ChasisBloqIA>
  );
}
