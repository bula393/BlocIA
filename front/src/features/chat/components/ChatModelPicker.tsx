import type { ChatController } from '../useChatController';

export function ChatModelPicker({ chat }: { chat: ChatController }) {
  const { usageLock, selectedModel, selectModel, modelOptions, interactionPending, loading, modelsLoading, providerQueryError, providerTokenAvailable, failedCatalogs } = chat;
  return <>
            {!usageLock?.blocked && <div className="chat-model-picker">
              <label htmlFor="chat-model">Modelo de respuesta</label>
              <select id="chat-model" value={selectedModel} onChange={(event) => selectModel(event.target.value)} disabled={!modelOptions.length || interactionPending || loading || usageLock?.blocked}>
                {modelOptions.length === 0 && <option value="">Sin modelo conectado</option>}
                {modelOptions.map((model) => <option value={model.key} key={model.key}>{model.displayName} — {model.providerName}</option>)}
              </select>
              {modelOptions.length === 0 && <small>{modelsLoading ? 'Buscando modelos…' : providerQueryError ? 'No se pudieron cargar tus proveedores.' : providerTokenAvailable ? 'No hay modelos disponibles para las claves conectadas. Revisá tu Perfil técnico.' : <>Conectá un proveedor desde <a href="/perfil-tecnico">Perfil técnico</a> para generar respuestas.</>}</small>}
              {failedCatalogs.length > 0 && <small className="bloq-error">No se pudieron cargar modelos. {failedCatalogs.join('; ')} Podés usar Qwen local si está instalado.</small>}
            </div>}
  </>;
}
