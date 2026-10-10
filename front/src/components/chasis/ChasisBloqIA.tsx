import { useEffect, useRef, useState, type ReactNode } from 'react';
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

export function ChasisBloqIA({ title, children, activePath = window.location.pathname, contentClassName, chatLocked = false, mobileSection, onMobileChatNavigation }: { title: string; children: ReactNode; activePath?: string; contentClassName?: string; chatLocked?: boolean; mobileSection?: 'home' | 'chats'; onMobileChatNavigation?: (section: 'home' | 'chats') => void }) {
  const isAuthenticated = getCurrentJwtStatus() === 'valid';
  const [sidebarCollapsed, setSidebarCollapsed] = useState(() => readSidebarPreference() ?? activePath === '/nuevo-chat');
  const shell = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const viewport = window.visualViewport;
    if (!viewport) return;
    let frame = 0;
    let restingHeight = window.innerHeight;
    let viewportWidth = window.innerWidth;
    const update = () => {
      const element = shell.current;
      if (!element) return;
      const fieldFocused = Boolean(document.activeElement?.matches('input, textarea, select'));
      if (!fieldFocused || viewportWidth !== window.innerWidth) {
        restingHeight = window.innerHeight;
        viewportWidth = window.innerWidth;
      }
      const keyboardOpen = window.matchMedia('(max-width: 767px)').matches
        && fieldFocused && viewport.height < restingHeight - 100;
      element.dataset.keyboardOpen = String(keyboardOpen);
      if (keyboardOpen) element.style.setProperty('--mobile-app-height', `${viewport.height}px`);
      else element.style.removeProperty('--mobile-app-height');
    };
    const schedule = () => { cancelAnimationFrame(frame); frame = requestAnimationFrame(update); };
    viewport.addEventListener('resize', schedule);
    window.addEventListener('resize', schedule);
    document.addEventListener('focusin', schedule);
    document.addEventListener('focusout', schedule);
    return () => {
      cancelAnimationFrame(frame);
      viewport.removeEventListener('resize', schedule);
      window.removeEventListener('resize', schedule);
      document.removeEventListener('focusin', schedule);
      document.removeEventListener('focusout', schedule);
    };
  }, []);

  function toggleSidebar() {
    const next = !sidebarCollapsed;
    saveSidebarPreference(next);
    setSidebarCollapsed(next);
  }

  async function handleLogout() {
    await logout();
    navigateTo('/', true);
  }

  return <div ref={shell} className="bloq-shell" data-authenticated={isAuthenticated} data-chat={activePath === '/nuevo-chat'} data-chat-locked={activePath === '/nuevo-chat' && chatLocked} data-sidebar-collapsed={sidebarCollapsed}>
    <RielLateral title={title} activePath={activePath} collapsed={sidebarCollapsed} chatLocked={activePath === '/nuevo-chat' && chatLocked} onToggleCollapse={toggleSidebar} onLogout={() => void handleLogout()} />
    <div className="bloq-work">
      <header className="bloq-header">
        <div className="bloq-header-title"><span className="bloq-chip">{title}</span><span className="bloq-header-context">{isAuthenticated ? 'Tu espacio, con contexto.' : 'Un espacio para pensar con criterio.'}</span></div>
        {isAuthenticated && activePath !== '/nuevo-chat' && <a className="bloq-header-action" href="/nuevo-chat"><Icon name="plus" size={16} />Nueva conversación</a>}
      </header>
      <main className={`bloq-content${contentClassName ? ` ${contentClassName}` : ''}`}>{children}</main>
    </div>
    {isAuthenticated && <nav className="bloq-bottom-nav" aria-label="Navegación móvil">
      {([['home', '/nuevo-chat', 'home', 'Inicio'], ['chats', '/nuevo-chat?history=1', 'chat', 'Chats'], ['account', '/cuenta', 'user', 'Cuenta']] as const).map(([section, href, icon, label]) => {
        const active = section === 'account' ? activePath !== '/nuevo-chat' : activePath === '/nuevo-chat' && (mobileSection ?? 'home') === section;
        return <a key={section} href={href} aria-current={active ? 'page' : undefined} onClick={(event) => {
          if (onMobileChatNavigation && section !== 'account') { event.preventDefault(); onMobileChatNavigation(section); }
        }}><span><Icon name={icon} size={22} /></span>{label}</a>;
      })}
    </nav>}
  </div>;
}
