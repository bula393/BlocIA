# Configuración de acceso con Google

El acceso con Google usa un cliente OAuth 2.0 de tipo **Aplicación web** de
Google Cloud. `GOOGLE_CLIENT_ID` y `GOOGLE_CLIENT_SECRET` son credenciales de ese
cliente; la clave de Gemini (`BLOCIA_DEFAULT_GOOGLE_TOKEN`) no sirve para iniciar
sesión y no debe copiarse en estas variables.

## Producción en Dokploy

1. Abrí [Google Auth Platform](https://console.cloud.google.com/auth/overview)
   en el proyecto de Google Cloud que quieras usar. Configurá el nombre de la
   aplicación, correo de soporte y contacto en **Branding**, y elegí la audiencia
   permitida en **Audience**. Si el cliente está en modo de prueba, agregá como
   usuarios de prueba las cuentas que van a iniciar sesión.
2. En **Clients**, creá un cliente de tipo **Web application**. Configurá como
   **Authorized JavaScript origin** `https://bloqia.policloudservices.ipm.edu.ar`
   y como **Authorized redirect URI**, exactamente:

   ```text
   https://bloqia.policloudservices.ipm.edu.ar/api/auth/google/callback
   ```

3. Guardá en **Environment** de `back` los siguientes valores. Obtené el ID y
   secreto del cliente recién creado; generá los secretos de firma una vez y
   conservalos entre despliegues. No incluyas estos secretos en `front` ni Vite.

   ```text
   GOOGLE_CLIENT_ID=<client-id-de-google>
   GOOGLE_CLIENT_SECRET=<client-secret-de-google>
   GOOGLE_REDIRECT_URI=https://bloqia.policloudservices.ipm.edu.ar/api/auth/google/callback
   FRONTEND_URL=https://bloqia.policloudservices.ipm.edu.ar
   GOOGLE_SESSION_SECRET=<secreto-largo-aleatorio-para-el-callback>
   GOOGLE_REGISTRATION_SECRET=<otro-secreto-largo-aleatorio-para-el-alta-pendiente>
   ```

   `ACCESS_TOKEN_SECRET` también debe estar configurado en `back`. Si
   `GOOGLE_SESSION_SECRET` queda vacío, el callback usa `ACCESS_TOKEN_SECRET`
   como firma; se recomienda configurar secretos separados. Para el alta
   pendiente, `GOOGLE_REGISTRATION_SECRET` usa el secreto del cliente OAuth
   como alternativa. Las credenciales reales de Google Cloud no se generan
   automáticamente al desplegar BlocIA.
4. Conservá la ruta pública del servicio `back` como `/api`, **Internal Path**
   `/` y **Strip Path** activado. El prefijo `/api` pertenece al enrutador de
   Dokploy; el endpoint del contenedor es `/auth/google/callback`. HTTPS
   permanece activado en front y back con el mismo host. Los puertos internos
   `60001` y `60002` no se agregan a la URI registrada en Google.
5. Desplegá `back`, abrí la app e iniciá **Continuar con Google**. El navegador
   debe ir a Google desde `/api/auth/google/start`, volver por el callback
   anterior y terminar en `/auth/google/callback` del frontend. Si falta edad
   o profesión, completá esos campos para crear la cuenta. Repetí el acceso
   para comprobar la cuenta existente y verificá también una cancelación.

Google exige que `redirect_uri` coincida exactamente con la URI autorizada.
`redirect_uri_mismatch` indica que tenés que revisar host, HTTPS, ruta y barra
final. Si faltan `GOOGLE_CLIENT_ID` o `GOOGLE_CLIENT_SECRET`, BlocIA vuelve al
frontend con `error=configuration`, sin enviar credenciales incompletas a Google.

## Desarrollo local

Podés agregar un cliente local separado o autorizar el callback local en el mismo
cliente. Estas variables van en `back/.env.dev`:

```text
GOOGLE_CLIENT_ID=<client-id-de-google>
GOOGLE_CLIENT_SECRET=<client-secret-de-google>
GOOGLE_REGISTRATION_SECRET=<secreto-largo-distinto-para-firmar-el-alta-pendiente>
ACCESS_TOKEN_SECRET=<secreto-largo-para-firmar-las-sesiones>
GOOGLE_SESSION_SECRET=<secreto-largo-para-firmar-el-resultado-del-callback>
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
FRONTEND_URL=http://localhost:5173
```

Usá el mismo hostname en ambas URLs durante desarrollo: no mezcles
`localhost` con `127.0.0.1`, porque la cookie que valida `state` es deliberadamente
host-only.

Cuando `GOOGLE_REDIRECT_URI` no está definido o está vacío, en desarrollo se usa
`http://localhost:8000/auth/google/callback`. En producción se deriva de
`FRONTEND_URL` agregando `/api/auth/google/callback`. En Dokploy conviene guardar
el valor explícito de producción indicado arriba.

## Validaciones del flujo

El inicio crea un `state` y un `nonce` distintos. Se guardan juntos en una cookie
HTTP-only firmada que vence a los diez minutos; el callback valida su firma,
expiración y coincidencia del `state` antes de canjear el código en el servidor.
La biblioteca oficial `google-auth` valida la firma del ID token con las claves
públicas de Google, emisor, audiencia y fechas. BlocIA comprueba además el
`nonce` y que Google haya verificado el correo.

El resultado del callback usa otra cookie HTTP-only firmada, con un propósito
distinto y una expiración comprobada en el servidor de dos minutos. Se elimina
al recuperarlo desde el frontend; ninguna credencial se coloca en la URL. Si
faltan edad o profesión, el front muestra únicamente esos campos. Las cookies
de producción usan HTTPS y `SameSite=Lax`.

Referencias: [flujo OpenID Connect de Google](https://developers.google.com/identity/openid-connect/openid-connect)
y [validación de ID tokens con Python](https://developers.google.com/identity/sign-in/web/backend-auth).
