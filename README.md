# BloqIA: chat y clasificador local

Interfaz de chat en español con historial por usuario y la paleta original. Clasifica cada consulta con **E5 multilingüe + regresión logística**. Las consultas generales e informativas reciben una respuesta en Markdown del modelo elegido. Sin claves de proveedor, usa **Qwen3-0.6B local** si está instalado.

## Despliegue por servicios

El proyecto usa tres **Applications** independientes de Dokploy con proveedor Docker: `front`, `back` y `clasificador`. GitHub Actions verifica los cambios, publica sus imágenes en GHCR y, cuando habilitás el despliegue, actualiza y despliega las tres Applications después de que pasen las pruebas.

Seguí la [guía paso a paso de Dokploy](docs/dokploy.md) para configurar las imágenes, el dominio, los volúmenes y las variables manuales. Las configuraciones [Docker Compose separadas](deploy/) permanecen como alternativa. Las automatizaciones están en [CI](.github/workflows/ci.yml) y [despliegue](.github/workflows/deploy.yml). El Compose local está en [compose.yaml](compose.yaml).

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

- `back/ml/source/`: documentos de referencia y ejemplos aportados, con una nota que aclara que la etiqueta depende de la intención, no de la puntuación.
- `back/config/classifier.yaml`: modelo, prefijo `query: `, etiquetas y umbrales tomados del documento.
- `back/config/chat.yaml`: límites de entrada, hilos de CPU y patrones para detectar decisiones sensibles.
- `back/ml/dataset.jsonl`: corpus de entrenamiento materializado por `back/ml/train.py`, con al menos 1.000 ejemplos únicos por etiqueta. Incluye el material de origen, ejemplos personales aportados y ampliaciones reproducibles de `back/ml/expanded_examples.py`.
- `back/ml/artifacts/classifier.json`: pesos entrenados, sin objetos pickle ejecutables.
- `back/ml/artifacts/training-report.json`: particiones, métricas por clase, matriz de confusión, huella de los datos y revisión del encoder.

Los límites y los umbrales se vuelven a leer cuando cambia el YAML. Después de cambiar el encoder o los pesos, volver a entrenar y reiniciar el backend. Los prompts del usuario no pueden modificar los archivos del servidor.

## Entrenamiento

```powershell
cd back
.\.venv\Scripts\python.exe -m ml.prepare
.\.venv\Scripts\python.exe -m ml.train
```

`prepare` descarga los pesos públicos del encoder E5 y Qwen3-0.6B fijado a una revisión. El encoder se guarda en `back/models/embeddings` y el generador gratuito en `back/models/chat`; el manifiesto del encoder queda en `back/models/manifest.json`. `train` trabaja sin conexión, comprueba el mínimo de 1.000 ejemplos únicos por etiqueta y conserva las variantes casi idénticas en una misma partición. La ampliación incluye preguntas, pedidos directos, frases y enunciados; la forma interrogativa por sí sola no determina la etiqueta. El informe registra los tamaños de entrenamiento, validación y prueba.

La evaluación actual obtuvo **macro F1 = 0,9911** y **recall de personal_decision = 0,9843** sobre 782 ejemplos de prueba. Los criterios de aceptación son macro F1 ≥ 0,80 y recall de decisiones ≥ 0,85. Si fallan, el entrenamiento no publica pesos nuevos y el servicio no anuncia el clasificador como listo.

Son métricas sobre un corpus sintético que combina ejemplos que compartiste con variantes generadas, agrupadas por semejanza léxica. No garantizan el mismo resultado sobre consultas reales ni eliminan todo solapamiento semántico.

## Resultado de clasificación

- `no_personal`: consulta general.
- `personal_informativa`: información o análisis personal.
- `personal_decision`: solicitud de una decisión personal.
- Confianza menor a 0,55: revisión manual; entre 0,55 y 0,70: baja confianza.
- Decisiones sensibles de salud, legales o financieras: indicador de revisión humana.

