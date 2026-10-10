import { useEffect, useRef, useState } from 'react';
import { Brand, Icon } from '../mockup/brand';
import '../mockup/mockup.css';
import { useMobileViewport } from '../components/mobile/useMobileViewport';
import { MobileSheet } from '../components/mobile/MobileSheet';

export type LandingAction = 'chat' | 'profile' | 'providers' | 'usage' | 'login' | 'register' | 'google';
const stages = [
  { title: 'Una buena pregunta abre caminos.', text: 'Traé esa idea que todavía no termina de encajar. Una duda de estudio, un problema de trabajo o algo que querés entender mejor.', prompt: '¿Cómo puedo organizar el estudio de un tema nuevo?', label: 'Tu punto de partida', result: 'Empezá por lo que ya sabés. Una buena pregunta conecta lo nuevo con algo que ya entendés.' },
  { title: 'Primero, entendemos qué estás preguntando.', text: 'Cada consulta tiene un contexto. BloqIA distingue una pregunta general, un análisis personal y una decisión que requiere tu propio criterio.', prompt: '¿Qué factores puedo considerar antes de cambiar de trabajo?', label: 'Análisis personal', result: 'Podés ordenar la reflexión en cuatro aspectos: tus prioridades, el entorno, las oportunidades de aprendizaje y tu situación actual.' },
  { title: 'Más perspectiva. El criterio sigue siendo tuyo.', text: 'Explorá información con el modelo que elijas. Cuando la pregunta pide una decisión personal, BloqIA lo señala y deja ese paso en tus manos.', prompt: '¿Debería cambiar de trabajo?', label: 'Decisión personal', result: 'Esta consulta fue clasificada como una decisión personal. Revisá su clasificación antes de avanzar.' }
];

