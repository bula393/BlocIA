# BloqIA: chat y clasificador local

Interfaz de chat en español con historial por usuario y la paleta original. Clasifica cada consulta con **E5 multilingüe + regresión logística**. Las consultas generales e informativas reciben una respuesta en Markdown del modelo elegido. Sin claves de proveedor, usa **Qwen3-0.6B local** si está instalado.

## Abrir el sistema

### Linux (sin `sudo`)

Con Python 3.11 o posterior, Node.js 18 o posterior y npm instalados para tu usuario, ejecutá desde la carpeta del proyecto:

```bash
./run.sh
```

En el primer inicio, el script crea `back/.venv-linux`, instala PyTorch para CPU y el resto de las dependencias localmente, instala npm desde el lockfile y descarga los modelos de clasificación y chat. Hace falta conexión a internet y espacio libre para las dependencias y los modelos. Los inicios siguientes reutilizan lo ya instalado.

Abrí <http://127.0.0.1:5173/nuevo-chat>. El script también permite consultar el estado y detener los servicios:

```bash
./run.sh status
./run.sh stop
```

Backend, frontend, base SQLite, clave de cifrado y registros quedan dentro de la carpeta del proyecto. Los servidores sólo escuchan en `127.0.0.1`; no se usa Docker, PostgreSQL ni se requieren privilegios de administrador. Si falta Python, Node.js o npm, instalalos en tu usuario y volvé a correr el script.

### Windows (PowerShell)

Desde esta carpeta:

```powershell
.\Start-BlocIA.ps1
```

Abrir http://127.0.0.1:5173/nuevo-chat y crear una cuenta o iniciar sesión. Para detener los dos procesos: `./Stop-BlocIA.ps1`. Los procesos quedan limitados a la interfaz local del equipo; los registros están en `back/data/run`.

## Configuración y fuentes

- `back/ml/source/`: copias originales de los dos Markdown aportados. No fueron modificadas.
- `back/config/classifier.yaml`: modelo, prefijo `query: `, etiquetas y umbrales tomados del documento.
- `back/config/chat.yaml`: límites de entrada, hilos de CPU y patrones para detectar decisiones sensibles.
- `back/ml/dataset.jsonl`: 370 ejemplos extraídos del Markdown, conservando las etiquetas originales.
- `back/ml/artifacts/classifier.json`: pesos entrenados, sin objetos pickle ejecutables.
- `back/ml/artifacts/training-report.json`: particiones, métricas por clase, matriz de confusión, huella de los datos y revisión del encoder.

Los límites y los umbrales se vuelven a leer cuando cambia el YAML. Después de cambiar el encoder o los pesos, volver a entrenar y reiniciar el backend. Los prompts del usuario no pueden modificar los archivos del servidor.

## Entrenamiento

```powershell
cd back
.\.venv\Scripts\python.exe -m ml.prepare
.\.venv\Scripts\python.exe -m ml.train
```

`prepare` descarga los pesos públicos del encoder E5 y Qwen3-0.6B fijado a una revisión. El encoder se guarda en `back/models/embeddings` y el generador gratuito en `back/models/chat`; el manifiesto del encoder queda en `back/models/manifest.json`. `train` trabaja sin conexión y conserva los grupos de preguntas casi idénticas en una misma partición. Se usaron 259 ejemplos para entrenar, 37 para elegir la regularización y 74 para evaluar; la prueba no se usa para elegir hiperparámetros.

La evaluación inicial obtuvo **macro F1 = 0,9586** y **recall de personal_decision = 1,0000**, con 71/74 predicciones correctas. Los criterios de aceptación adoptados en la configuración son macro F1 ≥ 0,80 y recall de decisiones ≥ 0,85. Si fallan, el entrenamiento no publica pesos nuevos y el servicio no anuncia el clasificador como listo.

Son métricas sobre ejemplos sintéticos aportados por el usuario, con agrupación por semejanza léxica. No garantizan ese resultado sobre consultas reales ni eliminan todo solapamiento semántico.

## Resultado de clasificación

- `no_personal`: consulta general.
- `personal_informativa`: información o análisis personal.
- `personal_decision`: solicitud de una decisión personal.
- Confianza menor a 0,55: revisión manual; entre 0,55 y 0,70: baja confianza.
- Decisiones sensibles de salud, legales o financieras: indicador de revisión humana.

