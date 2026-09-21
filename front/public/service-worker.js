const SHELL_CACHE = 'blocia-shell-v1';
const SHELL_ASSETS = ['/', '/index.html', '/manifest.webmanifest'];

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(SHELL_CACHE).then((cache) => cache.addAll(SHELL_ASSETS)));
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  const privatePath = url.pathname.startsWith('/auth') || url.pathname.startsWith('/profile') || url.pathname.startsWith('/technical-profile');
  if (privatePath || event.request.method !== 'GET') {
    event.respondWith(fetch(event.request));
    return;
  }
  event.respondWith(caches.match(event.request).then((cached) => cached || fetch(event.request)));
});
