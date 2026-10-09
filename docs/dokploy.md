# Subir BlocIA a Dokploy

En el proyecto `BloqIa` se usan tres servicios **Application** independientes con proveedor **Docker** (`back`, `front` y `clasificador`) y una base **PostgreSQL** administrada como recurso Database separado. GitHub Actions publica las imágenes y, cuando se habilita `DEPLOY_ENABLED`, actualiza el tag y solicita el despliegue de las tres Applications mediante la API de Dokploy. PostgreSQL se conserva entre versiones y no se recrea en cada push.

| Servicio | Función | Puerto del contenedor | Datos persistentes |
| --- | --- | --- | --- |
| `database` | PostgreSQL para cuentas, chats, límites y credenciales cifradas | 5432, solo red privada | Volumen administrado por Dokploy |
| `back` | `ghcr.io/bula393/blocia-api:<SHA>` | 60002, público vía HTTPS en `/api` | Usa `database`; conserva la clave Fernet en Environment |
| `front` | `ghcr.io/bula393/blocia-frontend:<SHA>` | 60001, público vía HTTPS en `/` | Ninguno |
| `clasificador` | `ghcr.io/bula393/blocia-inference:<SHA>` | 8001, privado | Volumen en `/app/models` |

`front` y `back` comparten el host público existente `BloqIA.policloudservices.ipm.edu.ar`: la interfaz se sirve en `/` y la API en `/api`. La URL normalizada es `https://bloqia.policloudservices.ipm.edu.ar`. PostgreSQL y el clasificador permanecen en la red privada. Dokploy administra la persistencia de PostgreSQL; el clasificador necesita un volumen persistente para sus modelos. Los tags de imagen son inmutables y cambian en cada push aprobado.

El código está organizado en `front/src/features/chat/` para el chat y sus componentes; `back/app/bootstrap.py` para montar la API; `back/app/application/` para casos de uso; `back/app/presentation/` para contratos HTTP; `back/app/infrastructure/` para persistencia y transportes; y `back/app/inference_main.py` para la IA independiente.

## 1. Preparar dominio y servidor

Usá el host `BloqIA.policloudservices.ipm.edu.ar` ya configurado en `back` y comprobá que su DNS resuelva hacia el servidor de Dokploy. El servidor debe permitir que Dokploy atienda HTTP/HTTPS y pueda descargar imágenes desde GHCR y modelos desde Hugging Face. Usá Linux con Docker; la construcción predeterminada es para `linux/amd64`.

Los límites iniciales son 6 GB para inferencia, 512 MB para la API y 128 MB para la interfaz. Reservá memoria adicional para Dokploy y el sistema. Son valores iniciales ajustables en el `.env.example` de cada servicio; el consumo real depende de los modelos y las consultas. No se comprobó el rendimiento en tu servidor.

Por defecto, `BLOCIA_ENABLE_LOCAL_CHAT=0` instala solamente el clasificador. Para generar respuestas, conectá un proveedor desde Perfil técnico, configurá una credencial del servidor, o cambiá esa variable a `1` para instalar Qwen3-0.6B. La primera instalación descarga pesos en el volumen; puede tardar varios minutos. Los despliegues siguientes reutilizan esos archivos.

## 2. Crear PostgreSQL y las tres Applications en Dokploy