El servicio guarda cada consulta y su clasificación estructurada en el historial para permitir estadísticas posteriores. La clasificación se muestra al pasar el cursor sobre el indicador junto a la respuesta. `no_personal` y `personal_informativa` se responden con el modelo seleccionado; `personal_decision` no se envía al generador. Las claves conectadas habilitan las APIs de OpenAI, Google, Anthropic, Groq y OpenRouter. Si no hay claves, Qwen3 se ejecuta en este equipo y no envía el texto a un proveedor externo.

## Modelos sin costo y claves personales

### Modelo remoto gratuito por defecto

El servidor admite una clave de respaldo de OpenRouter para quienes no conecten una propia. Usa únicamente `openrouter/free`; las rutas pagas se rechazan. Si la clave no está configurada, no se anuncia acceso remoto gratuito. El cupo gratuito se comparte entre quienes usen esta clave.

Después de obtener una clave desde https://openrouter.ai/settings/keys sin comprar créditos, ejecutá desde `back`:

```powershell
.\.venv\Scripts\python.exe -m app.application.chat.remote_defaults
```

La entrada es oculta. El comando valida el catálogo y una inferencia gratuita antes de guardar la clave cifrada en `back/data`, excluido de Git. Conservá juntos `.free-openrouter.token` y `.free-openrouter.key` para respaldarla. También se puede configurar `BLOCIA_FREE_OPENROUTER_KEY` en el entorno del backend. Al abrir un chat nuevo, el selector prioriza el modelo remoto de respaldo frente al local cuando no hay modelos de claves personales; una clave personal de OpenRouter tiene prioridad al enviar. Las consultas que se respondan con ese modelo se envían a OpenRouter y al proveedor remoto elegido por su router. Los límites gratuitos pueden agotarse; no se cambia automáticamente a una ruta paga.

En **Perfil técnico** podés conectar claves API de tus propias cuentas; después elegí el modelo en el chat. Las claves se cifran en la base local y se usan desde el backend. No ingreses contraseñas de Google, ChatGPT ni de otros proveedores.

