# Subir BlocIA a Dokploy

Creá **tres servicios diferentes en Dokploy**, dentro del mismo proyecto y servidor: `blocia-inference`, `blocia-api` y `blocia-frontend`. Cada recurso es de tipo **Docker Compose**, origen **Raw**, y contiene solamente su propio contenedor. Podés reiniciar, actualizar y consultar registros de cada recurso por separado.

| Servicio | Función | Puerto del contenedor | Datos persistentes |
| --- | --- | --- | --- |
| frontend | Interfaz y acceso a la API desde el mismo dominio | 8080 | Ninguno |
| api | Usuarios, conversaciones, consentimiento y límites | 8000, privado | `api-data`, montado en `/app/data` |
| inference | Clasificación y, opcionalmente, Qwen local | 8001, privado | `inference-models`, montado en `/app/models` |

El navegador usa `https://TU_DOMINIO/api/...`. Nginx deriva esas solicitudes a `blocia-prod-api:8000`; la API usa `http://blocia-prod-inference:8001` y un secreto compartido. Solamente `frontend` lleva un dominio público. SQLite queda en el volumen de la API, con una sola instancia del servicio.

El código está organizado en `front/src/features/chat/` para el chat y sus componentes; `back/app/bootstrap.py` para montar la API; `back/app/application/` para casos de uso; `back/app/presentation/` para contratos HTTP; `back/app/infrastructure/` para persistencia y transportes; y `back/app/inference_main.py` para la IA independiente.

## 1. Preparar dominio y servidor

Creá un registro DNS `A` de tu dominio hacia la IP del servidor de Dokploy. El servidor debe permitir que Dokploy atienda HTTP/HTTPS y pueda descargar imágenes desde GHCR y modelos desde Hugging Face. Usá Linux con Docker; la construcción predeterminada es para `linux/amd64`.

Los límites iniciales son 6 GB para inferencia, 512 MB para la API y 128 MB para la interfaz. Reservá memoria adicional para Dokploy y el sistema. Son valores iniciales ajustables en el `.env.example` de cada servicio; el consumo real depende de los modelos y las consultas. No se comprobó el rendimiento en tu servidor.

Por defecto, `BLOCIA_ENABLE_LOCAL_CHAT=0` instala solamente el clasificador. Para generar respuestas, conectá un proveedor desde Perfil técnico, configurá una credencial del servidor, o cambiá esa variable a `1` para instalar Qwen3-0.6B. La primera instalación descarga pesos en el volumen; puede tardar varios minutos. Los despliegues siguientes reutilizan esos archivos.

## 2. Crear la red y los tres recursos independientes

1. En Dokploy, creá el proyecto `BlocIA` y su entorno de producción. Seleccioná el mismo servidor para los tres recursos.
2. En la terminal del servidor, creá una red compartida una sola vez: `docker network create blocia-production`. Si ya existe, conservála. También podés ejecutar `sh scripts/create_deployment_network.sh blocia-production` desde una copia de este repositorio en ese servidor; el script verifica o crea la red sin reemplazarla.
3. Creá los siguientes **tres servicios Docker Compose**; seleccioná **Docker Compose**, origen **Raw**, en cada uno:

| Recurso de Dokploy | Archivo que pegás en Raw | Variables que copiás en Environment |
| --- | --- | --- |
| `blocia-inference` | [`deploy/inference/compose.yaml`](../deploy/inference/compose.yaml) | [`deploy/inference/.env.example`](../deploy/inference/.env.example) |
| `blocia-api` | [`deploy/api/compose.yaml`](../deploy/api/compose.yaml) | [`deploy/api/.env.example`](../deploy/api/.env.example) |
| `blocia-frontend` | [`deploy/frontend/compose.yaml`](../deploy/frontend/compose.yaml) | [`deploy/frontend/.env.example`](../deploy/frontend/.env.example) |

4. Guardá cada configuración. Conservá sus marcadores `x-blocia-deployment` y `x-blocia-service`, y los nombres de volumen. No actives Isolated Deployments: estos archivos usan la red externa común.
5. Dejá desactivado el Auto Deploy propio de Dokploy en los tres recursos; GitHub coordinará las pruebas y las actualizaciones.

La red `blocia-production` conecta los tres recursos. Los alias `blocia-prod-api` y `blocia-prod-inference` permiten encontrarlos aunque cambie el nombre que Dokploy asigna a los contenedores. Sólo frontend se conecta además con `dokploy-network` para recibir tráfico del dominio. No hay dependencias de Compose entre archivos independientes; el workflow despliega en el orden IA → API → frontend.