export function Landing({ open, isAuthenticated = false }: { open: (view: LandingAction) => void; isAuthenticated?: boolean }) {
  const [menu, setMenu] = useState(false);
  const [stage, setStage] = useState(0);
  const [faq, setFaq] = useState<number | null>(0);
  const mobile = useMobileViewport();
  const root = useRef<HTMLDivElement>(null);
  const heroImage = useRef<HTMLImageElement>(null);

  useEffect(() => {
    let frame = 0;
    const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
    const update = () => {
      frame = 0;
      const max = document.documentElement.scrollHeight - window.innerHeight;
      root.current?.style.setProperty('--mk-progress', String(max > 0 ? window.scrollY / max : 0));
      if (heroImage.current && !reduced.matches) heroImage.current.style.transform = `translateY(${Math.min(window.scrollY * .07, 32)}px) scale(1.06)`;
    };
    const scroll = () => { if (!frame) frame = window.requestAnimationFrame(update); };
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) if (entry.isIntersecting && !window.matchMedia('(max-width: 767px)').matches) setStage(Number((entry.target as HTMLElement).dataset.stage));
    }, { rootMargin: '-25% 0px -45% 0px', threshold: 0 });
    root.current?.querySelectorAll('[data-stage]').forEach(el => observer.observe(el));
    window.addEventListener('scroll', scroll, { passive: true });
    window.addEventListener('resize', scroll);
    update();
    return () => { observer.disconnect(); window.removeEventListener('scroll', scroll); window.removeEventListener('resize', scroll); if (frame) window.cancelAnimationFrame(frame); };
  }, []);

  const closeMenu = () => setMenu(false);
  const faqs = [
    ['¿Para qué puedo usar BloqIA?', 'Para entender un tema, ordenar ideas, explorar información o hacer preguntas de estudio y trabajo. Cada consulta muestra su clasificación para que puedas leer la respuesta con contexto.'],
    ['¿Puedo elegir el modelo que responde?', 'Sí. El espacio de chat incluye un selector. En Configuración podés conectar Google, Groq, OpenRouter, OpenAI o Anthropic con tus claves API. Las opciones disponibles dependen de la instalación y de cada proveedor.'],
    ['¿Dónde quedan mis conversaciones?', 'El historial se guarda por usuario en este equipo y podés eliminar cada chat. Si elegís un modelo remoto, tu consulta y su contexto se envían al proveedor que seleccionaste.'],
    ['¿Qué pasa con las decisiones personales?', 'BloqIA identifica las preguntas que solicitan una decisión personal, muestra su clasificación y no las envía al generador. El siguiente paso queda en tus manos.'],
    ['¿Necesito una clave para empezar?', 'Qwen local puede funcionar sin clave si sus pesos están instalados. También pueden existir modelos de respaldo configurados por el servidor. El catálogo y la disponibilidad real se muestran dentro del chat.']
  ];

  return <div className="mk-site" ref={root}>
    <a className="mk-skip" href="#contenido">Saltar al contenido</a>
    <div className="mk-reading-progress" aria-hidden="true" />
    <header className="mk-header">
      <a href="#contenido" className="mk-brand-link" aria-label="BloqIA, inicio" onClick={closeMenu}><Brand /></a>
      <nav className={`mk-nav${menu ? ' mk-nav--open' : ''}`} aria-label="Navegación del sitio">
        <a href="#espacio" onClick={closeMenu}>El espacio</a>
        <a href="#metodo" onClick={closeMenu}>Cómo funciona</a>
        <a href="#criterio" onClick={closeMenu}>Tu criterio</a>
      </nav>
      <div className="mk-header-actions"><button className="mk-access" onClick={() => open(isAuthenticated ? 'profile' : 'login')}>{isAuthenticated ? 'Mi perfil' : 'Iniciar sesión'}</button><button className="mk-button mk-button--small" onClick={() => open(isAuthenticated ? 'chat' : 'register')}>{isAuthenticated ? 'Abrir el chat' : 'Crear cuenta'} <Icon name="arrow-up" size={16} /></button></div>
      <button className="mk-menu" aria-label={menu ? 'Cerrar menú' : 'Abrir menú'} aria-expanded={menu} onClick={() => setMenu(!menu)}><Icon name={menu ? 'close' : 'menu'} /></button>
    </header>
    <MobileSheet open={mobile && menu} onClose={closeMenu} title="Explorá BloqIA"><nav className="mobile-landing-menu" aria-label="Secciones de la portada"><a href="#espacio" onClick={closeMenu}>El espacio<Icon name="chevron" /></a><a href="#metodo" onClick={closeMenu}>Cómo funciona<Icon name="chevron" /></a><a href="#criterio" onClick={closeMenu}>Tu criterio<Icon name="chevron" /></a><a href="#preguntas" onClick={closeMenu}>Antes de empezar<Icon name="chevron" /></a></nav><button type="button" className="mobile-sheet-primary" onClick={() => { closeMenu(); open(isAuthenticated ? 'chat' : 'register'); }}>{isAuthenticated ? 'Abrir el chat' : 'Crear cuenta'}</button><button type="button" className="mobile-sheet-secondary" onClick={() => { closeMenu(); open(isAuthenticated ? 'profile' : 'login'); }}>{isAuthenticated ? 'Mi perfil' : 'Iniciar sesión'}</button></MobileSheet>

    <main id="contenido">
      <section className="mk-hero" aria-labelledby="hero-title">
        <div className="mk-hero-copy">
          <h1 id="hero-title">Pensá con<br />más <span>perspectiva.</span></h1>
          <p className="mk-hero-description">Un espacio para hacer mejores preguntas,<br className="mk-desktop-break" /> explorar ideas y encontrar tu próximo paso.</p>
          <div className="mk-hero-actions"><button className="mk-button" onClick={() => open('chat')}>Abrí tu espacio <Icon name="arrow" /></button><a className="mk-text-link" href="#metodo">Descubrí cómo <Icon name="down" size={17} /></a></div>
          <div className="mk-hero-example">
            <span className="mk-example-marker" aria-hidden="true"><Brand compact /></span>
            <div><span className="mk-example-label">Un punto de partida · ejemplo</span><p>“¿Y si empezamos por lo que ya sabés?”</p></div>
          </div>
        </div>
        <figure className="mk-hero-figure">
          <div className="mk-hero-photo"><img ref={heroImage} src="/mockup/images/thinking-desk.png" alt="Manos trazando ideas en un cuaderno, junto a bloques azules sobre una mesa de estudio" width="1536" height="1024" fetchPriority="high" /></div>
          <figcaption><span>Las ideas se construyen.</span><span>Una pregunta a la vez.</span></figcaption>
          <a href="#metodo" className="mk-photo-arrow" aria-label="Explorar cómo funciona"><Icon name="down" size={28} /></a>
        </figure>
      </section>

      <section className="mk-introduction" id="espacio" aria-labelledby="space-title">
        <div className="mk-section-heading"><h2 id="space-title">Menos ruido.<br /><span>Más espacio para pensar.</span></h2><p>Una conversación puede ser mucho más que una respuesta. Puede ayudarte a entender, conectar y mirar desde otro lugar.</p></div>
        <div className="mk-purpose-list">
          <button onClick={() => open('chat')}><span>Entendé un tema</span><p>Del concepto abstracto al ejemplo que hace clic.</p><Icon name="arrow-up" size={24} /></button>
          <button onClick={() => open('chat')}><span>Ordená tus ideas</span><p>Conectá preguntas. Encontrá el hilo de lo que importa.</p><Icon name="arrow-up" size={24} /></button>
          <button onClick={() => open('chat')}><span>Explorá posibilidades</span><p>Sumá información para formar tu propia perspectiva.</p><Icon name="arrow-up" size={24} /></button>
        </div>
      </section>

      <section className="mk-method" id="metodo" aria-labelledby="method-title">
        <div className="mk-method-top"><h2 id="method-title">De la pregunta<br />a una nueva perspectiva.</h2><p>Así se construye una conversación en BloqIA.<br />Deslizá para seguir el recorrido.</p></div>
        <div className="mk-mobile-stage-tabs" role="group" aria-label="Pasos de una consulta">{['Preguntar', 'Clasificar', 'Explorar'].map((label, i) => <button type="button" key={label} aria-pressed={stage === i} onClick={() => setStage(i)}>{label}</button>)}</div>
        <div className="mk-method-grid">
          <div className="mk-chapters">
            {stages.map((item, i) => <article className={`mk-chapter${stage === i ? ' mk-chapter--active' : ''}`} key={item.title} data-stage={i}><div className="mk-chapter-position" aria-label={`Paso ${i + 1} de 3`}><span>{['Preguntar', 'Clasificar', 'Explorar'][i]}</span><span>{i + 1} / 3</span></div><h3>{item.title}</h3><p>{item.text}</p></article>)}
          </div>
          <div className="mk-demo-sticky">
            <div className="mk-conversation" aria-label="Ejemplo de conversación según el recorrido">
              <header><Brand compact /><span>Una idea en construcción</span><span className="mk-demo-note">Ejemplo</span></header>
              <div className="mk-conversation-body" key={stage}>
                <span className="mk-dialog-author">Vos</span><p className="mk-dialog-question">{stages[stage].prompt}</p>
                <div className="mk-classify-result"><span className={`mk-status-dot${stage === 2 ? ' mk-status-dot--attention' : ''}`} />{stage === 0 ? 'Consulta general' : stages[stage].label}<span>Clasificación</span></div>
                <div className="mk-dialog-answer"><div className="mk-dialog-brand"><Brand compact /><strong>BloqIA</strong></div><p>{stages[stage].result}</p>{stage === 2 && <span className="mk-human-note"><Icon name="shield" size={16} /> Tu decisión, tu criterio.</span>}</div>
              </div>
              <footer><span>Una pregunta abre otra.</span><button onClick={() => open('chat')} aria-label="Abrir chat de demostración"><Icon name="arrow" /></button></footer>
            </div>
            <div className="mk-step-controls" aria-label="Pasos del ejemplo">{stages.map((_, i) => <button key={i} aria-label={`Ver paso ${i + 1}: ${['preguntar', 'clasificar', 'explorar'][i]}`} aria-pressed={stage === i} onClick={() => setStage(i)} />)}</div>
          </div>
        </div>
      </section>

      <section className="mk-tools" aria-labelledby="tools-title">
        <div className="mk-section-heading"><h2 id="tools-title">Un lugar para tus ideas.<br /><span>Y todas tus herramientas.</span></h2><p>Volvé a una conversación, elegí cómo responder o ajustá tu perfil. Todo tiene su lugar.</p></div>
        <div className="mk-tools-layout">
          <div className="mk-workspace-preview">
            <aside><Brand compact /><div><Icon name="chat" /><Icon name="settings" /><Icon name="profile" /></div></aside>
            <div className="mk-mini-work"><header><span>Tu espacio</span><span className="mk-mini-model">Qwen local <Icon name="chevron-down" size={13} /></span></header><div className="mk-mini-content"><h3>¿Qué tenés en mente?</h3><p>Cada idea empieza con una pregunta.</p><button onClick={() => open('chat')}>Explicame un concepto <Icon name="arrow-up" size={15} /></button><button onClick={() => open('chat')}>Ayudame a ordenar una idea <Icon name="arrow-up" size={15} /></button></div><button className="mk-mini-composer" onClick={() => open('chat')}><span>Escribí tu pregunta…</span><span><Icon name="arrow" size={16} /></span></button><small>Vista de ejemplo del espacio de trabajo</small></div>
          </div>
          <div className="mk-feature-directory">
            <button onClick={() => open('chat')}><div><Icon name="chat" /><h3>Conversaciones que continúan</h3><p>Tus conversaciones, listas para retomar donde las dejaste.</p></div><Icon name="arrow-up" /></button>
            <button onClick={() => open('providers')}><div><Icon name="settings" /><h3>El modelo lo elegís vos</h3><p>Conectá tus proveedores o usá las opciones disponibles.</p></div><Icon name="arrow-up" /></button>
            <button onClick={() => open('usage')}><div><Icon name="usage" /><h3>Tu actividad, a la vista</h3><p>Consultá tus mensajes y conexiones de hoy.</p></div><Icon name="arrow-up" /></button>
            <button onClick={() => open('profile')}><div><Icon name="profile" /><h3>Un espacio con tu contexto</h3><p>Configurá tu perfil para tu estudio o tu trabajo.</p></div><Icon name="arrow-up" /></button>
          </div>
        </div>
      </section>

      <section className="mk-criterion" id="criterio" aria-labelledby="criterion-title">
        <figure><img src="/mockup/images/quiet-study.png" alt="Estudio tranquilo con luz natural, libros abiertos y una silla azul frente a un ventanal" width="1024" height="1536" loading="lazy" /><figcaption>El espacio también es parte de la idea.</figcaption></figure>
        <div className="mk-criterion-copy"><h2 id="criterion-title">La inteligencia<br />suma.<br /><em>Tu criterio guía.</em></h2><p>La idea no es pensar menos.<br />Es pensar mejor.</p><p className="mk-criterion-detail">BloqIA te acompaña con información y contexto. Las decisiones personales merecen una pausa, una mirada propia y, cuando hace falta, la orientación de otra persona.</p><a className="mk-text-link" href="#preguntas">Conocé cómo cuidamos ese espacio <Icon name="arrow" size={18} /></a><div className="mk-principle"><Icon name="shield" size={20} /><span>Las decisiones personales no se envían al generador.</span></div></div>
      </section>

      <section className="mk-faq" id="preguntas" aria-labelledby="faq-title"><h2 id="faq-title">Antes de empezar.</h2><div className="mk-faq-list">{faqs.map(([question, answer], i) => <div className="mk-faq-item" key={question}><h3><button aria-expanded={faq === i} aria-controls={`mk-faq-${i}`} onClick={() => setFaq(faq === i ? null : i)}>{question}<Icon name={faq === i ? 'close' : 'plus'} size={20} /></button></h3><div id={`mk-faq-${i}`} hidden={faq !== i}><p>{answer}</p></div></div>)}</div></section>

      <section className="mk-closing" aria-labelledby="closing-title"><div><h2 id="closing-title">Tu próxima idea<br />empieza <em>acá.</em></h2><button className="mk-button mk-button--light" onClick={() => open('chat')}>Empezá una conversación <Icon name="arrow" /></button></div><span className="mk-closing-mark" aria-hidden="true"><Brand compact /></span><p>Traé una pregunta.<br />Llevate otra perspectiva.</p></section>
    </main>
    {mobile && <div className="mk-mobile-dock"><button type="button" className="mk-button" onClick={() => open('chat')}>Abrí tu espacio<Icon name="arrow" size={19} /></button></div>}

    <footer className="mk-footer"><div className="mk-footer-top"><div><Brand /><p>Un espacio para pensar con criterio.</p></div><div className="mk-footer-links"><div><strong>Tu espacio</strong><button onClick={() => open('chat')}>Chat y conversaciones</button><button onClick={() => open('providers')}>Proveedores y modelos</button></div><div><strong>Tu cuenta</strong><button onClick={() => open('profile')}>Perfil</button><button onClick={() => open('usage')}>Actividad</button><button onClick={() => open('login')}>Iniciar sesión</button><button onClick={() => open('register')}>Crear cuenta</button></div><div><strong>Explorá</strong><a href="#metodo">Cómo funciona</a><a href="#criterio">Tu criterio</a><a href="#identidad">La identidad</a><button onClick={() => open('google')}>Acceso con Google</button></div></div></div>
      <div className="mk-brand-system" id="identidad"><div><strong>Una identidad que se construye.</strong><p>Bloques que conectan. Tinta para pensar. Papel para leer.</p><a href="/mockup/logo.svg" download="bloqia-logo.svg">Descargar logo SVG <Icon name="arrow-up" size={14} /></a></div><div className="mk-palette" aria-label="Paleta de identidad"><div><span style={{ background: '#18252B' }} /><strong>Tinta</strong><code>#18252B</code></div><div><span style={{ background: '#F4F3EE' }} /><strong>Papel</strong><code>#F4F3EE</code></div><div><span style={{ background: '#244ADA' }} /><strong>Ultramar</strong><code>#244ADA</code></div><div><span style={{ background: '#DAED9E' }} /><strong>Idea</strong><code>#DAED9E</code></div></div></div>
      <div className="mk-footer-bottom"><span>© 2026 BloqIA</span><span>Un espacio para pensar con criterio.</span><a href="#contenido">Volver arriba <Icon name="arrow-up" size={14} /></a></div>
    </footer>
  </div>;
}