El servicio guarda cada consulta completada y su clasificación estructurada en el historial para permitir estadísticas posteriores. `no_personal` se responde con el modelo seleccionado. Al terminar la clasificación de una consulta `personal_informativa`, el chat pregunta si querés usar una de tus 3 respuestas personales diarias; recién después de aceptar se prepara la respuesta y se envía al modelo cuando corresponde. Cancelar no consume cupo ni guarda mensajes. `personal_decision` no se envía al generador. La confirmación aparece dentro del recuadro de envío. La barra al pie de ese mismo recuadro se llena con las consultas personales usadas y muestra cuántas quedan antes del bloqueo. Las claves conectadas habilitan las APIs de OpenAI, Google, Anthropic, Groq y OpenRouter. Si no hay claves, Qwen3 se ejecuta en este equipo y no envía el texto a un proveedor externo.

Las consultas parecidas a los grupos del material aportado —sentimentales, de salud, cotidianas y de planes— reciben una respuesta predefinida en español. Estas respuestas quedan en el historial y no se envían al modelo ni a un proveedor externo.

## Rendimiento del chat

El encoder se carga y ejecuta una consulta de preparación al iniciar el backend, antes de aceptar mensajes. Esto traslada la espera inicial al arranque. `BLOCIA_PRELOAD_CLASSIFIER=0` permite desactivar esa preparación. Con `BLOCIA_PRELOAD_LOCAL_CHAT=1` también se carga Qwen al arrancar; de forma predeterminada se carga al primer uso para ahorrar memoria cuando se elige la nube.

Las matrices y los patrones del clasificador se preparan una vez. Una caché de 128 resultados evita repetir la inferencia para preguntas idénticas; guarda huellas SHA-256 y clasificaciones, sin conservar los textos. Se invalida cuando cambian los pesos, archivos del encoder, manifiesto, evaluación o configuración. Los fragmentos de consultas largas conservan el solapamiento y la detección de decisiones sensibles al final del texto.

Qwen usa `local_model_dtype: float32` en `back/config/chat.yaml`: mejoró la velocidad en la CPU de esta instalación frente al bfloat16 del modelo. Sus pesos ocupan aproximadamente el doble de memoria; se puede elegir `auto` y reiniciar el backend para volver a la precisión del archivo original. La generación conserva el límite de 1024 tokens y usa la caché de atención.

