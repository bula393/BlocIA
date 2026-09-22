import { useState, type ReactNode } from 'react';
import { useQuery } from '@tanstack/react-query';
import { RielLateral } from './RielLateral';
import { getCurrentJwtStatus } from '../../app/routeGuard';
import { logout } from '../../api/auth';
import { getTodayUsage } from '../../api/usage';
import { navigateTo } from '../../app/navigation';

function formattedActivity(value: string | null) {
  return value ? new Intl.DateTimeFormat('es-AR', { hour: '2-digit', minute: '2-digit' }).format(new Date(value)) : 'Todavía no registraste actividad';
}

export function ChasisBloqIA({ title, children, status, activePath = window.location.pathname }: { title: string; children: ReactNode; status?: ReactNode; activePath?: string }) {
  const [usageOpen, setUsageOpen] = useState(false);
  const isAuthenticated = getCurrentJwtStatus() === 'valid';
  const usage = useQuery({ queryKey: ['usage-today'], queryFn: getTodayUsage, enabled: isAuthenticated, retry: false });

  async function handleLogout() {
    await logout();
    navigateTo('/', true);
  }

  function toggleUsage() {
    setUsageOpen((isOpen) => {
      const nextOpen = !isOpen;
      if (nextOpen) void usage.refetch();
      return nextOpen;
    });
  }

  return <div className="bloq-shell" data-chat={activePath === '/nuevo-chat'}>
    <RielLateral activePath={activePath} onUsage={toggleUsage} onLogout={() => void handleLogout()} />
    <div className="bloq-work">
      <header className="bloq-header">
        <span className="bloq-chip">{title === 'Inicio' ? 'BloqIA' : title}</span>
        {isAuthenticated && usage.data && <div className="bloq-compact-status" aria-label="Actividad de hoy"><span className="bloq-number">{usage.data.chatMessages ?? 0}</span><small> mensajes hoy</small></div>}
      </header>
      <main className="bloq-content">{children}</main>
    </div>
    {usageOpen && <aside className="bloq-usage-drawer" aria-label="Estadísticas de uso">
      <div className="bloq-usage-heading"><div><p className="provider-eyebrow">Datos guardados</p><h2>Actividad de hoy</h2></div><button type="button" onClick={() => setUsageOpen(false)} aria-label="Cerrar estadísticas">Cerrar</button></div>
      {status ?? <>
        {usage.isLoading && <p>Cargando actividad...</p>}
        {usage.isError && <p className="bloq-error">No se pudieron cargar las estadísticas guardadas.</p>}
        {usage.data && <>
          <section className="bloq-panel-block"><span className="bloq-panel-label">Mensajes enviados</span><strong className="bloq-panel-value bloq-number">{usage.data.chatMessages ?? 0}</strong><small>Consultas guardadas en tus chats hoy</small></section>
          <section className="bloq-panel-block"><span className="bloq-panel-label">Consultas de modelos</span><strong className="bloq-panel-value bloq-number">{usage.data.modelCatalogRequests}</strong><small>Actualizaciones del catálogo realizadas hoy</small></section>
          <section className="bloq-panel-block"><span className="bloq-panel-label">Proveedores conectados</span><strong className="bloq-panel-value bloq-number">{usage.data.configuredProviders}</strong><small>Claves configuradas actualmente</small></section>
          <section className="bloq-panel-block"><span className="bloq-panel-label">Última actividad</span><strong className="bloq-panel-small">{formattedActivity(usage.data.lastActivityAt)}</strong></section>
        </>}
      </>}
    </aside>}
  </div>;
}
