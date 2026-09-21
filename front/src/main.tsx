import React from 'react';
import ReactDOM from 'react-dom/client';
import { Router } from './app/router';
import { AppProviders } from './app/providers';
import { registerServiceWorker } from './sw/registerSW';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AppProviders>
      <Router />
    </AppProviders>
  </React.StrictMode>
);

registerServiceWorker();