Dokploy admite recursos Compose y variables mediante referencias `${VARIABLE}` en cada archivo. Consultá la [guía oficial de Compose](https://docs.dokploy.com/docs/core/docker-compose).

## 3. Completar variables en Dokploy

En **Environment** de cada recurso, copiá solamente el ejemplo de su carpeta indicado arriba. Completá los valores según esta tabla. Los ejemplos contienen valores ficticios; los secretos reales quedan en Dokploy.

| Variable | Valor que debés colocar |
| --- | --- |
| `GHCR_IMAGE_PREFIX` | `ghcr.io/bula393/blocia`, si seguís usando este repositorio. Usá el mismo valor en GitHub. |
| `RELEASE_TAG` | SHA completo de 40 caracteres de un commit. Actions lo actualizará al desplegar. No agregues `sha-`. |
| `BLOCIA_NETWORK_NAME` | `blocia-production` en los tres recursos; debe coincidir con la red creada en el servidor. |
| `BLOCIA_SERVICE_NAMESPACE` | `blocia-prod` en los tres recursos. Usá otro prefijo si alojás otra instalación de BlocIA en ese servidor. |
| `FRONTEND_URL` | `https://TU_DOMINIO`, sin rutas ni barra final. |
| `ACCESS_TOKEN_SECRET` | Secreto aleatorio de al menos 32 caracteres. Conservá el mismo entre despliegues. |
| `BLOCIA_INFERENCE_TOKEN` | Otro secreto aleatorio, diferente del anterior. Copiá exactamente el mismo valor en API e IA; frontend no lo necesita. |
| `BLOCIA_LOCK_MINUTES` | Minutos de bloqueo, por defecto `1440`. |
| `BLOCIA_ENABLE_LOCAL_CHAT` | `0` para clasificar y usar proveedores; `1` para habilitar respuestas con Qwen local. |
| `GOOGLE_REDIRECT_URI` | Si usás acceso con Google: `https://TU_DOMINIO/api/auth/google/callback`. |

`GHCR_IMAGE_PREFIX`, `RELEASE_TAG`, `BLOCIA_NETWORK_NAME` y `BLOCIA_SERVICE_NAMESPACE` deben coincidir en los tres recursos. `FRONTEND_URL`, `ACCESS_TOKEN_SECRET`, proveedor de IA y variables de Google pertenecen a la API. `BLOCIA_ENABLE_LOCAL_CHAT` y los límites de memoria del modelo pertenecen a inferencia.

Podés generar cada secreto en tu equipo con `python -c "import secrets; print(secrets.token_urlsafe(48))"`. Ejecutalo dos veces y colocá cada resultado en su campo correspondiente.

Las variables `BLOCIA_DEFAULT_*_TOKEN` son opcionales; también podés conectar credenciales por usuario desde la app. Google Login necesita `GOOGLE_CLIENT_ID` y `GOOGLE_CLIENT_SECRET`, además de registrar la URL de retorno exacta en Google. Registro y acceso con contraseña funcionan sin Google.

`BLOCIA_ENCRYPTION_KEY` es una clave Fernet opcional. Si la dejás vacía, la API crea una clave dentro de `/app/data`; se conserva con el volumen. Si ya tenés datos, conservá la clave usada originalmente. Cambiarla impide leer los tokens guardados.

## 4. Conectar el dominio

En **blocia-frontend**, abrí **Domains → Add Domain** y completá:

| Campo | Valor |
| --- | --- |
| Service | `frontend` |
| Host | `TU_DOMINIO`, sin `https://` |
| Path | `/` |
| Container Port | `8080` |
| HTTPS | Activado, certificado Let's Encrypt |

Guardá y revisá **Preview Compose**. `frontend` debe conservar la red de la aplicación y la conexión con Traefik. Esta configuración usa `dokploy-network`; dejá desactivada la opción Isolated Deployments para seguir este archivo tal cual. No agregues dominio ni puertos públicos a `api` o `inference`. Los dominios se aplican en el siguiente despliegue, según la [documentación oficial de Domains](https://docs.dokploy.com/docs/core/docker-compose/domains).

## 5. Dar acceso a las imágenes de GitHub

Después de un push a `main`, si `CI` termina correctamente, Actions publica estas imágenes con el SHA completo del commit. En Dokploy, la correspondencia es:

```text
back         → ghcr.io/bula393/blocia-api:SHA_COMPLETO
front        → ghcr.io/bula393/blocia-frontend:SHA_COMPLETO
clasificador → ghcr.io/bula393/blocia-inference:SHA_COMPLETO
```

En los tres campos **Registry URL** usá `ghcr.io`. `SHA_COMPLETO` se reemplaza por el SHA de 40 caracteres que aparece en la ejecución exitosa de GitHub Actions; cada servicio usa el sufijo de imagen indicado arriba. La publicación de imágenes no requiere `DEPLOY_ENABLED=true`; esa variable habilita el paso separado que actualiza y despliega los tres recursos Docker Compose.

Para paquetes privados, creá un token clásico de GitHub con permiso `read:packages` y acceso a esos paquetes. En Dokploy, agregá un **Registry** para el servidor de despliegue: URL `ghcr.io`, usuario de GitHub y ese token como contraseña. Probá la conexión. Si una organización requiere SSO, autorizá el token para ella. Alternativamente, podés configurar los tres paquetes como públicos una vez creados.

El token que permite a Dokploy descargar imágenes es diferente de `DOKPLOY_API_KEY`. Actions publica con su `GITHUB_TOKEN` automático. Referencias: [GHCR en Dokploy](https://docs.dokploy.com/docs/core/registry/ghcr) y [permisos del Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry).

## 6. Completar GitHub Actions

En el repositorio, abrí **Settings → Secrets and variables → Actions**. Creá estas **Repository variables**:

| Variable | Valor |
| --- | --- |
| `DEPLOY_ENABLED` | `false` mientras configurás; `true` al terminar. Las pruebas funcionan aunque esté desactivado. |
| `DEPLOY_BRANCH` | `main`, o tu rama de producción. |
| `GHCR_IMAGE_PREFIX` | `ghcr.io/bula393/blocia`, igual que en Dokploy. Puede omitirse si coincide con el nombre del repositorio en minúsculas. |
| `DOKPLOY_URL` | `https://TU_DOKPLOY`, sin `/api` ni otras rutas. |
| `DOKPLOY_INFERENCE_COMPOSE_ID` | ID del recurso `blocia-inference`. |
| `DOKPLOY_API_COMPOSE_ID` | ID del recurso `blocia-api`. |
| `DOKPLOY_FRONTEND_COMPOSE_ID` | ID del recurso `blocia-frontend`. |
| `PUBLIC_HEALTH_URL` | `https://TU_DOMINIO/api/ready` |
| `FRONTEND_VERSION_URL` | `https://TU_DOMINIO/version.json` |
| `IMAGE_PLATFORMS` | Opcional: `linux/amd64`. Para un servidor ARM, `linux/arm64`; esa arquitectura requiere verificar sus imágenes en tu servidor. |

Cada ID se ve en la URL al abrir su recurso. Deben ser tres IDs distintos; no uses el ID del proyecto. El workflow anterior con un único `DOKPLOY_COMPOSE_ID` queda reemplazado por estas tres variables.

En Dokploy, generá una API key desde **Profile / API o CLI**. En GitHub creá el **Actions secret** `DOKPLOY_API_KEY` con ese valor. La clave se envía en `x-api-key`, conforme a la [API oficial de Dokploy](https://docs.dokploy.com/docs/api).

Creá un **Environment** de GitHub llamado `production`. Podés poner ahí el secreto `DOKPLOY_API_KEY` y las variables de Dokploy en lugar de hacerlo a nivel del repositorio. `DEPLOY_ENABLED`, `DEPLOY_BRANCH`, `GHCR_IMAGE_PREFIX` e `IMAGE_PLATFORMS` deben ser variables del repositorio, porque también se usan antes del job de producción. Para despliegue automático sin intervención, no agregues revisores obligatorios a ese entorno.

Si usás una organización, permití que Actions publique paquetes y que el repositorio tenga acceso a los paquetes existentes. Las credenciales de proveedores de IA y de usuarios quedan en Dokploy, no se necesitan para las pruebas de GitHub.

## 7. Primer despliegue y próximos pushes

1. Subí estos archivos al repositorio con un commit y push.
2. Confirmá que `CI` termina en verde en **Actions**; después se publican las tres imágenes con ese SHA.
3. Para despliegue automático, completá primero los IDs de los recursos Docker Compose, el dominio, la red compartida y los secretos indicados arriba; recién entonces colocá `DEPLOY_ENABLED=true`.
4. Ejecutá **Actions → Deploy to Dokploy → Run workflow**, eligiendo la rama configurada. La ejecución manual también corre las pruebas antes de publicar.
5. El flujo comprueba antes de modificar nada que los tres IDs correspondan al recurso Compose correcto, usen el mismo servidor y red, y compartan el secreto entre API e IA.
6. Actualiza `RELEASE_TAG` y `GHCR_IMAGE_PREFIX` en cada recurso conservando sus propias variables y volúmenes. Despliega IA → API → frontend y espera a que `/api/ready` y `/version.json` identifiquen el SHA esperado; también verifica el SHA de inferencia a través de la API. Abrí tu dominio y registrate para comprobar el funcionamiento.

Después, cada push a la rama de producción pasa por `CI` antes de publicar y desplegar. Los pushes a otras ramas y los pull requests ejecutan las comprobaciones. Un commit que ya no sea la punta de la rama no reemplaza una versión más reciente.

`CI` ejecuta pruebas del backend, pruebas y construcción del frontend, el flujo de consentimiento y cupo en navegador, validación de Compose y construcción de contenedores. Conserva resultados JUnit, evidencias del navegador e informe de dependencias en **Artifacts**. Los fallos de pruebas o construcción detienen el flujo; la auditoría de dependencias es informativa. Estos informes ayudan a depurar, pero no modifican el código automáticamente.

## Operación, datos y recuperación

- Cada tarjeta de Dokploy tiene sus propios **Deployments**, **Logs** y controles de reinicio; abrí el recurso que quieras revisar. En GitHub, abrí la ejecución y descargá los informes cuando una comprobación falle.
- `/healthz` confirma que responde Nginx. `/api/health` confirma la base de datos. `/api/ready` exige base e IA disponibles. `/version.json` identifica la imagen de la interfaz.
- El primer arranque puede tardar por la descarga de modelos. El flujo espera hasta 30 minutos en total; sus registros muestran qué servicio está pendiente.
- Conservá los tres recursos Compose, sus nombres de volumen y las claves entre despliegues. Configurá copias de seguridad de `api-data`; incluye SQLite y su clave de cifrado. Para una copia consistente de SQLite, pausá la API o usá la operación de backup de SQLite; no copies solamente el archivo principal mientras escribe en WAL.
- Para volver a una versión anterior, establecé `RELEASE_TAG` con el mismo SHA previamente publicado en los tres recursos y desplegá IA, API y frontend en ese orden. Conservá los volúmenes. Un rollback de código no revierte migraciones de datos; guardá una copia antes de cambios de esquema.
- La preparación de IA rechaza cambios de revisión que sobrescribirían pesos existentes. Para actualizar modelos, hacé una copia del volumen y ejecutá explícitamente `python -m ml.prepare --classifier-only --force-model-revision` dentro del contenedor de inferencia; omití `--classifier-only` si habilitaste Qwen. Reiniciá inferencia después. No se forza ese cambio en cada despliegue.
- Una API y SQLite son la configuración actual. Para escalar a varias instancias de API hace falta migrar la persistencia a una base compartida.

## Si ya desplegaste la configuración conjunta

Los tres recursos nuevos pueden reutilizar los datos existentes: configurá `BLOCIA_API_VOLUME_NAME` en API con el nombre real del volumen anterior y `BLOCIA_MODELS_VOLUME_NAME` en IA con el nombre real del volumen de modelos. Consultá esos nombres en los volúmenes del recurso anterior. Pausá la API anterior antes de iniciar la nueva sobre SQLite, y conservá su clave de cifrado. No borres los volúmenes al retirar el recurso anterior.

Los valores predeterminados crean `blocia-prod-api-data` y `blocia-prod-inference-models` en una instalación nueva. Si cambiás el namespace para otra instalación, los nombres predeterminados de volumen también usan ese prefijo; los campos `BLOCIA_*_VOLUME_NAME` permiten indicar un volumen existente.

El antiguo [`deploy/dokploy.compose.yaml`](../deploy/dokploy.compose.yaml) permanece como alternativa conjunta manual; GitHub Actions usa ahora los tres archivos independientes.

## Probar los servicios en tu equipo

Copiá `deploy/.env.example` a `.env`, completá los secretos, poné `FRONTEND_URL=http://localhost:8080`, y ejecutá:

```sh
docker compose --env-file .env up --build -d
docker compose logs -f inference
```

Abrí `http://localhost:8080` cuando los servicios estén listos. El Compose local conjunto usa cookies de desarrollo para HTTP. Los datos se guardan en volúmenes de Docker separados de tus carpetas de desarrollo.

Para verificar archivos sin desplegar:

```sh
python scripts/validate_deployment.py
docker compose --env-file deploy/inference/.env.example -f deploy/inference/compose.yaml config --quiet
docker compose --env-file deploy/api/.env.example -f deploy/api/compose.yaml config --quiet
docker compose --env-file deploy/frontend/.env.example -f deploy/frontend/compose.yaml config --quiet
```

El validador requiere PyYAML, incluido en las dependencias del backend. `config --quiet` evita imprimir valores secretos. Para detener los servicios conservando los datos, usá `docker compose down`.
