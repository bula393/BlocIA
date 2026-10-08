import { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getUsageDashboard, type UsageDashboard } from '../api/usage';
import { ChasisBloqIA } from '../components/chasis/ChasisBloqIA';
import { Icon } from '../mockup/brand';

const pageSize = 40;
const categories: Array<{ id: string; name: string; color: string }> = [
  { id: 'no_personal', name: 'Consultas generales', color: 'blue' },
  { id: 'personal_informativa', name: 'Análisis personales', color: 'amber' },
  { id: 'personal_decision', name: 'Decisiones personales', color: 'coral' },
  { id: 'unclassified', name: 'Sin clasificación', color: 'muted' },
];
const providerNames: Record<string, string> = {
  google: 'Google AI', groq: 'Groq', openrouter: 'OpenRouter', openai: 'OpenAI', anthropic: 'Anthropic', local: 'En este equipo', none: 'Respuesta propia de BloqIA',
};
const reasonNames: Record<string, string> = {
  usage_time: 'Alcanzaste el límite de 3 horas de uso de IA.',
  personal_questions: 'Alcanzaste el límite de 3 consultas personales durante las últimas 24 horas.',
};

function formatDuration(seconds: number) {
  const wholeMinutes = Math.floor(Math.max(0, seconds) / 60);
  const hours = Math.floor(wholeMinutes / 60);
  const minutes = wholeMinutes % 60;
  if (hours) return `${hours} h ${String(minutes).padStart(2, '0')} min`;
  if (wholeMinutes) return `${wholeMinutes} min`;
  return `${Math.max(0, Math.round(seconds))} s`;
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat('es-AR', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(value));
}

function weekSeries(rows: UsageDashboard['summary']['lastSevenDays']) {
  const byDate = new Map(rows.map((row) => [row.date, row]));
  const today = new Date();
  const dates = Array.from({ length: 7 }, (_, index) => {
    const date = new Date(Date.UTC(today.getUTCFullYear(), today.getUTCMonth(), today.getUTCDate() - 6 + index));
    const key = date.toISOString().slice(0, 10);
    const value = byDate.get(key);
    return { date: key, count: value?.count ?? 0, personal: value?.personal ?? 0, label: new Intl.DateTimeFormat('es-AR', { weekday: 'short', timeZone: 'UTC' }).format(date).replace('.', '') };
  });
  return dates;
}

