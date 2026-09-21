# Configuración de acceso con Google

Creá un cliente OAuth 2.0 de tipo **Aplicación web** en Google Cloud y registrá
la URL de redirección del backend. Para desarrollo local:

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

En producción, `GOOGLE_REDIRECT_URI` debe ser la URL pública HTTPS del backend
terminada en `/auth/google/callback`, y `FRONTEND_URL` la URL pública del front.
No expongas ningún secreto en Vite ni lo incluyas en el repositorio. En
producción son obligatorios `ACCESS_TOKEN_SECRET` y `GOOGLE_SESSION_SECRET`;
usá valores distintos, largos y aleatorios.

El callback valida el estado guardado en una cookie HTTP-only, canjea el código
en el servidor y valida la identidad contra Google. Luego entrega al front un
resultado de un solo uso mediante otra cookie HTTP-only; si faltan edad o
profesión, el front muestra únicamente esos campos.
