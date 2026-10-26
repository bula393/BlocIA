import { useEffect, useLayoutEffect, useRef, useState, type ReactNode } from 'react';
import { flushSync } from 'react-dom';
import { changeView, trackMotionPreferences } from './motion';
import { handleInternalLink } from './navigation';
import { useContentTransition } from '../components/useContentTransition';
import { getCurrentJwtStatus, isPublicRoute } from './routeGuard';
import { Inicio } from '../pages/Inicio';
import { Login } from '../pages/Login';
import { Register } from '../pages/Register';
import { Perfil } from '../pages/Perfil';
import { PerfilTecnico } from '../pages/PerfilTecnico';
import { NuevoChat } from '../pages/NuevoChat';
import { ChasisBloqIA } from '../components/chasis/ChasisBloqIA';
import { GoogleCallback } from '../pages/GoogleCallback';
import { Actividad } from '../pages/Actividad';
import { Cuenta } from '../pages/Cuenta';

function ProtectedRouteGuard({ requestedPath }: { requestedPath: string }) {
  return (
    <ChasisBloqIA title="Acceso requerido" activePath="/login" contentClassName="auth-content">
      <section className="bloq-section guard-surface" aria-label="Ruta protegida">
        <h1>Iniciá sesión para seguir</h1>
        <p className="bloq-status-line" data-state="attention">La ruta {requestedPath} requiere un token JWT válido.</p>
        <div className="bloq-actions">
          <a className="bloq-button" data-primary="true" href="/login">Iniciar sesión</a>
        </div>
      </section>
    </ChasisBloqIA>
  );
}

export function Router() {
  const [location, setLocation] = useState(() => window.location.pathname + window.location.search);
  const requested = useRef(location);
  const previous = useRef(location);
  const view = useRef<HTMLDivElement>(null);
  const path = location.split('?')[0];
  useContentTransition(view, location, typeof (document as Document & { startViewTransition?: unknown }).startViewTransition !== 'function');

  useEffect(() => {
    const stopTracking = trackMotionPreferences();
    const updatePath = () => {
      const next = window.location.pathname + window.location.search;
      if (next === requested.current) return;
      requested.current = next;
      changeView((synchronous) => {
        if (synchronous) flushSync(() => setLocation(next));
        else setLocation(next);
      });
    };
    window.addEventListener('popstate', updatePath);
    document.addEventListener('click', handleInternalLink);
    return () => {
      stopTracking();
      window.removeEventListener('popstate', updatePath);
      document.removeEventListener('click', handleInternalLink);
    };
  }, []);

  useLayoutEffect(() => {
    if (previous.current === location) return;
    previous.current = location;
    // Route changes announce the destination without scrolling animated content under the reader.
    const heading = Array.from(view.current?.querySelectorAll<HTMLElement>('h1') ?? []).find(element => element.getClientRects().length);
    const focusTarget = heading ?? view.current;
    focusTarget?.setAttribute('tabindex', '-1');
    focusTarget?.focus({ preventScroll: true });
    window.scrollTo({ top: 0, behavior: 'instant' });
    if (window.location.hash) {
      const anchor = document.getElementById(decodeURIComponent(window.location.hash.slice(1)));
      anchor?.scrollIntoView({ behavior: 'instant' });
    }
  }, [location]);

  let page: ReactNode;
  if (path === '/') page = <Inicio />;
  else if (path === '/register') page = <Register />;
  else if (path === '/login') page = <Login />;
  else if (path === '/auth/google/callback') page = <GoogleCallback />;
  else if (!isPublicRoute(path) && getCurrentJwtStatus() !== 'valid') page = <ProtectedRouteGuard requestedPath={path} />;
  else if (path === '/perfil') page = <Perfil />;
  else if (path === '/perfil-tecnico') page = <PerfilTecnico />;
  else if (path === '/nuevo-chat') page = <NuevoChat />;
  else if (path === '/actividad') page = <Actividad />;
  else if (path === '/cuenta') page = <Cuenta />;
  else page = <ProtectedRouteGuard requestedPath={path} />;
  return <div className="route-view" ref={view} key={location}>{page}</div>;
}
