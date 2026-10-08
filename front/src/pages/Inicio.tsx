import { getCurrentJwtStatus } from '../app/routeGuard';
import { navigateTo } from '../app/navigation';
import { startGoogleLogin } from '../api/auth';
import { Landing, type LandingAction } from './Landing';

export function Inicio() {
  const isAuthenticated = getCurrentJwtStatus() === 'valid';

  function open(action: LandingAction) {
    if (action === 'google') {
      startGoogleLogin();
      return;
    }

    const destinations: Record<Exclude<LandingAction, 'google'>, string> = {
      chat: isAuthenticated ? '/nuevo-chat' : '/login',
      profile: isAuthenticated ? '/perfil' : '/login',
      providers: isAuthenticated ? '/perfil-tecnico' : '/login',
      usage: isAuthenticated ? '/actividad' : '/login',
      login: isAuthenticated ? '/perfil' : '/login',
      register: isAuthenticated ? '/nuevo-chat' : '/register'
    };

    navigateTo(destinations[action]);
  }

  return <div className="mockup-app"><Landing open={open} isAuthenticated={isAuthenticated} /></div>;
}
