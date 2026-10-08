import { useState } from 'react';
import { getCurrentJwtStatus } from '../../app/routeGuard';
import { Brand, Icon } from '../../mockup/brand';

type Destination = { href: string; label: string; icon: string };

const publicDestinations: Destination[] = [
  { href: '/', label: 'Inicio', icon: 'home' },
  { href: '/login', label: 'Iniciar sesión', icon: 'user' },
  { href: '/register', label: 'Crear cuenta', icon: 'plus' }
];

const conversationDestinations: Destination[] = [
  { href: '/nuevo-chat', label: 'Chat', icon: 'chat' }
];

const accountDestinations: Destination[] = [
  { href: '/perfil', label: 'Perfil', icon: 'profile' },
  { href: '/perfil-tecnico', label: 'Proveedores y modelos', icon: 'settings' },
  { href: '/actividad', label: 'Actividad', icon: 'usage' }
];

function destinationIsActive(destination: Destination, activePath: string) {
  return activePath === destination.href;
}

function DestinationList({ destinations, activePath, close }: { destinations: Destination[]; activePath: string; close: () => void }) {
  return <nav className="bloq-nav">
    {destinations.map((destination) => {
      const active = destinationIsActive(destination, activePath);
      return <a key={destination.href} href={destination.href} title={destination.label} data-active={active} aria-current={active ? 'page' : undefined} onClick={close}>
        <Icon name={destination.icon} size={18} />
        <span>{destination.label}</span>
      </a>;
    })}
  </nav>;
}

export function RielLateral({ activePath, title, collapsed, chatLocked = false, onToggleCollapse, onLogout }: { activePath: string; title: string; collapsed: boolean; chatLocked?: boolean; onToggleCollapse: () => void; onLogout: () => void }) {
  const isAuthenticated = getCurrentJwtStatus() === 'valid';
  const [menuOpen, setMenuOpen] = useState(false);
  const closeMenu = () => setMenuOpen(false);

  return <>
    <header className="bloq-mobilebar">
      <button className="bloq-menu-button" type="button" onClick={() => setMenuOpen((open) => !open)} aria-expanded={menuOpen} aria-label={menuOpen ? 'Cerrar navegación' : 'Abrir navegación'}><Icon name={menuOpen ? 'close' : 'menu'} /></button>
      <a href="/" aria-label="BloqIA, inicio"><Brand /></a>
      <span className="bloq-mobile-title">{title}</span>
    </header>
    <button className="bloq-sidebar-backdrop" type="button" aria-label="Cerrar navegación" aria-hidden={!menuOpen} tabIndex={menuOpen ? 0 : -1} onClick={closeMenu} data-open={menuOpen} />
    <aside className="bloq-rail" aria-label="Navegación principal" data-open={menuOpen}>
      <div className="bloq-sidebar-head">
        <div className="bloq-sidebar-brand-group">
          <a className="bloq-sidebar-brand" href="/" aria-label="BloqIA, inicio" title="BloqIA, inicio"><Brand /></a>
          {chatLocked && <span className="bloq-chat-lock" role="img" aria-label="Chat bloqueado" title="Chat bloqueado"><Icon name="lock" size={14} /></span>}
        </div>
        <button className="bloq-sidebar-collapse" type="button" onClick={onToggleCollapse} aria-label={collapsed ? 'Expandir menú' : 'Compactar menú'} aria-expanded={!collapsed} title={collapsed ? 'Expandir menú' : 'Compactar menú'} data-collapsed={collapsed}>
          <Icon name="chevron" size={17} />
        </button>
        <button className="bloq-sidebar-close" type="button" aria-label="Cerrar navegación" onClick={closeMenu}><Icon name="close" /></button>
      </div>
      {isAuthenticated ? <>
        <p className="bloq-nav-caption">CONVERSACIONES</p>
        <DestinationList destinations={conversationDestinations} activePath={activePath} close={closeMenu} />
        <p className="bloq-nav-caption bloq-nav-caption--account">TU ESPACIO</p>
        <DestinationList destinations={accountDestinations} activePath={activePath} close={closeMenu} />
      </> : <DestinationList destinations={publicDestinations} activePath={activePath} close={closeMenu} />}
      <div className="bloq-rail-footer">
        {isAuthenticated && <a className="bloq-account-link" href="/perfil" title="Tu cuenta" onClick={closeMenu}><span className="bloq-avatar" aria-hidden="true">B</span><span className="bloq-account-label"><strong>Tu cuenta</strong><small>Perfil y preferencias</small></span><Icon name="chevron" size={16} /></a>}
        {isAuthenticated && <button className="bloq-logout-button" type="button" title="Cerrar sesión" onClick={onLogout}><Icon name="logout" size={16} /><span>Cerrar sesión</span></button>}
        {!isAuthenticated && <p className="bloq-sidebar-note">Una pregunta puede abrir otra perspectiva.</p>}
      </div>
    </aside>
  </>;
}
