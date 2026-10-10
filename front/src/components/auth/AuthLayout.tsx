import type { ReactNode } from 'react';
import { Brand, Icon } from '../../mockup/brand';

export function AuthLayout({ children }: { children: ReactNode }) {
  return <div className="auth-page">
    <aside className="auth-story">
      <a className="auth-brand" href="/" aria-label="BloqIA, inicio"><Brand light /></a>
      <div className="auth-story-copy">
        <p className="auth-story-kicker">UN ESPACIO PARA PENSAR</p>
        <h2>La claridad empieza con una pregunta.</h2>
        <p>Explorá una idea con información, contexto y espacio para formar tu propia perspectiva.</p>
        <div className="auth-story-principle"><Icon name="shield" size={19} /><span>La inteligencia suma.<br /><strong>Tu criterio guía.</strong></span></div>
      </div>
      <footer className="auth-story-footer"><span>© 2026 BloqIA</span><span>Ideas en construcción.</span></footer>
    </aside>
    <main className="auth-main">
      <header className="auth-main-header"><a href="/" className="auth-home-link"><Icon name="arrow-left" size={16} />Volver al inicio</a><span>Un paso a la vez.</span></header>
      <a href="/" className="auth-mobile-brand" aria-label="BloqIA, inicio"><Brand compact /></a>
      <div className="auth-form-wrap">{children}</div>
      <footer className="auth-main-footer">Una buena pregunta abre caminos.</footer>
    </main>
  </div>;
}
