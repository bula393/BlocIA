export function navigateTo(path: string, replace = false) {
  window.history[replace ? 'replaceState' : 'pushState']({}, '', path);
  window.dispatchEvent(new PopStateEvent('popstate'));
}

const applicationPaths = new Set(['/', '/login', '/register', '/auth/google/callback', '/nuevo-chat', '/perfil', '/perfil-tecnico', '/actividad', '/cuenta']);

export function handleInternalLink(event: MouseEvent) {
  if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
  const link = event.target instanceof Element ? event.target.closest('a[href]') : null;
  if (!(link instanceof HTMLAnchorElement) || link.hasAttribute('download') || (link.target && link.target !== '_self') || link.rel.split(/\s+/).includes('external')) return;
  const destination = new URL(link.href);
  if (destination.origin !== window.location.origin || !applicationPaths.has(destination.pathname)) return;
  // Same-page anchors retain native scrolling, focus and browser history.
  if (destination.pathname === window.location.pathname && destination.search === window.location.search) {
    if (!destination.hash) event.preventDefault();
    return;
  }
  event.preventDefault();
  navigateTo(`${destination.pathname}${destination.search}${destination.hash}`);
}