En el proyecto y entorno `production` que ya abriste, creá primero un recurso **Database → PostgreSQL** llamado `blocia-db`. Usá la misma instancia/servidor y entorno que las Applications. Elegí un nombre de base y de usuario dedicados (`blocia` y `blocia_app`) y generá una contraseña URL-safe en tu equipo con `python -c "import secrets; print(secrets.token_urlsafe(48))"`; pegala directamente en Dokploy, no en el chat. Dejá desactivado **External Port/External Credentials**: la API se conectará por la conexión interna de Dokploy y PostgreSQL no quedará expuesto a Internet. Guardá el recurso y comprobá que esté listo. Dokploy muestra el host, puerto, credenciales internas y la **Internal Connection URL** en la pestaña de conexión ([guía oficial](https://docs.dokploy.com/docs/core/databases/connection)).

Después, creá tres recursos de tipo **Application**: `back`, `front` y `clasificador`. Usá el mismo proyecto, entorno y servidor; elegí el proveedor **Docker** para cada uno. No elijas Docker Compose para este flujo.

En cada servicio, completá el proveedor Docker de esta manera:

| Application | Docker Image inicial | Registry URL |
| --- | --- | --- |
| `back` | `ghcr.io/bula393/blocia-api:SHA_COMPLETO` | `ghcr.io` |
| `front` | `ghcr.io/bula393/blocia-frontend:SHA_COMPLETO` | `ghcr.io` |
| `clasificador` | `ghcr.io/bula393/blocia-inference:SHA_COMPLETO` | `ghcr.io` |

Reemplazá `SHA_COMPLETO` por los 40 caracteres del commit que Actions publicó más recientemente; el resumen de la ejecución y la pestaña **Packages** muestran el tag exacto. Las imágenes son públicas, así que podés dejar vacíos usuario y contraseña del registro. No uses `latest`: cada versión queda identificada y se puede revertir. El workflow actualiza estas imágenes al SHA del push que haya pasado las pruebas. En estas Applications, configurá `PORT=60001` para `front` y `PORT=60002` para `back`; `clasificador` conserva `8001`. Las imágenes admiten estos puertos por Environment y mantienen `8080`/`8000` como valores predeterminados para la alternativa Compose.

En `clasificador`, agregá un volumen persistente montado en `/app/models`; la descarga inicial del modelo puede demorar. `front` y `back` se publican mediante el enrutador HTTPS de Dokploy, sin agregar puertos de host. PostgreSQL (`5432`) y el clasificador (`8001`) quedan privados.

Las imágenes de GitHub se consultan desde [GHCR](https://github.com/bula393?tab=packages). Para las imágenes públicas no hace falta crear credenciales del registro en Dokploy. Si después hacés privados los paquetes, creá un token de GitHub con `read:packages` y configurá un Registry GHCR con ese usuario y token. Actions publica con su `GITHUB_TOKEN` automático. Referencias: [GHCR en Dokploy](https://docs.dokploy.com/docs/core/registry/ghcr) y [permisos del Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry).

## 3. Variables de cada Application

En la pestaña **Environment** de cada Application, agregá las variables de runtime de esta tabla. Los archivos `.env.example` de `deploy/` son para la alternativa Compose; no copies sus variables de red, volúmenes, `GHCR_IMAGE_PREFIX` o `RELEASE_TAG` a estas Applications.

| Application | Variable | Valor |
| --- | --- | --- |
| `back` | `PORT` | `60002` |
| `back` | `FRONTEND_URL` | `https://bloqia.policloudservices.ipm.edu.ar`, sin barra final |
| `back` | `ACCESS_TOKEN_SECRET` | Secreto aleatorio de al menos 32 caracteres |
| `back` | `DATABASE_URL` | **Internal Connection URL** que muestra el recurso PostgreSQL de Dokploy |
| `back` | `BLOCIA_ENCRYPTION_KEY` | Clave Fernet aleatoria; necesaria para cifrar los tokens de proveedores guardados por la app |
| `back` | `BLOCIA_LOCK_MINUTES` | Minutos de bloqueo deseados; `1440` equivale a un día |
| `back` | `BLOCIA_INFERENCE_URL` | `http://blocia-clasificador-nrn9qa:8001` |
| `back` | `BLOCIA_INFERENCE_TOKEN` | Secreto aleatorio compartido con `clasificador` |
| `front` | `PORT` | `60001` |
| `front` | `BLOCIA_API_UPSTREAM` | `bloqia-back-b1bgga:60002` |
| `clasificador` | `BLOCIA_INFERENCE_TOKEN` | El mismo valor configurado en `back` |
| `clasificador` | `BLOCIA_ENABLE_LOCAL_CHAT` | `0` para solo clasificar; `1` habilita Qwen local y requiere más memoria |

Los nombres internos `blocia-clasificador-nrn9qa` y `bloqia-back-b1bgga` aparecen debajo del título de cada Application en Dokploy. Las Applications y el recurso PostgreSQL deben compartir la red privada del entorno para que se resuelvan entre sí. Usá la **Internal Connection URL** que Dokploy muestra para PostgreSQL; no armes una URL con el host externo. Conservá `BLOCIA_API_UPSTREAM` con el nombre interno del back para el proxy de la interfaz. No agregues puertos de host: el enrutador de Dokploy publica front y back por HTTPS, mientras los puertos `5432` y `8001` permanecen privados.

Generá los secretos en tu equipo, sin pegarlos en el chat. `ACCESS_TOKEN_SECRET` y `BLOCIA_INFERENCE_TOKEN` deben ser valores distintos; el token de inferencia sí se comparte entre `back` y `clasificador`. Para `BLOCIA_ENCRYPTION_KEY`, ejecutá `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` y guardá una copia segura: si se pierde o cambia, la app no podrá descifrar los tokens de proveedores ya almacenados. Las credenciales `BLOCIA_DEFAULT_*_TOKEN` son opcionales. Google Login también es opcional y requiere `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` y registrar `https://bloqia.policloudservices.ipm.edu.ar/api/auth/google/callback` como URL de retorno.

### Google Login y verificación de correo para claves propias

Seguí [la guía de Google OAuth](../back/GOOGLE_OAUTH_SETUP.md) para crear un cliente de tipo **Aplicación web**. En **Google Auth Platform**, completá Branding/Audience y agregá las cuentas de prueba mientras el proyecto esté en Testing. Usá como origen `https://bloqia.policloudservices.ipm.edu.ar` y como redirect autorizado `https://bloqia.policloudservices.ipm.edu.ar/api/auth/google/callback`. Guardá `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` y esa misma `GOOGLE_REDIRECT_URI` solo en **back → Environment**; después desplegá back. El secreto OAuth es distinto de una clave Gemini y nunca se incluye en el frontend.

Para conectar claves propias de proveedores, cada cuenta debe recibir y confirmar un código en su correo. Configurá estas variables únicamente en **back → Environment**:

| Variable | Ejemplo Gmail | Función |
| --- | --- | --- |
| `SMTP_HOST` | `smtp.gmail.com` | Servidor de envío |
| `SMTP_PORT` | `587` | Puerto SMTP saliente; independiente de los puertos públicos de la app |
| `SMTP_SECURITY` | `starttls` | TLS obligatorio; también admite `ssl` con puerto `465` |
| `SMTP_USERNAME` | `tu-cuenta@gmail.com` | Cuenta remitente |
| `SMTP_PASSWORD` | Contraseña de aplicación | Credencial SMTP, nunca la contraseña habitual |
| `SMTP_FROM` | `tu-cuenta@gmail.com` | Dirección remitente autorizada por el servidor SMTP |

Para Gmail, activá la verificación en dos pasos y generá una contraseña para BloqIA en [Contraseñas de aplicación](https://myaccount.google.com/apppasswords). Algunas cuentas institucionales no permiten esta opción; en ese caso usá el SMTP que habilite el administrador o un proveedor de correo transaccional. [Ayuda de Google](https://support.google.com/accounts/answer/185833?hl=es).

El código tiene seis dígitos, vence en diez minutos y admite cinco intentos. Se puede reenviar después de un minuto, con un máximo de diez envíos por cuenta cada 24 horas. PostgreSQL conserva los intentos y la verificación entre despliegues; el código se guarda como HMAC y se elimina al confirmar. Si falta SMTP o falla la entrega, la API rechaza guardar claves propias. Las credenciales del servidor y la eliminación de claves existentes siguen disponibles. Incluso las cuentas que entran con Google deben completar este código para conectar una clave propia.

Validación real: abrí la app en un navegador habitual, entrá con Google y verificá que vuelva al chat (o a completar el registro si es una cuenta nueva). En Perfil técnico, pedí un código, comprobá la recepción, ingresalo y conectá una clave. Comprobá también que una cuenta sin verificar recibe `403` al guardar una clave por API. Las pruebas automatizadas simulan Google y SMTP; no reemplazan esta validación con credenciales y entrega reales.

## 4. Configurar las rutas públicas de front y back

En **Domains** de cada Application, usá el mismo host existente en `back`: `BloqIA.policloudservices.ipm.edu.ar`. Configurá estas dos rutas:

| Application | Host | Path | Internal Path | Strip Path | Container Port | HTTPS |
| --- | --- | --- | --- | --- | --- | --- |
| `front` | `BloqIA.policloudservices.ipm.edu.ar` | `/` | `/` | Desactivado | `60001` | Activado, Let's Encrypt |
| `back` | `BloqIA.policloudservices.ipm.edu.ar` | `/api` | `/` | Activado | `60002` | Activado, Let's Encrypt |

La ruta `/api` del back tiene prioridad sobre la ruta `/` del front. `Strip Path` elimina el prefijo `/api` antes de enviar la solicitud a la API: `/api/health` llega como `/health` al contenedor. Los puertos de contenedor `60001` y `60002` cumplen el requisito de usar puertos superiores a `60000`; el acceso público sigue siendo HTTPS sin indicar puerto en la URL. No agregues dominios ni puertos externos a PostgreSQL o `clasificador`, ni puertos de host adicionales a front o back. Revisá y guardá las rutas en Dokploy según su [documentación oficial de Applications](https://docs.dokploy.com/docs/core/applications).

## 5. Configurar GitHub Actions para desplegar las Applications

En GitHub abrí **Settings → Secrets and variables → Actions → Variables** y creá estas Repository variables:

| Variable | Valor |
| --- | --- |
| `DEPLOY_ENABLED` | `false` durante la configuración; cambialo a `true` cuando los tres servicios estén listos. |
| `DEPLOY_BRANCH` | `main` |
| `GHCR_IMAGE_PREFIX` | `ghcr.io/bula393/blocia` |
| `DOKPLOY_URL` | `https://policloud.ipm.edu.ar` |
| `DOKPLOY_CLASIFICADOR_APPLICATION_ID` | `eVTqos01ugqO1i1s-YDxc` |
| `DOKPLOY_BACK_APPLICATION_ID` | `CdbClN8o2saQvhFa2iOmK` |
| `DOKPLOY_FRONT_APPLICATION_ID` | `o7wO6_qhR5KcKPT9FMYak` |
| `IMAGE_PLATFORMS` | Opcional; por defecto `linux/amd64`. |

Los tres IDs son de las Applications `clasificador`, `back` y `front` de este proyecto; no uses el ID del proyecto ni los IDs de los recursos Compose anteriores.

En **Settings → Secrets and variables → Actions → Secrets**, agregá `DOKPLOY_API_KEY` con una API key que generes desde tu cuenta Dokploy. La clave se manda a la API del mismo Dokploy para actualizar el tag Docker y solicitar cada despliegue; nunca se imprime en los logs. GitHub usa un Environment llamado `production` para el secreto. Si lo creás, colocá allí el secreto y asegurate de que su nombre sea exactamente `production`; las variables de selección y configuración de arriba deben quedar disponibles como Repository variables.

Dejá vacías las credenciales GHCR: los tres paquetes son públicos. Si los hacés privados, agregá como Repository variable `GHCR_USERNAME` y como Actions secret `GHCR_READ_TOKEN` (token GitHub con permiso `read:packages`). `DOKPLOY_API_KEY` y el token de lectura de GHCR tienen propósitos distintos.

La API de Dokploy utilizada es [application.saveDockerProvider](https://docs.dokploy.com/docs/api/reference-application) para guardar la imagen y [application.deploy](https://docs.dokploy.com/docs/api/reference-application) para solicitar el despliegue.

## 6. Qué pasa en cada push

1. Un push a `main` inicia `CI`: pruebas del backend, frontend, navegador, validaciones de despliegue y construcción de contenedores.
2. Solo si CI termina correctamente, GitHub publica las tres imágenes etiquetadas con el SHA completo de ese commit.
3. Cuando `DEPLOY_ENABLED=true`, Actions verifica que el commit siga siendo la punta de `main`, actualiza las imágenes Docker de las Applications y solicita el despliegue en orden `clasificador` → `back` → `front`.
4. Abrí **Deployments** y **Logs** de cada Application en Dokploy para seguir su estado. Un resultado exitoso de Actions confirma que Dokploy aceptó las solicitudes; revisá allí que los contenedores queden saludables y que el dominio responda.

La primera vez, mantené `DEPLOY_ENABLED=false` hasta completar PostgreSQL, las variables, los volúmenes, el dominio y la API key. Luego habilitalo y podés ejecutar **Actions → Deploy to Dokploy → Run workflow** para probar manualmente. El workflow manual vuelve a ejecutar CI antes de publicar. Los pushes a otras ramas y los pull requests ejecutan las comprobaciones, pero no despliegan producción.

El workflow conserva el SHA completo de cada versión. Para hacer rollback, elegí el SHA anterior y volvé a colocar su imagen en la Application correspondiente desde Dokploy. Conservá la base y su respaldo antes de actualizar el esquema; un rollback de imagen no revierte cambios de datos.

CI conserva resultados JUnit, evidencias del navegador e informe de dependencias en **Artifacts**. Los fallos de prueba o construcción detienen la publicación; el informe de dependencias es informativo y no modifica el código automáticamente.

## Alternativa: Docker Compose

Si preferís administrar contenedores mediante Compose en lugar de las tres Applications, el repositorio también contiene [`deploy/inference/compose.yaml`](../deploy/inference/compose.yaml), [`deploy/api/compose.yaml`](../deploy/api/compose.yaml) y [`deploy/frontend/compose.yaml`](../deploy/frontend/compose.yaml), además de [`deploy/dokploy.compose.yaml`](../deploy/dokploy.compose.yaml) como configuración conjunta. Esa alternativa requiere una red externa compartida y la automatización de Compose; no mezcles los IDs o los pasos de Compose con el workflow de Applications descrito arriba. Consultá la [guía oficial de Docker Compose en Dokploy](https://docs.dokploy.com/docs/core/docker-compose).

## Operación, datos y recuperación

- Cada tarjeta de Dokploy tiene sus propios **Deployments**, **Logs** y controles de reinicio; abrí el recurso que quieras revisar. En GitHub, abrí la ejecución y descargá los informes cuando una comprobación falle.
- `/healthz` confirma que responde Nginx. `/api/health` confirma la base de datos. `/api/ready` exige base e IA disponibles. `/version.json` identifica la imagen de la interfaz.
- El primer arranque del clasificador puede tardar por la descarga de modelos; seguí su estado en **Deployments** y **Logs** de Dokploy.
- Conservá el servicio PostgreSQL y su volumen. Configurá y probá backups en la pestaña **Backup** de Dokploy. Guardá `BLOCIA_ENCRYPTION_KEY` en un lugar seguro y mantené el mismo valor entre despliegues para poder descifrar las credenciales de proveedores.
- Para volver a una versión anterior, colocá en cada Application el tag completo del SHA anterior publicado y desplegá `clasificador`, `back` y `front` en ese orden. Conservá los volúmenes. Un rollback de código no revierte migraciones de datos; guardá una copia antes de cambios de esquema.
- La preparación de IA rechaza cambios de revisión que sobrescribirían pesos existentes. Para actualizar modelos, hacé una copia del volumen y ejecutá explícitamente `python -m ml.prepare --classifier-only --force-model-revision` dentro del contenedor de `clasificador`; omití `--classifier-only` si habilitaste Qwen. Reiniciá esa Application después. No se forza ese cambio en cada despliegue.
- El back usa PostgreSQL mediante `DATABASE_URL`; SQLite queda como opción local de desarrollo y pruebas.

## Si ya desplegaste la configuración conjunta con Compose

Las instrucciones de este apartado aplican solo si migrás una instalación anterior que guardaba datos en SQLite. La nueva versión no copia automáticamente el archivo SQLite a PostgreSQL. Antes de cambiar, respaldá la base y sus claves; importá los datos con un procedimiento de migración antes de abrir el nuevo back. No retires el volumen viejo hasta verificar cuentas, chats y credenciales en PostgreSQL.

El antiguo [`deploy/dokploy.compose.yaml`](../deploy/dokploy.compose.yaml) permanece como alternativa conjunta manual; el workflow descrito arriba usa las tres Applications y la API de Dokploy.

## Probar los servicios en tu equipo

Copiá `deploy/.env.example` a `.env`, completá los secretos, poné `FRONTEND_URL=http://localhost:8080`, y ejecutá:

```sh
docker compose --env-file .env up --build -d
docker compose logs -f inference
```

Abrí `http://localhost:8080` cuando los servicios estén listos. El Compose local usa SQLite y cookies de desarrollo para HTTP. La configuración conjunta `deploy/dokploy.compose.yaml` agrega PostgreSQL como contenedor independiente y conserva sus datos en `database-data`.

Para verificar archivos sin desplegar:

```sh
python scripts/validate_deployment.py
docker compose --env-file deploy/inference/.env.example -f deploy/inference/compose.yaml config --quiet
docker compose --env-file deploy/api/.env.example -f deploy/api/compose.yaml config --quiet
docker compose --env-file deploy/frontend/.env.example -f deploy/frontend/compose.yaml config --quiet
```

El validador requiere PyYAML, incluido en las dependencias del backend. `config --quiet` evita imprimir valores secretos. Para detener los servicios conservando los datos, usá `docker compose down`.
