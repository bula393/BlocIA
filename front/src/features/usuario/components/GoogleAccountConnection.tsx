import { useEffect, useState } from 'react';
import { Notice } from '../../../components/Notice';
import { useGoogleConnection } from '../useGoogleConnection';
import { Icon } from '../../../mockup/brand';
import './provider-accounts.css';

const callbackMessages: Record<string, string> = {
  connected: 'Cuenta Google conectada. Elegí un proyecto para terminar.',
  state: 'Esta conexión venció o cambió tu sesión. Volvé a conectar la cuenta.',
  cancelled: 'Cancelaste la conexión. Podés volver a intentarlo cuando quieras.',
  permission: 'Google no autorizó todos los permisos necesarios. Volvé a conectar tu cuenta y revisá la autorización.',
  configuration: 'La conexión con Google todavía no está habilitada en BloqIA.',
  unavailable: 'No pudimos completar la conexión con Google. Volvé a intentarlo.',
  reconnect: 'Volvé a conectar tu cuenta Google para continuar.',
};

export function GoogleAccountConnection({ emailVerified }: { emailVerified: boolean }) {
  const { status, projects, start, select, disconnect } = useGoogleConnection();
  const [selected, setSelected] = useState('');
  const [changingProject, setChangingProject] = useState(false);
  const [result] = useState(() => new URLSearchParams(window.location.search).get('google'));
  useEffect(() => {
    if (result) {
      const url = new URL(window.location.href);
      url.searchParams.delete('google');
      window.history.replaceState(null, '', url.pathname + url.search + url.hash);
    }
  }, [result]);
  const current = status.data;
  const projectId = selected || current?.projectId || (projects.data?.projects.length === 1 ? projects.data.projects[0].projectId : '');
  const choosingProject = current?.connected && !current.needsReconnect && current.available && (!current.ready || changingProject);
  const busy = start.isPending || select.isPending || disconnect.isPending;
  const error = [start, select, disconnect].find((mutation) => mutation.isError);
  const enableUrl = projectId ? `https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com?project=${encodeURIComponent(projectId)}` : 'https://aistudio.google.com/';

  return <div className="provider-account" data-ready={Boolean(current?.ready)}>
    <div className="provider-account__heading"><h3>{current?.ready ? 'Tu cuenta está lista' : 'Usá Gemini con tu cuenta'}</h3>{current?.ready && <span className="provider-account__ready"><Icon name="check" size={15} /> Conectada</span>}</div>
    {!current?.ready && <p>Autorizá tu cuenta en Google y elegí dónde usar Gemini. Sin copiar claves.</p>}
    {current?.available && <ol className="provider-account__steps" aria-label="Pasos para conectar Google">
      <li data-complete={Boolean(current.connected && !current.needsReconnect)} aria-current={!current.connected || current.needsReconnect ? 'step' : undefined}><span aria-hidden="true">{current.connected && !current.needsReconnect ? <Icon name="check" size={14} /> : '1'}</span>Autorizar cuenta</li>
      <li data-complete={current.ready} aria-current={current.connected && !current.needsReconnect && !current.ready ? 'step' : undefined}><span aria-hidden="true">{current.ready ? <Icon name="check" size={14} /> : '2'}</span>Comprobar Gemini</li>
    </ol>}
    {result && callbackMessages[result] && (result !== 'connected' || (current?.connected && !current.ready)) && <Notice className={result === 'connected' ? 'bloq-success' : 'bloq-error'} role={result === 'connected' ? 'status' : 'alert'}>{callbackMessages[result]}</Notice>}
    {status.isLoading && <p role="status">Revisando la conexión…</p>}
    {status.isError && <Notice key={status.errorUpdatedAt}>No pudimos revisar la conexión. <button type="button" onClick={() => void status.refetch()}>Volver a intentar</button></Notice>}
    {current && !current.available && <p className="provider-account__unavailable" role="status">La conexión con cuenta Google todavía no está habilitada. {current.connected ? 'Desconectá esta cuenta si querés usar una clave API.' : 'Mientras tanto, podés usar BloqIA o una clave API en las opciones avanzadas.'}</p>}
    {current?.connected && <div className="provider-account__identity"><span className="provider-account__avatar" aria-hidden="true"><Icon name="user" size={20} /></span><div><strong>{current.email}</strong><span>{!current.available ? 'Conexión deshabilitada' : current.ready ? current.projectName : current.needsReconnect ? 'Volvé a autorizar esta cuenta' : 'Cuenta autorizada · falta un paso'}</span></div></div>}
    {current?.available && (!current.connected || current.needsReconnect) && <>
      <button type="button" className="provider-account__connect" data-primary="true" onClick={() => start.mutate()} disabled={!emailVerified || busy}>{start.isPending ? 'Abriendo Google…' : current.needsReconnect ? 'Volver a conectar Google' : 'Conectar con Google'}</button>
      {!emailVerified && <p><a href="#verificacion-correo">Verificá tu correo</a> antes de conectar una cuenta personal.</p>}
      <details className="provider-account__permissions"><summary>Qué permiso solicita Google</summary><p>Google pedirá acceso a Google Cloud. BloqIA lo usa para encontrar tus proyectos, consultar sus permisos y enviar tus consultas a Gemini. Podés retirarlo cuando quieras.</p></details>
    </>}
    {current?.ready && !changingProject && <div className="provider-account__actions"><a className="provider-account__chat" href="/nuevo-chat">Ir al chat <Icon name="arrow-up-right" size={16} /></a><button type="button" onClick={() => { setChangingProject(true); select.reset(); }}>Cambiar proyecto</button></div>}
    {choosingProject && <div className="provider-account__projects">
      <label htmlFor="google-project">Dónde usar Gemini</label>
      {projects.isLoading && <p role="status">Buscando tus proyectos…</p>}
      {projects.data && projects.data.projects.length > 0 && <>
        <select id="google-project" value={projectId} onChange={(event) => { setSelected(event.target.value); select.reset(); }} disabled={busy}>
          <option value="">Elegí un proyecto</option>
          {projects.data.projects.map((project) => <option key={project.projectId} value={project.projectId}>{project.name} · {project.projectId}</option>)}
        </select>
        <p>Google administra tu acceso y cupo en este proyecto.{projects.data.projects.length === 1 ? ' Ya lo seleccionamos por vos.' : ''}</p>
        <p className="provider-account__cost">La comprobación envía una consulta breve. Puede consumir cupo o generar un cargo según el proyecto. Google AI Pro y Ultra se administran por separado.</p>
        <button type="button" data-primary="true" onClick={() => select.mutate(projectId, { onSuccess: () => setChangingProject(false) })} disabled={!projectId || !emailVerified || busy}>{select.isPending ? 'Comprobando Gemini…' : 'Comprobar y usar Gemini'}</button>
        {!emailVerified && <p><a href="#verificacion-correo">Verificá tu correo</a> antes de completar la conexión.</p>}
      </>}
      {projects.data?.projects.length === 0 && <p>Tu cuenta todavía no tiene proyectos disponibles. Abrí Google AI Studio y creá uno para usar Gemini; después actualizá esta lista.</p>}
      <div className="provider-account__links"><a href={enableUrl} target="_blank" rel="noopener noreferrer">Preparar Gemini en Google <Icon name="arrow-up-right" size={14} /></a><button type="button" onClick={() => void projects.refetch()} disabled={projects.isFetching || busy}>Actualizar proyectos</button></div>
      {projects.isError && <Notice key={projects.errorUpdatedAt}>{projects.error instanceof Error ? projects.error.message : 'No pudimos buscar tus proyectos.'}</Notice>}
      {changingProject && <button type="button" onClick={() => { setSelected(''); setChangingProject(false); select.reset(); }} disabled={busy}>Cancelar cambio</button>}
    </div>}
    {!choosingProject && <p className="provider-account__cost">Gemini usa el cupo y la facturación del proyecto elegido; Google puede cobrar según su plan. Google AI Pro y Ultra se administran por separado.</p>}
    {select.isSuccess && <Notice key={select.submittedAt} className="bloq-success" role="status">Google aceptó la prueba. Ya podés elegir Gemini en el chat; los cupos pueden cambiar.</Notice>}
    {error && <Notice key={error.submittedAt}>{error.error instanceof Error ? error.error.message : 'No pudimos completar la conexión. Volvé a intentarlo.'}</Notice>}
    {disconnect.isSuccess && !disconnect.data.revoked && <Notice className="bloq-error">La cuenta se quitó de BloqIA, pero Google no confirmó la revocación. <a href="https://myaccount.google.com/connections" target="_blank" rel="noopener noreferrer">Retirá el acceso en Google</a>.</Notice>}
    {current?.connected && <button type="button" className="provider-account__disconnect" onClick={() => disconnect.mutate(undefined, { onSuccess: () => { setSelected(''); setChangingProject(false); select.reset(); start.reset(); } })} disabled={busy}>{disconnect.isPending ? 'Desconectando…' : 'Desconectar cuenta Google'}</button>}
  </div>;
}
