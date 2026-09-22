# BloqIA: chat y clasificador local

Interfaz de chat en español con historial por usuario y la paleta original. Funciona localmente con **E5 multilingüe + regresión logística**. Cada consulta devuelve únicamente categoría, confianza y estado de revisión; no genera respuestas ni usa el historial como entrada del modelo.

## Abrir el sistema

En PowerShell, desde esta carpeta:

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

`prepare` descarga únicamente los pesos públicos del encoder E5 fijados a una revisión y deja su manifiesto en `back/models/manifest.json`. `train` trabaja sin conexión y conserva los grupos de preguntas casi idénticas en una misma partición. Se usaron 259 ejemplos para entrenar, 37 para elegir la regularización y 74 para evaluar; la prueba no se usa para elegir hiperparámetros.

La evaluación inicial obtuvo **macro F1 = 0,9586** y **recall de personal_decision = 1,0000**, con 71/74 predicciones correctas. Los criterios de aceptación adoptados en la configuración son macro F1 ≥ 0,80 y recall de decisiones ≥ 0,85. Si fallan, el entrenamiento no publica pesos nuevos y el servicio no anuncia el clasificador como listo.

Son métricas sobre ejemplos sintéticos aportados por el usuario, con agrupación por semejanza léxica. No garantizan ese resultado sobre consultas reales ni eliminan todo solapamiento semántico.

## Resultado de clasificación

- `no_personal`: consulta general.
- `personal_informativa`: información o análisis personal.
- `personal_decision`: solicitud de una decisión personal.
- Confianza menor a 0,55: revisión manual; entre 0,55 y 0,70: baja confianza.
- Decisiones sensibles de salud, legales o financieras: indicador de revisión humana.

El servicio guarda la consulta y su clasificación estructurada en una misma transacción. La interfaz muestra la clasificación de los chats anteriores, conservando los registros existentes. El generador fue retirado del código y de la configuración; sus pesos descargados anteriormente pueden permanecer en disco, pero no se cargan ni son necesarios.

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

La ejecución usa CPU por defecto y no descarga modelos al recibir mensajes.

Referencias oficiales: [E5 multilingüe](https://huggingface.co/intfloat/multilingual-e5-small), [Sentence Transformers](https://www.sbert.net/docs/package_reference/sentence_transformer/model.html).
