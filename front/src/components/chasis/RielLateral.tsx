import { getCurrentJwtStatus } from '../../app/routeGuard';

const publicDestinations = [
  { href: '/', label: 'Inicio', icon: 'home' },
  { href: '/login', label: 'Iniciar sesión', icon: 'access' }
];

const privateDestinations = [
  { href: '/', label: 'Inicio', icon: 'home' },
  { href: '/nuevo-chat', label: 'Chat', icon: 'chat' },
  { href: '/perfil-tecnico', label: 'Configuración técnica', icon: 'settings' }
];

function Icon({ name }: { name: string }) {
  if (name === 'chat') return <svg viewBox="0 0 20 20" aria-hidden="true"><path d="M3 3h14v11H8l-5 3V3Z" /><line x1="6" y1="7" x2="14" y2="7" /><line x1="6" y1="10" x2="11" y2="10" /></svg>;
  if (name === 'home') return <svg viewBox="0 0 20 20" aria-hidden="true"><rect x="3" y="3" width="14" height="14" /><line x1="6" y1="8" x2="14" y2="8" /><line x1="6" y1="11" x2="14" y2="11" /><line x1="6" y1="14" x2="11" y2="14" /></svg>;
  if (name === 'profile') return <svg viewBox="0 0 20 20" aria-hidden="true"><rect x="7" y="3" width="6" height="6" /><path d="M3 17 5 11h10l2 6" /></svg>;
  if (name === 'settings') return <svg viewBox="0 0 20 20" aria-hidden="true"><rect x="4" y="4" width="12" height="12" /><line x1="7" y1="8" x2="13" y2="8" /><line x1="7" y1="12" x2="13" y2="12" /></svg>;
  return <svg viewBox="0 0 20 20" aria-hidden="true"><rect x="4" y="3" width="12" height="14" /><line x1="7" y1="10" x2="16" y2="10" /><path d="m12 7 3 3-3 3" /></svg>;
}

export function RielLateral({ activePath, onUsage, onLogout }: { activePath: string; onUsage: () => void; onLogout: () => void }) {
  const isAuthenticated = getCurrentJwtStatus() === 'valid';
  const destinations = isAuthenticated ? privateDestinations : publicDestinations;

  return (
    <aside className="bloq-rail" aria-label="Navegacion principal">
      <a className="bloq-brand" href="/" aria-label="BloqIA, inicio">
        <svg viewBox="0 0 24 24" aria-hidden="true"><rect x="2" y="2" width="12" height="9" /><rect x="9" y="13" width="13" height="9" /></svg>
      </a>
      <nav className="bloq-nav">
        {destinations.map((destination) => (
          <a key={destination.href} href={destination.href} data-active={activePath === destination.href} aria-label={destination.label} title={destination.label}>
            <Icon name={destination.icon} />
          </a>
        ))}
      </nav>
      <div className="bloq-rail-footer">
        {isAuthenticated && <button className="bloq-usage-button" type="button" onClick={onUsage} aria-label="Ver estadísticas de uso">Uso</button>}
        {isAuthenticated && <a className="bloq-avatar-wrap" href="/perfil" aria-label="Ver perfil">
          <span className="bloq-avatar" aria-hidden="true">B</span>
          <span className="bloq-session-dot" aria-hidden="true" />
        </a>}
        {isAuthenticated && <button className="bloq-logout-button" type="button" onClick={onLogout}>Cerrar sesión</button>}
      </div>
    </aside>
  );
}