export function Actividad() {
  const [offset, setOffset] = useState(0);
  const [activity, setActivity] = useState<UsageDashboard['activity']['items']>([]);
  const dashboard = useQuery({ queryKey: ['usage-dashboard', offset], queryFn: ({ signal }) => getUsageDashboard(pageSize, offset, signal), retry: false, refetchInterval: 30_000, placeholderData: (previous) => previous });

  useEffect(() => {
    const page = dashboard.data?.activity;
    if (!page || page.offset !== offset) return;
    setActivity((previous) => offset === 0 ? page.items : [...previous, ...page.items]);
  }, [dashboard.data, offset]);

  const data = dashboard.data;
  const lockDurationMinutes = data?.limits.lockDurationMinutes ?? 1440;
  const lockDuration = lockDurationMinutes % 60 === 0 ? `${lockDurationMinutes / 60} ${lockDurationMinutes === 60 ? 'hora' : 'horas'}` : `${lockDurationMinutes} ${lockDurationMinutes === 1 ? 'minuto' : 'minutos'}`;
  const daily = data ? weekSeries(data.summary.lastSevenDays) : [];
  const peakDay = Math.max(1, ...daily.map((day) => day.count));
  const usagePercent = data ? Math.min(100, Math.round(data.limits.usageSeconds / data.limits.usageLimitSeconds * 100)) : 0;
  const categoryTotal = data ? Object.values(data.summary.categoryCounts).reduce((sum, count) => sum + count, 0) : 0;

  function refresh() {
    setActivity([]);
    if (offset !== 0) setOffset(0);
    else void dashboard.refetch();
  }

  return <ChasisBloqIA title="Actividad" activePath="/actividad" contentClassName="usage-content">
    <div className="usage-page usage-dashboard">
      <header className="usage-heading">
        <div><p className="provider-eyebrow">Tu espacio · datos privados</p><h1>Actividad y límites</h1><p>Una vista completa de tus consultas, categorías y uso reciente.</p></div>
        <button className="usage-refresh" type="button" onClick={refresh} disabled={dashboard.isFetching}><Icon name="refresh" size={16} />{dashboard.isFetching ? 'Actualizando…' : 'Actualizar'}</button>
      </header>
      {dashboard.isLoading && <p role="status" className="usage-state">Cargando tu actividad…</p>}
      {dashboard.isError && <div className="usage-error" role="alert"><p>No se pudo cargar el tablero de actividad.</p><button type="button" onClick={() => void dashboard.refetch()}>Intentar de nuevo</button></div>}
      {data && <>
        {data.limits.blocked && <section className="usage-lock-banner" role="status">
          <span className="usage-lock-symbol"><Icon name="lock" size={21} /></span>
          <div><p className="usage-lock-kicker">Pausa de seguridad · {lockDuration}</p><h2>La IA está bloqueada</h2>
            {data.limits.reasonCodes.map((reason) => <p key={reason}>{reasonNames[reason] ?? 'Se alcanzó un límite de uso.'}</p>)}
            <small>El acceso se restablece {data.limits.lockUntil ? formatDate(data.limits.lockUntil) : 'cuando termina el período de bloqueo'}.</small>
          </div>
          <strong>{lockDuration}</strong>
        </section>}
        <section className="usage-metrics usage-metrics--four" aria-label="Indicadores principales">
          <article><span>Uso de IA · últimas 24 h</span><strong>{formatDuration(data.limits.usageSeconds)}</strong><small>Tiempo acumulado de clasificación y respuesta.</small></article>
          <article><span>Consultas personales · 24 h</span><strong>{data.limits.personalQuestions}<i> / {data.limits.personalQuestionLimit}</i></strong><small>Consultas informativas y de decisión.</small></article>
          <article><span>Consultas guardadas</span><strong>{data.summary.totalQueries}</strong><small>Todo el historial disponible en tu cuenta.</small></article>
          <article><span>Clasificaciones</span><strong>{data.summary.classifiedQueries}</strong><small>Consultas con una categoría asignada.</small></article>
        </section>

        <section className="usage-insight-grid" aria-label="Análisis de actividad">
          <article className="usage-insight usage-time-card">
            <header><div><p className="usage-section-kicker">LÍMITE DE USO</p><h2>Tiempo de IA</h2></div><span className="usage-meter-value">{usagePercent}%</span></header>
            <div className="usage-meter-track" role="progressbar" aria-label="Uso de IA de las últimas 24 horas" aria-valuenow={usagePercent} aria-valuemin={0} aria-valuemax={100}><span data-blocked={data.limits.blocked} style={{ width: `${usagePercent}%` }} /></div>
            <div className="usage-meter-labels"><span>{formatDuration(data.limits.usageSeconds)} usados</span><span>3 h disponibles</span></div>
            <p>El contador considera el tiempo empleado en clasificar y preparar las respuestas. Se calcula sobre las últimas 24 horas.</p>
          </article>

          <article className="usage-insight usage-trend-card">
            <header><div><p className="usage-section-kicker">RITMO</p><h2>Últimos 7 días</h2></div><span>{daily.reduce((sum, day) => sum + day.count, 0)} consultas</span></header>
            <div className="usage-week-chart" role="img" aria-label="Consultas por día durante los últimos siete días">
              {daily.map((day) => <div className="usage-week-day" key={day.date} title={`${day.count} consultas · ${day.personal} personales`}><div className="usage-week-bar"><span data-personal={day.personal > 0} style={{ height: `${day.count ? Math.max(8, day.count / peakDay * 100) : 0}%` }} /></div><small>{day.label}</small></div>)}
            </div>
          </article>

          <article className="usage-insight usage-category-card">
            <header><div><p className="usage-section-kicker">CLASIFICACIÓN</p><h2>Tipos de consulta</h2></div><span>{categoryTotal} total</span></header>
            <div className="usage-category-list">{categories.map((category) => {
              const count = data.summary.categoryCounts[category.id] ?? 0;
              const percent = categoryTotal ? Math.round(count / categoryTotal * 100) : 0;
              return <div className="usage-category-row" data-color={category.color} key={category.id}><div><span>{category.name}</span><strong>{count}</strong></div><div className="usage-category-track"><span style={{ width: `${percent}%` }} /></div><small>{percent}%</small></div>;
            })}</div>
          </article>

          <article className="usage-insight usage-provider-card">
            <header><div><p className="usage-section-kicker">CONEXIONES</p><h2>Proveedores usados</h2></div><Icon name="layers" size={18} /></header>
            {data.summary.providerCounts.length === 0 ? <p className="usage-empty-note">Tus proveedores aparecerán cuando completes una consulta.</p> : <div className="usage-provider-list">{data.summary.providerCounts.map((provider) => <div key={provider.providerId}><span className="usage-provider-dot" data-provider={provider.providerId} /><span>{providerNames[provider.providerId] ?? provider.providerId}</span><strong>{provider.count}</strong></div>)}</div>}
          </article>
        </section>

        <section className="usage-history" aria-label="Historial completo de consultas">
          <header className="usage-history-heading"><div><p className="usage-section-kicker">REGISTRO COMPLETO</p><h2>Todas tus consultas</h2><p>Se muestran {activity.length} de {data.activity.total} consultas, de la más reciente a la más antigua.</p></div><span className="usage-history-count">{data.activity.total}<small> consultas</small></span></header>
          {activity.length === 0 ? <div className="usage-empty"><span><Icon name="activity" size={21} /></span><h3>Tu actividad empieza acá</h3><p>Cuando envíes tu primera consulta, vas a encontrar el detalle y su clasificación en esta sección.</p></div> : <div className="usage-history-list">{activity.map((item, index) => {
            const category = item.classification?.label ?? 'unclassified';
            const categoryName = categories.find((row) => row.id === category)?.name ?? 'Sin clasificación';
            return <a className="usage-history-item" href={`/nuevo-chat?chat=${encodeURIComponent(item.conversationId)}`} key={`${item.conversationId}-${item.createdAt}-${index}`}>
              <span className="usage-log-index">{String(data.activity.total - index - 1).padStart(2, '0')}</span>
              <span className="usage-log-main"><span className="usage-log-meta"><span className="usage-category-pill" data-category={category}>{categoryName}{item.classification?.confidence !== undefined ? ` · ${Math.round(item.classification.confidence * 100)}%` : ''}</span>{item.classification?.needs_human_review && <span className="usage-review-pill">Revisión</span>}<time dateTime={item.createdAt}>{formatDate(item.createdAt)}</time></span><strong>{item.prompt}</strong><small>{item.conversationTitle}</small></span>
              <span className="usage-log-detail"><span>{providerNames[item.providerId ?? 'none'] ?? item.providerId}</span><small>{item.modelId ?? 'Sin modelo externo'} · {formatDuration(item.durationSeconds)}</small></span>
              <Icon name="arrow-up-right" size={16} />
            </a>;
          })}</div>}
          {data.activity.hasMore && <button className="usage-load-more" type="button" onClick={() => setOffset((current) => current + pageSize)} disabled={dashboard.isFetching}><Icon name="down" size={15} />{dashboard.isFetching ? 'Cargando…' : 'Cargar consultas anteriores'}</button>}
        </section>
        <footer className="usage-next-step"><div><h2>¿Seguimos pensando?</h2><p>Volvé a una conversación o abrí una pregunta nueva.</p></div><a className="bloq-button" data-primary="true" href="/nuevo-chat">Abrir el chat <Icon name="arrow" size={17} /></a></footer>
      </>}
    </div>
  </ChasisBloqIA>;
}
