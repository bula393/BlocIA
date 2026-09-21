import { ChasisBloqIA } from '../components/chasis/ChasisBloqIA';

export function Inicio() {
  return (
    <ChasisBloqIA title="Inicio" activePath="/">
      <section className="inicio-surface" aria-label="Inicio publico">
        <div className="inicio-copy">
          <h1>Tu espacio para pensar con criterio.</h1>
          <p className="bloq-reading">Consultá sobre lo que estudiás o trabajás. BloqIA mantiene visible el tiempo de uso y separa las consultas personales de las académicas.</p>
        </div>
        <div className="bloq-actions inicio-actions">
          <a className="bloq-button" data-primary="true" href="/login">Iniciar sesión</a>
          <a className="bloq-button" href="/register">Crear cuenta</a>
        </div>
      </section>
    </ChasisBloqIA>
  );
}
