import { ChasisBloqIA } from '../components/chasis/ChasisBloqIA';
import { getCurrentJwtStatus } from '../app/routeGuard';

export function Inicio() {
  const isAuthenticated = getCurrentJwtStatus() === 'valid';

  return (
    <ChasisBloqIA title="Inicio" activePath="/" contentClassName="inicio-content">
      <section className="inicio-surface" aria-label={isAuthenticated ? 'Inicio personal' : 'Inicio público'}>
        <div className="inicio-hero">
          <div className="inicio-copy">
            <h1>Tu espacio para pensar con criterio.</h1>
            <p className="bloq-reading">Estudiá, explorá una idea o resolvé una duda de trabajo. Vos ponés la pregunta; BloqIA te ayuda a encontrar el siguiente paso.</p>
            <div className="bloq-actions inicio-actions">
              {isAuthenticated ? <>
                <a className="bloq-button" data-primary="true" href="/nuevo-chat">Nuevo chat</a>
                <a className="bloq-button" href="/perfil-tecnico">Configurar técnico</a>
              </> : <>
                <a className="bloq-button" data-primary="true" href="/login">Iniciar sesión</a>
                <a className="bloq-button" href="/register">Crear cuenta</a>
              </>}
            </div>
          </div>
          <aside className="inicio-example" aria-label="Ejemplo ilustrativo de una conversación">
            <header className="inicio-example-header">
              <span>Una pregunta, un punto de partida</span>
              <span className="inicio-example-label">Ejemplo</span>
            </header>
            <div className="inicio-example-body">
              <p className="inicio-example-author">Vos</p>
              <p className="inicio-example-question">¿Cómo puedo organizar el estudio de un tema nuevo?</p>
              <div className="inicio-example-answer">
                <p className="inicio-example-author">BloqIA</p>
                <p className="bloq-reading">Empezá por lo que ya sabés. Después, dividí el tema en preguntas más pequeñas.</p>
                <ol>
                  <li>Identificá las ideas principales.</li>
                  <li>Conectá cada idea con un ejemplo.</li>
                  <li>Explicalo con tus propias palabras.</li>
                </ol>
              </div>
            </div>
            <footer className="inicio-example-footer">La idea no es pensar menos. Es pensar mejor.</footer>
          </aside>
        </div>
      </section>
    </ChasisBloqIA>
  );
}
