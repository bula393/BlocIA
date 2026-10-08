import { useState, type ReactNode } from 'react';
import { RielLateral } from './RielLateral';
import { getCurrentJwtStatus } from '../../app/routeGuard';
import { logout } from '../../api/auth';
import { navigateTo } from '../../app/navigation';
import { Icon } from '../../mockup/brand';

const SIDEBAR_PREFERENCE_KEY = 'bloq-sidebar-collapsed';

function readSidebarPreference(): boolean | null {
  try {
    const value = window.localStorage.getItem(SIDEBAR_PREFERENCE_KEY);
    return value === null ? null : value === 'true';
  } catch {
    return null;
  }
}

function saveSidebarPreference(collapsed: boolean) {
  try {
    window.localStorage.setItem(SIDEBAR_PREFERENCE_KEY, String(collapsed));
  } catch {
    // The menu still works for this page when browser storage is unavailable.
  }
}

export function ChasisBloqIA({ title, children, activePath = window.location.pathname, contentClassName, chatLocked = false }: { title: string; children: ReactNode; activePath?: string; contentClassName?: string; chatLocked?: boolean }) {
  const isAuthenticated = getCurrentJwtStatus() === 'valid';
  const [sidebarCollapsed, setSidebarCollapsed] = useState(() => readSidebarPreference() ?? activePath === '/nuevo-chat');

  function toggleSidebar() {
    const next = !sidebarCollapsed;
    saveSidebarPreference(next);
    setSidebarCollapsed(next);
  }

  async function handleLogout() {
    await logout();
    navigateTo('/', true);
  }

  return <div className="bloq-shell" data-chat={activePath === '/nuevo-chat'} data-chat-locked={activePath === '/nuevo-chat' && chatLocked} data-sidebar-collapsed={sidebarCollapsed}>
    <RielLateral title={title} activePath={activePath} collapsed={sidebarCollapsed} chatLocked={activePath === '/nuevo-chat' && chatLocked} onToggleCollapse={toggleSidebar} onLogout={() => void handleLogout()} />
    <div className="bloq-work">
      <header className="bloq-header">
        <div className="bloq-header-title"><span className="bloq-chip">{title}</span><span className="bloq-header-context">{isAuthenticated ? 'Tu espacio, con contexto.' : 'Un espacio para pensar con criterio.'}</span></div>
        {isAuthenticated && activePath !== '/nuevo-chat' && <a className="bloq-header-action" href="/nuevo-chat"><Icon name="plus" size={16} />Nueva conversación</a>}
      </header>
      <main className={`bloq-content${contentClassName ? ` ${contentClassName}` : ''}`}>{children}</main>
    </div>
  </div>;
}