Las peticiones a la nube comparten un [cliente HTTP con conexiones persistentes](https://www.python-httpx.org/advanced/clients/), con credenciales individuales por petición. El contexto recupera solo los cuatro últimos intercambios respondidos. La interfaz deja de consultar el progreso al comenzar la generación y muestra la respuesta sin esperar al siguiente intervalo de 300 ms.

Mediciones locales del 4/10/2026: en los 74 ejemplos de evaluación, el tiempo mediano de clasificación sin caché pasó de 14,19 a 12,18 ms y los resultados completos fueron idénticos. Para cuatro consultas repetidas, el promedio pasó de 72,24 a 0,44 ms usando la caché. En una generación fija de 32 tokens, Qwen pasó de 3,45 a 4,52 tokens/s al usar float32. Estas cifras dependen del equipo y la longitud de entrada; no se midió la latencia real de los proveedores externos.

## Modelos predeterminados y claves personales

### Gemini predeterminado

El servidor puede ofrecer `gemini-3.8-flash` como modelo de respaldo para quienes no conecten una clave propia. Desde `back`, ejecutá `python -m app.application.chat.google_defaults`; la clave se solicita sin mostrarla, se valida contra el catálogo de Google y se cifra en `back/data`, excluido de Git. También se puede configurar `BLOCIA_FREE_GOOGLE_KEY` en el entorno del backend. Conservá juntos `.free-google.token` y `.free-google.key` para respaldar la instalación.

Las claves personales siguen teniendo prioridad. Si no hay ninguna, los mensajes se envían a Google con esta clave compartida y usan la cuota o facturación del proyecto asociado. Gemini 3.8 Flash puede generar cargos según el plan del proyecto; revisá sus límites y precios antes de habilitarla para otras personas.

Si Google devuelve `ACCOUNT_STATE_INVALID`, indica que la cuenta de servicio vinculada a la clave está deshabilitada o eliminada. Para conservar la misma clave, [habilitá esa cuenta](https://docs.cloud.google.com/iam/docs/service-accounts-disable-enable) en el proyecto de Google Cloud. Si fue eliminada, Google permite [restaurarla dentro de los 30 días posteriores](https://docs.cloud.google.com/iam/docs/service-accounts-delete-undelete). El backend conserva la clave cifrada y muestra esta causa específica; el estado de la cuenta se corrige en Google Cloud.

### Modelo remoto gratuito por defecto

El servidor admite una clave de respaldo de OpenRouter para quienes no conecten una propia. Usa únicamente `openrouter/free`; las rutas pagas se rechazan. Si la clave no está configurada, no se anuncia acceso remoto gratuito. El cupo gratuito se comparte entre quienes usen esta clave.

Después de obtener una clave desde https://openrouter.ai/settings/keys sin comprar créditos, ejecutá desde `back`:

```powershell
.\.venv\Scripts\python.exe -m app.application.chat.remote_defaults
```

La entrada es oculta. El comando valida el catálogo y una inferencia gratuita antes de guardar la clave cifrada en `back/data`, excluido de Git. Conservá juntos `.free-openrouter.token` y `.free-openrouter.key` para respaldarla. También se puede configurar `BLOCIA_FREE_OPENROUTER_KEY` en el entorno del backend. Al abrir un chat nuevo, el selector prioriza los modelos de claves personales; sin ellos ofrece Gemini, OpenRouter gratuito y Qwen local, en ese orden. Una clave personal de OpenRouter tiene prioridad al enviar. Las consultas que se respondan con ese modelo se envían a OpenRouter y al proveedor remoto elegido por su router. Los límites gratuitos pueden agotarse; no se cambia automáticamente a una ruta paga.

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

En desarrollo, completá los tokens predeterminados de `back/.env.dev`; en una instalación nueva, copialo desde `back/.env.dev.example`. Reiniciá el backend para aplicar los cambios. Las claves personales de cada usuario tienen prioridad; los valores globales nunca se devuelven al navegador. El catálogo de OpenRouter sigue limitado a modelos gratuitos.

`BLOCIA_LOCK_MINUTES` configura la duración del bloqueo en minutos enteros positivos; el valor predeterminado es `1440` (24 horas). Los límites siguen siendo 3 consultas personales y 3 horas de uso de IA en una ventana móvil de 24 horas. Cuando vence un bloqueo, comienza un nuevo cupo sin borrar los chats ni las métricas históricas. Un valor vacío, inválido o no positivo conserva la duración predeterminada.

`GET /health` ejecuta comprobaciones de integridad y relaciones de la base. `GET /chat/status`, autenticado, informa la disponibilidad del clasificador y las métricas de entrenamiento.

Para reiniciar el contador móvil de 24 horas y desbloquear una cuenta de forma administrativa, ejecutá `python scripts/reset_user_daily_limit.py` desde `back` con el mismo `BLOCIA_DATABASE_PATH` que usa el backend. El comando solicita el correo, un motivo y una confirmación escrita con el correo. Guarda la fecha y el motivo del reinicio, quita el bloqueo actual y conserva los chats y métricas históricas.

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

### Modelos Google y cuota del proyecto

`models.list` devuelve el catálogo, pero no confirma que un proyecto pueda generar respuestas con cada modelo. BloqIA cruza ese catálogo con `back/data/google-model-access.json`, un registro local ignorado por Git de los cupos revisados en AI Studio. El selector ofrece solamente los modelos de chat con RPM, TPM y RPD positivos. El servidor también rechaza selecciones antiguas fuera de ese registro.

El registro contiene `credentialSha256` (SHA-256 de la clave efectiva, sin guardarla), `projectId`, `checkedAt`, `source` y `models`: una lista de objetos con `modelId`, `chat`, `rpm`, `tpm` y `rpd`. Puede cambiarse su ruta con `BLOCIA_GOOGLE_MODEL_ACCESS_PATH`. Al cambiar de clave o de proyecto, hay que verificar sus límites en https://aistudio.google.com/rate-limit y actualizar el registro; las cuotas de la clave anterior no se heredan. La lista se consulta de nuevo en cada petición. Al cambiar el plan o los límites también debe actualizarse: este registro es una verificación manual fechada, no una consulta de cuota en tiempo real. Cuota positiva no garantiza capacidad ni saldo disponible en el momento del envío.
