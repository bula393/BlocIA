import { useState, type ReactNode } from 'react';
import { MedidorTiempo } from '../estado/MedidorTiempo';
import { RielLateral } from './RielLateral';
import { getCurrentJwtStatus } from '../../app/routeGuard';
import { logout } from '../../api/auth';
import { navigateTo } from '../../app/navigation';

export function ChasisBloqIA({
  title,
  children,
  status,
  activePath = window.location.pathname
}: {
  title: string;
  children: ReactNode;
  status?: ReactNode;
  activePath?: string;
}) {
  const [usageOpen, setUsageOpen] = useState(false);
  const isAuthenticated = getCurrentJwtStatus() === 'valid';

  async function handleLogout() {
    await logout();
    navigateTo('/', true);
  }

  return (
    <div className="bloq-shell">
      <RielLateral activePath={activePath} onUsage={() => setUsageOpen((isOpen) => !isOpen)} onLogout={() => void handleLogout()} />
      <div className="bloq-work">
        <header className="bloq-header">
          <span className="bloq-chip">{title === 'Inicio' ? 'BloqIA' : title}</span>
          {isAuthenticated && <div className="bloq-compact-status" aria-label="Estado compacto">
            <span className="bloq-number">1 h 16</span><small>de 3 h</small>
          </div>}
          {isAuthenticated && <div className="bloq-pips" aria-label="Consultas personales">
            <span className="bloq-pip" data-level="1" />
            <span className="bloq-pip" data-level="2" />
            <span className="bloq-pip" />
          </div>}
        </header>
        <main className="bloq-content">{children}</main>
      </div>
      {usageOpen && <aside className="bloq-usage-drawer" aria-label="Estadísticas de uso">
        <div className="bloq-usage-heading"><h2>Uso de hoy</h2><button type="button" onClick={() => setUsageOpen(false)} aria-label="Cerrar estadísticas">Cerrar</button></div>
        {status ?? <>
          <section className="bloq-panel-block">
            <span className="bloq-panel-label">Tiempo usado</span>
            <strong className="bloq-panel-value bloq-number">1 h 16 <small>de 3 h</small></strong>
          </section>
          <section className="bloq-panel-block">
            <span className="bloq-panel-label">Consultas personales</span>
            <strong className="bloq-panel-small bloq-number">2 de 3</strong>
          </section>
          <section className="bloq-panel-block">
            <span className="bloq-panel-label">Última consulta</span>
            <span className="bloq-classification">Académica</span>
          </section>
        </>}
      </aside>}
      <MedidorTiempo />
    </div>
  );
}
