import { QueryClientProvider } from '@tanstack/react-query';
import { queryClient } from './queryClient';
import { useEffect, useState, type ReactNode } from 'react';
import { forgetSession, restoreSession } from '../api/auth';
import { getCurrentJwtStatus } from './routeGuard';
import '../tokens/visual.css';
import '../tokens/typography.css';
import '../tokens/chat.css';

function SessionBootstrap({ children }: { children: ReactNode }) {
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    let isMounted = true;
    if (getCurrentJwtStatus() === 'valid') {
      setIsReady(true);
      return () => {
        isMounted = false;
      };
    }

    const controller = new AbortController();
    const timeoutId = window.setTimeout(() => controller.abort(), 2_000);
    restoreSession(controller.signal)
      .catch(() => forgetSession())
      .finally(() => {
        window.clearTimeout(timeoutId);
        if (isMounted) setIsReady(true);
      });
    return () => {
      isMounted = false;
      window.clearTimeout(timeoutId);
      controller.abort();
    };
  }, []);

  if (!isReady) {
    return <div className="bloq-session-loading" role="status" aria-label="Restaurando sesión" />;
  }
  return <>{children}</>;
}

export function AppProviders({ children }: { children: ReactNode }) {
  return <QueryClientProvider client={queryClient}><SessionBootstrap>{children}</SessionBootstrap></QueryClientProvider>;
}
