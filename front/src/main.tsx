import React from 'react';
import ReactDOM from 'react-dom/client';
import { Router } from './app/router';
import { AppProviders } from './app/providers';
import { registerServiceWorker } from './sw/registerSW';
const Mockup = React.lazy(() => import('./mockup/Mockup').then((module) => ({ default: module.Mockup })));

const isMockup = window.location.pathname === '/mockup';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    {isMockup ? <React.Suspense fallback={<main aria-label="Cargando mockup">Abriendo el espacio de diseño…</main>}><Mockup /></React.Suspense> : <AppProviders>
      <Router />
    </AppProviders>}
  </React.StrictMode>
);

if (!isMockup) registerServiceWorker();
