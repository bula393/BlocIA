import { useState } from 'react';
import { ChasisBloqIA } from '../components/chasis/ChasisBloqIA';
import { usePerfilTecnico } from '../features/usuario/usePerfilTecnico';
import type { AIModel, ProviderWithModels } from '../types/dominio';

function modelPurpose(providerId: string, model: AIModel) {
  if (providerId === 'anthropic') {
    if (model.modelId.includes('opus')) return 'Análisis profundo y tareas complejas';
    if (model.modelId.includes('sonnet')) return 'Equilibrio para trabajo diario y código';
    return 'Respuestas ágiles para tareas frecuentes';
  }
  if (providerId === 'openai' && model.modelId.includes('oss')) return 'Modelo abierto para ejecutar en tu propia infraestructura';
  if (providerId === 'openai') return 'Modelo disponible para tu proyecto de OpenAI';
  return 'Modelo disponible en el catálogo del proveedor';
}

function ModelCatalog({ provider, models }: { provider: ProviderWithModels; models: AIModel[] }) {
  const brand = provider.providerId === 'anthropic' ? 'C' : provider.providerId === 'openai' ? 'G' : 'AI';
  const [showAll, setShowAll] = useState(false);
  const initialModelCount = 3;
  const visibleModels = showAll ? models : models.slice(0, initialModelCount);
  const hiddenModelCount = Math.max(0, models.length - initialModelCount);
  return <div className="model-catalog" aria-label={`Modelos de ${provider.name}`}>
    <p className="model-catalog__recency">{showAll || hiddenModelCount === 0 ? `${models.length} modelos disponibles` : `Mostrando los ${visibleModels.length} más nuevos`}</p>
    {visibleModels.map((model) => <article className="model-card" key={model.modelId}>
      <div className="model-brand" aria-hidden="true">{brand}</div>
      <div className="model-card__content">
        <div className="model-card__heading">
          <div><h4>{model.displayName}</h4><code className="model-id">{model.modelId}</code></div>
          <span className="model-availability">Disponible</span>
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

export function PerfilTecnico() {
  const { providers, availableModels, save, remove } = usePerfilTecnico();
  const [tokenByProvider, setTokenByProvider] = useState<Record<string, string>>({});

  return <ChasisBloqIA title="Perfil técnico" activePath="/perfil-tecnico">
    <div className="technical-intro"><p className="provider-eyebrow">Configuración</p><h1>Proveedores y modelos</h1><p>Conectá tus claves y elegí con claridad qué capacidades tiene cada modelo.</p></div>
    {providers.isLoading && <p>Cargando proveedores...</p>}
    {providers.isError && <p className="bloq-error">No se pudieron cargar los proveedores.</p>}
    {providers.data?.providers.map((provider) => {
      const displayedModels = provider.providerId === 'openai' ? availableModels.data?.models : provider.models;
      return <section className="provider-section" key={provider.providerId}>
        <header className="provider-section__header">
          <div><p className="provider-eyebrow">Proveedor de IA</p><h2>{provider.name}</h2><p className="provider-description">{provider.description ?? 'Conectá tu token para usar este proveedor.'}</p></div>
          <span className="provider-status">{provider.status === 'available' ? 'Disponible' : provider.status}</span>
        </header>
        <div className="provider-connection">
          <div><span>Conexión</span><strong>{provider.tokenStatus.status === 'configured' ? `Token conectado · ${provider.tokenStatus.maskedTokenLabel ?? ''}` : 'Sin token configurado'}</strong></div>
          <span className="connection-dot" data-state={provider.tokenStatus.status === 'configured' ? 'safe' : 'attention'} aria-label={provider.tokenStatus.status === 'configured' ? 'Token conectado' : 'Token sin configurar'} />
        </div>
        <div className="model-catalog__header"><div><p className="provider-eyebrow">Biblioteca</p><h3>Modelos disponibles</h3></div>{provider.providerId === 'openai' && <button type="button" className="model-refresh" onClick={() => availableModels.refetch()}>Actualizar</button>}</div>
        {provider.providerId === 'openai' && availableModels.isLoading && <p>Cargando modelos...</p>}
        {provider.providerId === 'openai' && availableModels.isError && <p className="bloq-error">No se pudieron consultar los modelos. Revisá el token e intentá de nuevo.</p>}
        {provider.providerId === 'openai' && availableModels.data && <p className="model-catalog__note" data-state={availableModels.data.source === 'token' ? 'safe' : 'attention'}>{availableModels.data.message}</p>}
        {displayedModels && <ModelCatalog provider={provider} models={displayedModels} />}
        <label className="provider-token-field"><span>Token de {provider.name}</span><input aria-label={`Token ${provider.name}`} value={tokenByProvider[provider.providerId] ?? ''} onChange={(event) => setTokenByProvider({ ...tokenByProvider, [provider.providerId]: event.target.value })} placeholder="Pegá tu token de API" type="password" autoComplete="off" /></label>
        <div className="bloq-actions"><button type="button" onClick={() => remove.mutate(provider.providerId)} disabled={provider.tokenStatus.status !== 'configured'}>Quitar token</button><button type="button" data-primary="true" onClick={() => save.mutate({ providerId: provider.providerId, token: tokenByProvider[provider.providerId] ?? '' })}>Conectar token</button></div>
      </section>;
    })}
    {save.isError && <p className="bloq-error">No se pudo guardar el token.</p>}
    {save.isSuccess && <p className="bloq-success">Token actualizado.</p>}
  </ChasisBloqIA>;
}
