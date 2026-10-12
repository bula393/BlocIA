const SHELL_CACHE = 'blocia-shell-v3-chat';
const SHELL_ASSETS = ['/', '/index.html', '/manifest.webmanifest'];

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(SHELL_CACHE).then((cache) => cache.addAll(SHELL_ASSETS)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (event) => {
  event.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((key) => key.startsWith('blocia-shell-') && key !== SHELL_CACHE).map((key) => caches.delete(key)))).then(() => self.clients.claim()));
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  const privatePath = ['/api', '/auth', '/profile', '/technical-profile', '/chat', '/nuevo-chat', '/perfil'].some((path) => url.pathname.startsWith(path));
  if (privatePath || event.request.method !== 'GET') {
    event.respondWith(fetch(event.request));
    return;
  }
  const isShellNavigation = event.request.mode === 'navigate' || url.pathname === '/index.html';
  if (isShellNavigation) {
    event.respondWith((async () => {
      const cache = await caches.open(SHELL_CACHE);
      try {
        const response = await fetch(event.request);
        if (response.ok) await cache.put(event.request, response.clone());
        return response;
      } catch {
        return (await cache.match(event.request)) || (await cache.match('/index.html')) || Response.error();
      }
    })());
    return;
  }
  event.respondWith(caches.match(event.request).then((cached) => cached || fetch(event.request)));
});
