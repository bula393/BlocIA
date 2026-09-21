import { useState } from 'react';
import { ChasisBloqIA } from '../components/chasis/ChasisBloqIA';
import { usePerfilTecnico } from '../features/usuario/usePerfilTecnico';

export function PerfilTecnico() {
  const { providers, save, remove } = usePerfilTecnico();
  const [tokenByProvider, setTokenByProvider] = useState<Record<string, string>>({});

  return (
    <ChasisBloqIA title="Perfil tecnico" activePath="/perfil-tecnico">
      <h1>Perfil tecnico</h1>
      {providers.isLoading && <p>Cargando proveedores...</p>}
      {providers.isError && <p className="bloq-error">No se pudieron cargar los proveedores.</p>}
      {providers.data?.providers.map((provider) => (
        <section className="bloq-section" key={provider.providerId}>
          <h2>{provider.name}</h2>
          <p className="bloq-status-line">Estado proveedor: {provider.status}</p>
          <p className="bloq-status-line" data-state={provider.tokenStatus.status === 'configured' ? 'safe' : 'attention'}>Token: {provider.tokenStatus.status} {provider.tokenStatus.maskedTokenLabel ?? ''}</p>
          <ul>
            {provider.models.map((model) => <li key={model.modelId}>{model.displayName} - {model.availabilityStatus}</li>)}
          </ul>
          <input
            aria-label={`Token ${provider.name}`}
            value={tokenByProvider[provider.providerId] ?? ''}
            onChange={(event) => setTokenByProvider({ ...tokenByProvider, [provider.providerId]: event.target.value })}
            placeholder="Token del proveedor"
          />
          <div className="bloq-actions">
            <button type="button" onClick={() => remove.mutate(provider.providerId)}>Eliminar token</button>
            <button type="button" data-primary="true" onClick={() => save.mutate({ providerId: provider.providerId, token: tokenByProvider[provider.providerId] ?? '' })}>Guardar token</button>
          </div>
        </section>
      ))}
      {save.isError && <p className="bloq-error">No se pudo guardar el token.</p>}
      {save.isSuccess && <p className="bloq-success">Token actualizado.</p>}
    </ChasisBloqIA>
  );
}
