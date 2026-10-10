import { Notice } from '../components/Notice';
import { ChasisBloqIA } from '../components/chasis/ChasisBloqIA';
import { usePerfil } from '../features/usuario/usePerfil';
import { logout } from '../api/auth';
import { navigateTo } from '../app/navigation';
import { Icon } from '../mockup/brand';

export function Cuenta() {
  const { profile } = usePerfil();
  const name = profile.data?.displayName || profile.data?.mail.split('@')[0];

  async function signOut() {
    await logout();
    navigateTo('/', true);
  }

  return <ChasisBloqIA title="Tu cuenta" activePath="/cuenta" contentClassName="account-content">
    <div className="mobile-account-page">
      <h1>Tu espacio,<br />a tu manera.</h1>
      {profile.isLoading && <p role="status">Cargando tu cuenta…</p>}
      {profile.isError && <Notice key={profile.errorUpdatedAt} className="bloq-error" role="alert">No pudimos cargar tu cuenta. <button type="button" className="profile-retry" onClick={() => void profile.refetch()}>Reintentar</button></Notice>}
      {profile.data && <div className="mobile-account-person"><span className="profile-initial" aria-hidden="true">{name?.charAt(0).toUpperCase()}</span><div><strong>{name}</strong><small>{profile.data.mail}</small></div></div>}
      <nav className="mobile-account-links" aria-label="Opciones de tu cuenta">
        {[['/perfil', 'profile', 'Tu perfil', 'Tus datos y contexto personal'], ['/perfil-tecnico', 'settings', 'Proveedores y modelos', 'Conexiones y modelos disponibles'], ['/actividad', 'activity', 'Tu actividad', 'Consultas, movimientos y límites'], ['/', 'home', 'Portada pública', 'Volver al inicio del sitio']].map(([href, icon, title, detail]) => <a href={href} key={href}><span className="mobile-account-icon"><Icon name={icon} /></span><span><strong>{title}</strong><small>{detail}</small></span><Icon name="chevron" size={17} /></a>)}
      </nav>
      <div className="mobile-account-principle"><p>Las buenas preguntas abren posibilidades.</p><small>Las decisiones personales son tuyas.</small></div>
      <button className="mobile-account-logout" type="button" onClick={() => void signOut()}><Icon name="logout" size={20} />Cerrar sesión</button>
    </div>
  </ChasisBloqIA>;
}
