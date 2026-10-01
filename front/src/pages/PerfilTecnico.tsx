import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ChasisBloqIA } from '../components/chasis/ChasisBloqIA';
import { usePerfilTecnico } from '../features/usuario/usePerfilTecnico';
import { listAvailableModels } from '../api/technicalProfile';
import type { AIModel, ProviderWithModels } from '../types/dominio';

const guides: Record<string, { tier: string; detail: string; keys: string; conditions: string }> = {
  google: { tier: 'Nivel gratuito', detail: 'Usá tu cuenta Google en AI Studio y una clave de un proyecto Free Tier. Los cupos dependen del modelo.', keys: 'https://aistudio.google.com/app/apikey', conditions: 'https://ai.google.dev/gemini-api/docs/pricing' },
  groq: { tier: 'Plan gratuito', detail: 'Groq ofrece un plan gratuito con límites por modelo. Revisá el plan de tu cuenta antes de usar la clave.', keys: 'https://console.groq.com/keys', conditions: 'https://console.groq.com/docs/rate-limits' },
  openrouter: { tier: 'Modelos gratuitos', detail: 'BloqIA muestra y envía sólo a rutas gratuitas de OpenRouter. El plan gratis tiene un cupo diario.', keys: 'https://openrouter.ai/settings/keys', conditions: 'https://openrouter.ai/pricing' },
  openai: { tier: 'API con facturación propia', detail: 'Una clave de la plataforma OpenAI usa tu proyecto de API. El plan ChatGPT Plus o Pro utiliza otra conexión.', keys: 'https://platform.openai.com/api-keys', conditions: 'https://developers.openai.com/api/docs/pricing' },
  anthropic: { tier: 'API con facturación propia', detail: 'La clave de Anthropic usa la cuenta de API y sus condiciones de facturación.', keys: 'https://console.anthropic.com/settings/keys', conditions: 'https://docs.anthropic.com/en/docs/about-claude/pricing' }
};
const providerOrder = ['google', 'groq', 'openrouter', 'openai', 'anthropic'];

function providerLabel(provider: ProviderWithModels) {
  const known: Record<string, string> = { google: 'Google AI', groq: 'Groq', openrouter: 'OpenRouter', openai: 'OpenAI', anthropic: 'Anthropic' };
  return known[provider.providerId] ?? provider.name.replace(/\s*·\s*/g, ', ');
}

function modelPurpose(providerId: string, model: AIModel) {
  if (providerId === 'openrouter') return 'Ruta gratuita de OpenRouter, sujeta a los límites de tu cuenta';
  if (providerId === 'groq') return 'Modelo de Groq; verificá el cupo de tu plan';
  if (providerId === 'anthropic') {
    if (model.modelId.includes('opus')) return 'Análisis profundo y tareas complejas';
    if (model.modelId.includes('sonnet')) return 'Equilibrio para trabajo diario y código';
    return 'Respuestas ágiles para tareas frecuentes';
  }
  if (providerId === 'openai' && model.modelId.includes('oss')) return 'Pesos abiertos para ejecutar en tu propia infraestructura';
  if (providerId === 'openai') return 'Modelo disponible para tu proyecto de OpenAI';
  return 'Modelo disponible en el catálogo del proveedor';
}

function ModelCatalog({ provider, models }: { provider: ProviderWithModels; models: AIModel[] }) {
  const [showAll, setShowAll] = useState(false);
  const initialModelCount = 3;
  const visibleModels = showAll ? models : models.slice(0, initialModelCount);
  const hiddenModelCount = Math.max(0, models.length - initialModelCount);
  return <div className="model-catalog" aria-label={`Modelos de ${providerLabel(provider)}`}>
    <p className="model-catalog__recency">{showAll || hiddenModelCount === 0 ? `${models.length} modelos en catálogo` : `Mostrando ${visibleModels.length} de ${models.length} modelos`}</p>
    {visibleModels.map((model) => <article className="model-card" key={model.modelId}>
      <div className="model-card__content">
        <div className="model-card__heading">
          <div><h4>{model.displayName}</h4><code className="model-id">{model.modelId}</code></div>
          <span className="model-availability">En catálogo</span>
        </div>
        <p>{modelPurpose(provider.providerId, model)}</p>
        <div className="model-meta">{model.capabilities.map((capability) => <span className="model-chip" key={capability}>{capability}</span>)}</div>
      </div>
    </article>)}
    {hiddenModelCount > 0 && <button type="button" className="model-more-button" onClick={() => setShowAll((current) => !current)} aria-expanded={showAll}>
      {showAll ? 'Mostrar menos' : `Ver ${hiddenModelCount} modelos más`}
    </button>}
  </div>;
}

