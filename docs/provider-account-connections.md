# Cuentas personales de proveedores

Los cambios de esta integración son locales. No se subieron al repositorio ni se desplegaron en Dokploy. El clasificador no se modifica.

## Google / Gemini

La conexión está implementada con OAuth: verificar el correo de BloqIA, autorizar la cuenta Google, elegir un proyecto y pulsar **Comprobar y usar Gemini**. Si sólo existe un proyecto, se selecciona automáticamente; la prueba no se envía hasta pulsar el botón. Puede consumir cupo o generar un cargo según el proyecto de Google.

La autorización permite usar la API de Gemini con el proyecto del usuario. No convierte una suscripción Google AI Pro o Ultra en crédito de API. Google administra esos beneficios por separado. [Documentación de planes](https://ai.google.dev/gemini-api/docs/google-ai-plans).

### Configuración pendiente para una prueba real

Avance del 11 de octubre de 2026: en el proyecto **BloqIA** (`ardent-depth-511122-g5`), cuenta `bloqia.app@gmail.com`, se creó el cliente web **BloqIA Gemini**, separado del login. Se registraron los dos retornos indicados abajo, se guardó `cloud-platform` junto con los permisos de identidad existentes y se agregó esa cuenta como usuario de prueba. Las credenciales se guardaron únicamente en `back/.env.dev`, ignorado por Git, con OAuth activado para desarrollo y el retorno local. Se comprobó que el backend carga los cuatro valores correctamente; todavía falta completar una autorización real de usuario. Dokploy y el código publicado no se modificaron.

Gemini API y Cloud Resource Manager API se habilitaron con autorización del titular. Service Usage API ya estaba habilitada y se comprobó su estado. AI Studio muestra el proyecto en nivel gratuito; no se activó facturación ni se contrató un plan.

Para probar, reiniciar el backend local y abrir el frontend en `http://localhost:5173`. Ingresar a BloqIA con una cuenta de prueba de Google y verificar su correo; en el perfil, conectar Google, elegir el proyecto y pulsar **Comprobar y usar Gemini**. Ese último paso envía una petición real y puede consumir cupo. Para otra cuenta, agregarla primero como usuario de prueba en Google Cloud. Antes de publicar, completar la información de marca y los requisitos de verificación de Google; no publicar la pantalla de consentimiento sólo para resolver una prueba.

1. En el proyecto Google Cloud de BloqIA, crear **otro cliente OAuth de aplicación web**, separado del usado para iniciar sesión en BloqIA. Así, desconectar Gemini no retira el acceso del cliente de login.
2. Registrar el retorno local `http://localhost:5173/api/technical-profile/google/callback`. Para una publicación futura registrar `https://bloqia.policloudservices.ipm.edu.ar/api/technical-profile/google/callback`. Si Vite se ejecuta en otro puerto, usar ese mismo puerto tanto en Google como en la variable de retorno.
3. Configurar la pantalla de consentimiento para `openid`, `email` y `https://www.googleapis.com/auth/cloud-platform`. Google describe este último como acceso amplio a Cloud; la aplicación lo usa sólo con los endpoints fijos de proyectos, permisos, servicios y Gemini. No habilita servicios ni facturación automáticamente. Revisar los requisitos de verificación de Google antes de ofrecerlo a todos los usuarios. En modo prueba, agregar las cuentas de prueba; las autorizaciones pueden vencer antes de su publicación.
4. Habilitar las APIs que necesite el cliente/proyecto: Cloud Resource Manager y Service Usage para descubrir y comprobar proyectos; Generative Language API para usar Gemini. Cada usuario debe tener acceso al proyecto seleccionado y permiso `serviceusage.services.use`.
5. Cargar en el **backend** las variables de abajo. No poner secretos en el frontend, en Git ni en archivos públicos. Usar `BLOCIA_ENCRYPTION_KEY` estable y conservarla para descifrar las conexiones guardadas.
6. Probar con una cuenta real: autorizar, elegir proyecto, comprobar, elegir explícitamente Gemini en el chat y enviar una consulta general. Luego desconectar y comprobar que la autorización ya no se usa. El modelo predeterminado sigue siendo Groq `openai/gpt-oss-20b`.

```dotenv
BLOCIA_GOOGLE_OAUTH_ENABLED=1
GOOGLE_AI_CLIENT_ID=<ID del cliente OAuth exclusivo para Gemini>
GOOGLE_AI_CLIENT_SECRET=<secreto del mismo cliente>
GOOGLE_AI_REDIRECT_URI=http://localhost:5173/api/technical-profile/google/callback
```

La conexión permanece deshabilitada por defecto en las plantillas y en producción; se activó sólo en el entorno local indicado arriba. `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` y `GOOGLE_REDIRECT_URI` siguen siendo los del login existente; no reemplazarlos por los de Gemini.

### Comportamiento y seguridad

- Código de autorización con PKCE, nonce y estado de un solo uso, ligado al usuario y a una cookie HttpOnly del navegador. Expira a los diez minutos.
- Tokens cifrados en SQLite/PostgreSQL, nunca devueltos al navegador. Renovación serializada para evitar carreras entre procesos.
- La elección del proyecto comprueba que está en la cuenta, su permiso de uso, que Gemini está habilitado y una petición breve real. La prueba no garantiza cupo futuro.
- Las peticiones usan el token de esa cuenta y `x-goog-user-project`. Una autorización vencida, incompleta o retirada exige reconectar; no pasa a usar la clave del servidor.
- Al desconectar se eliminan las credenciales locales y se solicita revocación a Google. Si falla la revocación remota, la pantalla ofrece el enlace para retirarla manualmente.
- Las claves API siguen disponibles en opciones avanzadas. Si hay una cuenta conectada, se pide desconectarla antes de cambiar a una clave.
- La confirmación de consultas personales y el límite diario continúan aplicándose antes de generar la respuesta.

Referencias: [OAuth Gemini](https://ai.google.dev/gemini-api/docs/oauth), [OAuth para servidores web](https://developers.google.com/identity/protocols/oauth2/web-server), [lista de proyectos](https://docs.cloud.google.com/resource-manager/reference/rest/v1/projects/list).

## ChatGPT

OpenAI ofrece **Sign in with ChatGPT** con identidad y uso de planes elegibles. Una aplicación alojada para varios usuarios, como BloqIA, requiere solicitar acceso al programa; el registro dinámico para herramientas locales de código abierto no habilita por sí solo una web pública.

El 11 de octubre de 2026 se comprobó en el [formulario](https://openai.com/form/sign-in-with-chatgpt-interest/) la confirmación **«Hemos recibido tu formulario»**, después de que el usuario completara sus datos. La solicitud de BloqIA está recibida; esto no equivale a aprobación ni a credenciales para integrar el servicio. OpenAI indica que se pondrá en contacto si el producto encaja. Durante el intento inicial se observó un error de Cloudflare Turnstile `300030`, compatible con el bloqueo temporal del envío; la confirmación posterior resuelve el estado de la solicitud.

No se muestra un botón de autorización que aparente funcionar antes de tener el acceso y registro correspondientes. Tras la aprobación, implementar el flujo alojado que indique OpenAI y el adaptador Responses API para uso de planes; el adaptador actual de claves API utiliza Chat Completions y no equivale a esa autorización.

Referencias: [inicio rápido](https://developers.openai.com/siwc/quickstart), [limitaciones](https://developers.openai.com/siwc/token-sharing-open-source/preview-limitations), [inferencia](https://developers.openai.com/siwc/token-sharing-open-source/models-and-inference).

## Claude

Para esta aplicación alojada se conserva la conexión con clave de API de Anthropic. No se ofrece importar cookies o credenciales de una suscripción personal. [Autenticación de Anthropic](https://platform.claude.com/docs/en/manage-claude/authentication).

## Alcance de la verificación local

Las pruebas automáticas simulan Google y usan almacenamiento cifrado real: permisos, nonce, PKCE, repetición/expiración, elección de proyecto, renovación, revocación, privacidad de errores y envío con la cuenta correcta. El recorrido visual se comprueba en escritorio y celular. Esto no reemplaza la autorización real de Google ni la aprobación de OpenAI; ambas siguen pendientes antes de publicar la función.
