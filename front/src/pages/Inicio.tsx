import { ChasisBloqIA } from '../components/chasis/ChasisBloqIA';
import { getCurrentJwtStatus } from '../app/routeGuard';

export function Inicio() {
  const isAuthenticated = getCurrentJwtStatus() === 'valid';

  return (
    <ChasisBloqIA title="Inicio" activePath="/">
      <section className="inicio-surface" aria-label={isAuthenticated ? 'Inicio personal' : 'Inicio público'}>
        <div className="inicio-copy">
          <h1>Tu espacio para pensar con criterio.</h1>
          <p className="bloq-reading">Consultá sobre lo que estudiás o trabajás. BloqIA mantiene visible el tiempo de uso y separa las consultas personales de las académicas.</p>
        </div>
        <div className="bloq-actions inicio-actions">
          {isAuthenticated ? <>
            <a className="bloq-button" data-primary="true" href="/nuevo-chat">Nuevo chat</a>
            <a className="bloq-button" href="/perfil-tecnico">Configurar técnico</a>
          </> : <>
            <a className="bloq-button" data-primary="true" href="/login">Iniciar sesión</a>
            <a className="bloq-button" href="/register">Crear cuenta</a>
          </>}
        </div>
      </section>
    </ChasisBloqIA>
  );
}