| Opción | Configuración | Alcance |
| --- | --- | --- |
| Qwen3 local | Ninguna, si descargaste los pesos con `ml.prepare` | Funciona sin cuenta ni peticiones externas. |
| Gemini | [Crear clave en Google AI Studio](https://aistudio.google.com/app/apikey) con una cuenta Google existente y un proyecto Free Tier | [Algunos modelos tienen nivel gratuito](https://ai.google.dev/gemini-api/docs/billing/) con límites por modelo y proyecto. Revisá [precios](https://ai.google.dev/gemini-api/docs/pricing) antes de elegir. |
| Groq | [Crear clave personal](https://console.groq.com/docs/quickstart) en una cuenta Free | Tiene [cupos gratuitos](https://console.groq.com/docs/rate-limits) por modelo. El catálogo de la API no informa el plan actual de la cuenta. |
| OpenRouter | [Crear clave personal](https://openrouter.ai/settings/keys) | BloqIA sólo muestra rutas `:free` con precio de texto cero o `openrouter/free`, y bloquea IDs pagos al enviar. El [plan gratis](https://openrouter.ai/pricing) tiene un cupo diario. |

No hace falta crear otra cuenta Google: podés usar la tuya para AI Studio. Si otro proveedor ofrece acceso con Google, ese inicio de sesión ocurre en su sitio y genera su propia clave API. BloqIA guarda sólo la clave que ingreses, nunca tu contraseña de Google. Los modelos y cuotas pueden cambiar; el catálogo confirma qué modelos devuelve el proveedor, pero no garantiza crédito disponible ni éxito de una inferencia. Una clave de un proyecto con facturación puede generar cargos según el plan de ese proveedor.

### Cuenta ChatGPT Plus o Pro

OpenAI documenta [Sign in with ChatGPT](https://developers.openai.com/siwc/quickstart) para usar el plan personal en peticiones elegibles a la Responses API. Está disponible para aplicaciones de código abierto y clientes privados seleccionados. BlocIA se mantiene privado, por lo que necesita [solicitar acceso para un cliente privado](https://developers.openai.com/siwc/request-client-id) y obtener la habilitación de OpenAI antes de conectar tu plan. Una clave API de OpenAI funciona en BlocIA con la cuenta de plataforma y su facturación propia; no consume el plan Plus o Pro. No reutilices cookies ni credenciales de ChatGPT o Codex como sustituto de ese flujo.

El clasificador no se ajusta con conversaciones de usuarios automáticamente. El historial se guarda localmente y se ocultan correos, teléfonos y algunos nombres/domicilios explícitos antes de persistirlos. Esa detección es heurística; no garantiza eliminar todo dato identificatorio de texto libre. El usuario puede eliminar sus chats.

## Base de datos

La aplicación utiliza **SQLite**, en `back/data/blocia.sqlite3`, con transacciones, claves foráneas, escritura WAL e índices. Al primer acceso importa el JSON anterior sin modificarlo y deja registrada la migración para no repetirla. Los cambios de cuenta y el guardado de mensajes se confirman completos o se revierten.

Las claves de proveedores se cifran con Fernet. La clave de cifrado queda en `back/data/.token-encryption.key`, o se toma de `BLOCIA_ENCRYPTION_KEY`. Para respaldar la instalación hay que conservar tanto la base como esa clave. El almacenamiento viejo no conservaba los secretos: los tokens importados requieren reconexión.

Variables opcionales: `BLOCIA_DATABASE_PATH`, `BLOCIA_DATA_PATH` (JSON anterior), `ACCESS_TOKEN_SECRET`, `BLOCIA_ENCRYPTION_KEY`, `FRONTEND_URL`, `BLOCIA_API_URL` (proxy de desarrollo). No subir `back/data`, claves ni modelos al repositorio.

`GET /health` ejecuta comprobaciones de integridad y relaciones de la base. `GET /chat/status`, autenticado, informa la disponibilidad del clasificador y las métricas de entrenamiento.

Para verificar la base instalada con registros temporales que se revierten al terminar: `python -m ml.verify_database` desde `back`, usando el Python de `.venv`. Para respaldos en caliente, usar la API `sqlite3.Connection.backup`; no copiar solamente el archivo principal mientras hay escrituras activas.

## Verificación

```powershell
cd back
.\.venv\Scripts\python.exe -m pytest -q
cd ../front
npm.cmd test
npm.cmd run build
npm.cmd run test:local
```

La prueba `test:local` requiere el encoder instalado y el clasificador entrenado y Chromium de Playwright (`npx playwright install chromium`). Inicia backend y frontend propios en 8181/4181, usa una base temporal sin datos reales y verifica registro, clasificación local, historial, recarga, revisión humana, vista móvil y borrado.

Las pruebas de base incluyen persistencia al reabrir, credenciales cifradas, rollback ante fallos, concurrencia, restricciones, migración y aislamiento por usuario. Pasar estas comprobaciones no equivale a garantizar ausencia de cualquier fallo posible.

## Instalación desde cero

Python 3.11 o posterior y Node.js instalados:

```powershell
cd back
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install torch --index-url https://download.pytorch.org/whl/cpu
.\.venv\Scripts\python.exe -m pip install -e '.[local,test]'
.\.venv\Scripts\python.exe -m ml.prepare
.\.venv\Scripts\python.exe -m ml.train
cd ../front
npm.cmd ci
```

La ejecución usa CPU por defecto y no descarga modelos al recibir mensajes. La preparación inicial descarga Qwen3-0.6B para habilitar respuestas sin una clave de proveedor.

## Configurar otra computadora después de clonar

```powershell
git clone https://github.com/bula393/BlocIA.git
cd BlocIA

cd back
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install torch --index-url https://download.pytorch.org/whl/cpu
.\.venv\Scripts\python.exe -m pip install -e ".[local,test]"

# Descarga el encoder E5 y Qwen3 local, y entrena el clasificador
.\.venv\Scripts\python.exe -m ml.prepare
.\.venv\Scripts\python.exe -m ml.train

cd ..\front
npm ci
cd ..
```

Los modelos descargados quedan en `back/models` y están excluidos de Git por su tamaño. La base SQLite se crea automáticamente en `back/data`.

Para iniciar el sistema completo:

```powershell
.\Start-BlocIA.ps1
```

Abrí <http://127.0.0.1:5173/nuevo-chat>. Para detenerlo:

```powershell
.\Stop-BlocIA.ps1
```

También se puede iniciar el backend manualmente:

```powershell
cd back
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Usá el inicio completo o el comando manual, pero no ambos al mismo tiempo: los dos usan el puerto 8000. Si PowerShell bloquea la activación o los scripts, se puede habilitar solo para la terminal actual:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
```

Referencias oficiales: [E5 multilingüe](https://huggingface.co/intfloat/multilingual-e5-small), [Sentence Transformers](https://www.sbert.net/docs/package_reference/sentence_transformer/model.html).
