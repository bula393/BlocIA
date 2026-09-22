import { useEffect, useState } from 'react';
import { getCurrentJwtStatus, isPublicRoute } from './routeGuard';
import { Inicio } from '../pages/Inicio';
import { Login } from '../pages/Login';
import { Register } from '../pages/Register';
import { Perfil } from '../pages/Perfil';
import { PerfilTecnico } from '../pages/PerfilTecnico';
import { NuevoChat } from '../pages/NuevoChat';
import { ChasisBloqIA } from '../components/chasis/ChasisBloqIA';
import { GoogleCallback } from '../pages/GoogleCallback';

function ProtectedRouteGuard({ requestedPath }: { requestedPath: string }) {
  return (
    <ChasisBloqIA title="Acceso requerido" activePath="/login">
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
  const [path, setPath] = useState(window.location.pathname);

  useEffect(() => {
    const updatePath = () => setPath(window.location.pathname);
    window.addEventListener('popstate', updatePath);
    return () => window.removeEventListener('popstate', updatePath);
  }, []);
  if (path === '/') return <Inicio />;
  if (path === '/register') return <Register />;
  if (path === '/login') return <Login />;
  if (path === '/auth/google/callback') return <GoogleCallback />;
  if (!isPublicRoute(path) && getCurrentJwtStatus() !== 'valid') return <ProtectedRouteGuard requestedPath={path} />;
  if (path === '/perfil') return <Perfil />;
  if (path === '/perfil-tecnico') return <PerfilTecnico />;
  if (path === '/nuevo-chat') return <NuevoChat />;
  return <ProtectedRouteGuard requestedPath={path} />;
}