function ProviderSection({ provider, token, setToken, save, remove }: {
  provider: ProviderWithModels;
  token: string;
  setToken: (value: string) => void;
  save: ReturnType<typeof usePerfilTecnico>['save'];
  remove: ReturnType<typeof usePerfilTecnico>['remove'];
}) {
  const guide = guides[provider.providerId];
  const catalog = useQuery({
    queryKey: ['available-models', provider.providerId],
    queryFn: () => listAvailableModels(provider.providerId),
    retry: false
  });
  const configured = provider.tokenStatus.status === 'configured';
  const displayedModels = catalog.data?.models ?? provider.models;
  const saving = save.isPending && save.variables?.providerId === provider.providerId;
  const removing = remove.isPending && remove.variables === provider.providerId;

  return <section className="provider-section" id={`provider-${provider.providerId}`}>
    <header className="provider-section__header">
      <div><h2>{providerLabel(provider)}</h2></div>
      {guide && <span className="provider-tier">{guide.tier}</span>}
    </header>
    {guide && <div className="provider-guide"><p>{guide.detail}</p><div className="provider-guide__links"><a href={guide.keys} target="_blank" rel="noopener noreferrer">Abrir consola de claves <span aria-hidden="true">↗</span></a><a href={guide.conditions} target="_blank" rel="noopener noreferrer">Ver condiciones y cupos <span aria-hidden="true">↗</span></a></div></div>}
    <div className="provider-connection">
      <div><span>Clave personal de API</span><strong>{configured ? `Guardada: ${provider.tokenStatus.maskedTokenLabel ?? '••••'}` : 'Sin clave configurada'}</strong></div>
    </div>
    <div className="model-catalog__header"><h3>Modelos del proveedor</h3><button type="button" className="model-refresh" onClick={() => void catalog.refetch()} disabled={catalog.isFetching}>Actualizar catálogo</button></div>
    {catalog.isFetching && <p role="status">Cargando modelos...</p>}
    {catalog.isError && <p className="bloq-error">No se pudo consultar el catálogo. Revisá la clave y volvé a intentar.</p>}
    {catalog.data && <p className="model-catalog__note" data-state={catalog.data.source === 'token' ? 'safe' : 'attention'}>{catalog.data.message}</p>}
    {displayedModels.length > 0 && <ModelCatalog provider={provider} models={displayedModels} />}
    <label className="provider-token-field"><span>Clave API de {providerLabel(provider)}</span><input aria-label={`Clave API ${providerLabel(provider)}`} value={token} onChange={(event) => setToken(event.target.value)} placeholder="Pegá tu clave API personal" type="password" autoComplete="off" spellCheck={false} /></label>
    <p className="provider-secret-help">Pegá una clave API de este proveedor. No ingreses tu contraseña de Google, ChatGPT ni Claude.</p>
    <div className="bloq-actions"><button type="button" onClick={() => remove.mutate(provider.providerId)} disabled={!configured || removing}>Quitar clave</button><button type="button" data-primary="true" onClick={() => save.mutate({ providerId: provider.providerId, token: token.trim() }, { onSuccess: () => setToken('') })} disabled={!token.trim() || saving}>{saving ? 'Guardando…' : 'Conectar clave'}</button></div>
  </section>;
}

export function PerfilTecnico() {
  const { providers, save, remove } = usePerfilTecnico();
  const [tokenByProvider, setTokenByProvider] = useState<Record<string, string>>({});
  const orderedProviders = [...(providers.data?.providers ?? [])].sort((first, second) => {
    const a = providerOrder.indexOf(first.providerId);
    const b = providerOrder.indexOf(second.providerId);
    return (a < 0 ? providerOrder.length : a) - (b < 0 ? providerOrder.length : b);
  });

  return <ChasisBloqIA title="Perfil técnico" activePath="/perfil-tecnico" contentClassName="technical-profile-content">
    <div className="technical-intro"><p className="provider-eyebrow">Configuración</p><h1>Proveedores y modelos</h1><p>Elegí cómo querés generar respuestas. Conectá cada proveedor con una clave API de tu propia cuenta.</p></div>
    <div className="provider-free-summary" aria-label="Opciones de uso gratuito">
      <div><strong>Qwen local</strong><span>Sin cuenta ni clave</span><a href="/nuevo-chat">Usar en el chat</a></div>
      <div><strong>Gemini</strong><span>Nivel gratuito según modelo</span><a href="#provider-google">Configurar</a></div>
      <div><strong>Groq</strong><span>Plan gratuito con cupos</span><a href="#provider-groq">Configurar</a></div>
      <div><strong>OpenRouter</strong><span>Rutas gratuitas</span><a href="#provider-openrouter">Configurar</a></div>
    </div>
    <p className="provider-free-disclaimer">Los cupos y modelos pueden cambiar. Consultá las condiciones actuales de cada proveedor antes de enviar peticiones.</p>
    {providers.isLoading && <p>Cargando proveedores...</p>}
    {providers.isError && <p className="bloq-error">No se pudieron cargar los proveedores.</p>}
    {orderedProviders.map((provider) => <ProviderSection key={provider.providerId} provider={provider} token={tokenByProvider[provider.providerId] ?? ''} setToken={(value) => setTokenByProvider((current) => ({ ...current, [provider.providerId]: value }))} save={save} remove={remove} />)}
    {save.isError && <p className="bloq-error">No se pudo guardar la clave.</p>}
    {save.isSuccess && <p className="bloq-success">Clave guardada. El catálogo mostrará los modelos disponibles para esta credencial.</p>}
  </ChasisBloqIA>;
}
