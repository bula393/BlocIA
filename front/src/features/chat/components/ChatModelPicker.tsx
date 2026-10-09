import { useEffect, useId, useMemo, useRef, useState, type KeyboardEvent } from 'react';
import type { ChatController } from '../useChatController';
import type { ChatModelOption } from '../types';
import { Icon } from '../../../mockup/brand';

export function ChatModelPicker({ chat }: { chat: ChatController }) {
  const {
    usageLock, selectedModel, selectedModelDisplay, selectModel, modelOptions, interactionPending, loading,
    modelsLoading, providerQueryError, providerTokenAvailable, failedCatalogs, modelSelectionMessage
  } = chat;
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const pickerId = useId();
  const pickerRef = useRef<HTMLDivElement>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const searchRef = useRef<HTMLInputElement>(null);
  const optionRefs = useRef<Array<HTMLButtonElement | null>>([]);
  const disabled = !modelOptions.length || interactionPending || loading || Boolean(usageLock?.blocked);
  const filteredOptions = useMemo(() => {
    const normalizedQuery = query.trim().toLocaleLowerCase('es-AR');
    if (!normalizedQuery) return modelOptions;
    return modelOptions.filter((model) =>
      `${model.displayName} ${model.modelId} ${model.providerName}`.toLocaleLowerCase('es-AR').includes(normalizedQuery)
    );
  }, [modelOptions, query]);

  useEffect(() => {
    if (open) searchRef.current?.focus();
  }, [open]);

  useEffect(() => {
    if (disabled) {
      setOpen(false);
      setQuery('');
    }
  }, [disabled]);

  useEffect(() => {
    if (!open) return;
    function onPointerDown(event: PointerEvent) {
      if (!pickerRef.current?.contains(event.target as Node)) {
        setOpen(false);
        setQuery('');
      }
    }
    function onKeyDown(event: globalThis.KeyboardEvent) {
      if (event.key === 'Escape') {
        event.preventDefault();
        setOpen(false);
        setQuery('');
        triggerRef.current?.focus();
      }
    }
    document.addEventListener('pointerdown', onPointerDown);
    document.addEventListener('keydown', onKeyDown);
    return () => {
      document.removeEventListener('pointerdown', onPointerDown);
      document.removeEventListener('keydown', onKeyDown);
    };
  }, [open]);

  function focusOption(index: number) {
    optionRefs.current[index]?.focus();
  }

  function handleSearchKeyDown(event: KeyboardEvent<HTMLInputElement>) {
    if (event.key === 'Enter') {
      // Keep Enter from submitting the surrounding message form while searching.
      event.preventDefault();
    } else if (event.key === 'ArrowDown' && filteredOptions.length) {
      event.preventDefault();
      focusOption(0);
    }
  }

  function handleOptionKeyDown(event: KeyboardEvent<HTMLButtonElement>, index: number) {
    if (event.key === 'ArrowDown') {
      event.preventDefault();
      focusOption(Math.min(index + 1, filteredOptions.length - 1));
    } else if (event.key === 'ArrowUp') {
      event.preventDefault();
      if (index === 0) searchRef.current?.focus();
      else focusOption(index - 1);
    } else if (event.key === 'Home') {
      event.preventDefault();
      focusOption(0);
    } else if (event.key === 'End') {
      event.preventDefault();
      focusOption(filteredOptions.length - 1);
    }
  }

  function chooseModel(model: ChatModelOption) {
    selectModel(model.key);
    setOpen(false);
    setQuery('');
    triggerRef.current?.focus();
  }

  function togglePicker() {
    if (open) setQuery('');
    setOpen(!open);
  }

  if (usageLock?.blocked) return null;

  return <div className="chat-model-picker" ref={pickerRef}>
    <span className="chat-model-picker-label" id={`${pickerId}-label`}>Modelo de respuesta</span>
    <button
      ref={triggerRef}
      type="button"
      className="chat-model-trigger"
      role="combobox"
      aria-label="Modelo de respuesta"
      aria-labelledby={`${pickerId}-label`}
      aria-haspopup="listbox"
      aria-expanded={open}
      aria-controls={`${pickerId}-listbox`}
      aria-describedby={modelSelectionMessage ? `${pickerId}-selection-message` : undefined}
      disabled={disabled}
      onClick={togglePicker}
      onKeyDown={(event) => {
        if (event.key === 'ArrowDown' && !open) {
          event.preventDefault();
          setOpen(true);
        }
      }}
    >
      <span className="chat-model-trigger-icon"><Icon name="layers" size={16} /></span>
      <span className="chat-model-trigger-copy">
        <strong>{selectedModelDisplay.displayName}</strong>
        <small>{selectedModelDisplay.providerName} · {selectedModelDisplay.modelId}</small>
      </span>
      <span className="chat-model-trigger-action">Cambiar</span>
      <Icon name="chevron-down" size={16} />
    </button>

    {open && <div className="chat-model-popover" onBlurCapture={(event) => {
      if (!event.currentTarget.parentElement?.contains(event.relatedTarget as Node | null)) {
        setOpen(false);
        setQuery('');
      }
    }}>
      <label className="chat-model-search">
        <Icon name="search" size={16} />
        <input
          ref={searchRef}
          type="search"
          value={query}
          aria-label="Buscar un modelo"
          placeholder="Buscar por modelo o proveedor"
          onChange={(event) => setQuery(event.target.value)}
          onKeyDown={handleSearchKeyDown}
        />
        <kbd>Esc</kbd>
      </label>
      <div className="chat-model-options" id={`${pickerId}-listbox`} role="listbox" aria-labelledby={`${pickerId}-label`}>
        {filteredOptions.map((model, index) => <button
          key={model.key}
          ref={(element) => { optionRefs.current[index] = element; }}
          type="button"
          role="option"
          aria-selected={model.key === selectedModel}
          className="chat-model-option"
          onClick={() => chooseModel(model)}
          onKeyDown={(event) => handleOptionKeyDown(event, index)}
        >
          <span className="chat-model-option-mark" aria-hidden="true">{model.providerName.slice(0, 1).toLocaleUpperCase('es-AR')}</span>
          <span className="chat-model-option-copy"><strong>{model.displayName}</strong><small>{model.providerName} · {model.modelId}</small></span>
          {model.key === selectedModel && <Icon name="check" size={16} />}
        </button>)}
        {filteredOptions.length === 0 && <p className="chat-model-empty">No encontramos modelos con “{query}”.</p>}
      </div>
      <div className="chat-model-popover-foot"><span>{filteredOptions.length} {filteredOptions.length === 1 ? 'modelo disponible' : 'modelos disponibles'}</span><span>↑ ↓ para recorrer</span></div>
    </div>}

    {modelSelectionMessage && <small id={`${pickerId}-selection-message`} className="chat-model-message" role="status" aria-live="polite">{modelSelectionMessage}</small>}
    {modelOptions.length === 0 && !modelSelectionMessage && <small className="chat-model-message">{modelsLoading ? 'Buscando modelos…' : providerQueryError ? 'No se pudieron cargar tus proveedores.' : providerTokenAvailable ? 'No hay modelos disponibles para las claves conectadas. Revisá tu Perfil técnico.' : <>Conectá un proveedor desde <a href="/perfil-tecnico">Perfil técnico</a> para generar respuestas.</>}</small>}
    {failedCatalogs.length > 0 && <small className="chat-model-message bloq-error">No se pudieron cargar modelos. {failedCatalogs.join('; ')} Revisá la conexión del proveedor o elegí otro modelo disponible.</small>}
  </div>;
}
