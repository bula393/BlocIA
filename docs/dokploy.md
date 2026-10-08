# Subir BlocIA a Dokploy

En el proyecto `BloqIa` se usan tres servicios **Application** independientes con proveedor **Docker**: `back`, `front` y `clasificador`. GitHub Actions publica las imágenes y, cuando se habilita `DEPLOY_ENABLED`, actualiza el tag y solicita el despliegue de cada Application mediante la API de Dokploy. Los archivos de `deploy/*/compose.yaml` quedan como alternativa para quien prefiera administrar recursos Docker Compose.

| Servicio | Función | Puerto del contenedor | Datos persistentes |
| --- | --- | --- | --- |
| `back` | `ghcr.io/bula393/blocia-api:<SHA>` | 8000, privado | Volumen en `/app/data` |
| `front` | `ghcr.io/bula393/blocia-frontend:<SHA>` | 8080, público | Ninguno |
| `clasificador` | `ghcr.io/bula393/blocia-inference:<SHA>` | 8001, privado | Volumen en `/app/models` |

Configurá únicamente un dominio público para `front`. La API y el clasificador permanecen privados. Al completar los servicios, asegurate de mantener un volumen persistente para los datos del backend y otro para los modelos del clasificador; los tags de imagen son inmutables y cambian en cada push aprobado.

El código está organizado en `front/src/features/chat/` para el chat y sus componentes; `back/app/bootstrap.py` para montar la API; `back/app/application/` para casos de uso; `back/app/presentation/` para contratos HTTP; `back/app/infrastructure/` para persistencia y transportes; y `back/app/inference_main.py` para la IA independiente.

## 1. Preparar dominio y servidor

Creá un registro DNS `A` de tu dominio hacia la IP del servidor de Dokploy. El servidor debe permitir que Dokploy atienda HTTP/HTTPS y pueda descargar imágenes desde GHCR y modelos desde Hugging Face. Usá Linux con Docker; la construcción predeterminada es para `linux/amd64`.

Los límites iniciales son 6 GB para inferencia, 512 MB para la API y 128 MB para la interfaz. Reservá memoria adicional para Dokploy y el sistema. Son valores iniciales ajustables en el `.env.example` de cada servicio; el consumo real depende de los modelos y las consultas. No se comprobó el rendimiento en tu servidor.

Por defecto, `BLOCIA_ENABLE_LOCAL_CHAT=0` instala solamente el clasificador. Para generar respuestas, conectá un proveedor desde Perfil técnico, configurá una credencial del servidor, o cambiá esa variable a `1` para instalar Qwen3-0.6B. La primera instalación descarga pesos en el volumen; puede tardar varios minutos. Los despliegues siguientes reutilizan esos archivos.

## 2. Crear las tres Applications en Dokploy

En el proyecto y entorno de producción que ya abriste, creá tres recursos de tipo **Application**. Usá el mismo servidor y el proveedor **Docker** para cada uno. No elijas Docker Compose para este flujo.

En cada servicio, completá el proveedor Docker de esta manera:

| Application | Docker Image inicial | Registry URL |
| --- | --- | --- |
| `back` | `ghcr.io/bula393/blocia-api:SHA_COMPLETO` | `ghcr.io` |
| `front` | `ghcr.io/bula393/blocia-frontend:SHA_COMPLETO` | `ghcr.io` |
| `clasificador` | `ghcr.io/bula393/blocia-inference:SHA_COMPLETO` | `ghcr.io` |

Reemplazá `SHA_COMPLETO` por los 40 caracteres del commit que Actions publicó más recientemente; el resumen de la ejecución y la pestaña **Packages** muestran el tag exacto. Las imágenes son públicas, así que podés dejar vacíos usuario y contraseña del registro. No uses `latest`: cada versión queda identificada y se puede revertir. El workflow actualiza estas imágenes al SHA del push que haya pasado las pruebas. La aplicación `front` debe escuchar en el puerto de contenedor `8080`, `back` en `8000` y `clasificador` en `8001`.

En `back`, agregá un volumen persistente montado en `/app/data`. En `clasificador`, agregá otro volumen persistente montado en `/app/models`; la descarga inicial del modelo puede demorar. No publiques los puertos `8000` ni `8001` hacia internet. Solo `front` requiere un dominio público.

Las imágenes de GitHub se consultan desde [GHCR](https://github.com/bula393?tab=packages). Para las imágenes públicas no hace falta crear credenciales del registro en Dokploy. Si después hacés privados los paquetes, creá un token de GitHub con `read:packages` y configurá un Registry GHCR con ese usuario y token. Actions publica con su `GITHUB_TOKEN` automático. Referencias: [GHCR en Dokploy](https://docs.dokploy.com/docs/core/registry/ghcr) y [permisos del Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry).

## 3. Variables de cada Application

En la pestaña **Environment** de cada Application, agregá las variables de runtime de esta tabla. Los archivos `.env.example` de `deploy/` son para la alternativa Compose; no copies sus variables de red, volúmenes, `GHCR_IMAGE_PREFIX` o `RELEASE_TAG` a estas Applications.

| Application | Variable | Valor |
| --- | --- | --- |
| `back` | `FRONTEND_URL` | `https://TU_DOMINIO`, sin barra final |
| `back` | `ACCESS_TOKEN_SECRET` | Secreto aleatorio de al menos 32 caracteres |
| `back` | `BLOCIA_LOCK_MINUTES` | Minutos de bloqueo deseados; `1440` equivale a un día |
| `back` | `BLOCIA_INFERENCE_URL` | `http://blocia-clasificador-nrn9qa:8001` |
| `back` | `BLOCIA_INFERENCE_TOKEN` | Secreto aleatorio compartido con `clasificador` |
| `front` | `BLOCIA_API_UPSTREAM` | `bloqia-back-b1bgga:8000` |
| `clasificador` | `BLOCIA_INFERENCE_TOKEN` | El mismo valor configurado en `back` |
| `clasificador` | `BLOCIA_ENABLE_LOCAL_CHAT` | `0` para solo clasificar; `1` habilita Qwen local y requiere más memoria |

Los nombres internos `blocia-clasificador-nrn9qa` y `bloqia-back-b1bgga` aparecen debajo del título de cada Application en Dokploy. Las dos Applications deben compartir la red interna de Dokploy para que puedan resolverse entre sí. Si Dokploy vuelve a generar esos nombres al recrear un servicio, actualizá las URLs correspondientes. No publiques los puertos `8000` ni `8001` al exterior.

Generá secretos distintos en tu equipo con `python -c "import secrets; print(secrets.token_urlsafe(48))"`. `BLOCIA_INFERENCE_TOKEN` debe tener el mismo valor en API e IA; `ACCESS_TOKEN_SECRET` debe ser diferente. Las credenciales de proveedores (`BLOCIA_DEFAULT_*_TOKEN`) son opcionales; también se pueden conectar credenciales por usuario desde la app. Google Login es opcional y requiere `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` y registrar `https://TU_DOMINIO/api/auth/google/callback` como URL de retorno. `BLOCIA_ENCRYPTION_KEY` también es opcional: si se deja vacía, la API la conserva en `/app/data`. No cambies esa clave si ya hay credenciales guardadas.

Generá secretos distintos en tu equipo con `python -c "import secrets; print(secrets.token_urlsafe(48))"`. Las variables `BLOCIA_DEFAULT_*_TOKEN` son opcionales; también se pueden conectar credenciales por usuario desde la app. Google Login es opcional y requiere `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` y registrar la URL de retorno exacta. `BLOCIA_ENCRYPTION_KEY` también es opcional: si se deja vacía, la API la conserva en `/app/data`. No cambies esa clave si ya hay credenciales guardadas.

## 4. Configurar el dominio público

En la Application `front`, abrí **Domains → Add Domain** y completá el host público que tengas configurado en DNS. Apuntá un registro DNS `A` a la IP del servidor Dokploy. Configurá el puerto de contenedor `8080`, el path `/` y HTTPS con Let's Encrypt. No agregues dominios públicos a `back` ni `clasificador`. Revisá y guardá el dominio en Dokploy según su [documentación oficial de Applications](https://docs.dokploy.com/docs/core/applications).

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

La primera vez, mantené `DEPLOY_ENABLED=false` hasta completar las variables, los volúmenes persistentes, el dominio y la API key. Luego habilitalo y podés ejecutar **Actions → Deploy to Dokploy → Run workflow** para probar manualmente. El workflow manual vuelve a ejecutar CI antes de publicar. Los pushes a otras ramas y los pull requests ejecutan las comprobaciones, pero no despliegan producción.

El workflow conserva el SHA completo de cada versión. Para hacer rollback, elegí el SHA anterior y volvé a colocar su imagen en la Application correspondiente desde Dokploy. Las migraciones de datos no se revierten automáticamente; conservá los volúmenes y respaldá `/app/data` antes de cambios de esquema.

CI conserva resultados JUnit, evidencias del navegador e informe de dependencias en **Artifacts**. Los fallos de prueba o construcción detienen la publicación; el informe de dependencias es informativo y no modifica el código automáticamente.

## Alternativa: Docker Compose

Si preferís administrar contenedores mediante Compose en lugar de las tres Applications, el repositorio también contiene [`deploy/inference/compose.yaml`](../deploy/inference/compose.yaml), [`deploy/api/compose.yaml`](../deploy/api/compose.yaml) y [`deploy/frontend/compose.yaml`](../deploy/frontend/compose.yaml), además de [`deploy/dokploy.compose.yaml`](../deploy/dokploy.compose.yaml) como configuración conjunta. Esa alternativa requiere una red externa compartida y la automatización de Compose; no mezcles los IDs o los pasos de Compose con el workflow de Applications descrito arriba. Consultá la [guía oficial de Docker Compose en Dokploy](https://docs.dokploy.com/docs/core/docker-compose).

## Operación, datos y recuperación

- Cada tarjeta de Dokploy tiene sus propios **Deployments**, **Logs** y controles de reinicio; abrí el recurso que quieras revisar. En GitHub, abrí la ejecución y descargá los informes cuando una comprobación falle.
- `/healthz` confirma que responde Nginx. `/api/health` confirma la base de datos. `/api/ready` exige base e IA disponibles. `/version.json` identifica la imagen de la interfaz.
- El primer arranque del clasificador puede tardar por la descarga de modelos; seguí su estado en **Deployments** y **Logs** de Dokploy.
- Conservá los volúmenes y las claves entre despliegues. Respaldá `/app/data`, que contiene SQLite y la clave de cifrado. Para una copia consistente de SQLite, pausá la Application `back` o usá la operación de backup de SQLite; no copies solamente el archivo principal mientras escribe en WAL.
- Para volver a una versión anterior, colocá en cada Application el tag completo del SHA anterior publicado y desplegá `clasificador`, `back` y `front` en ese orden. Conservá los volúmenes. Un rollback de código no revierte migraciones de datos; guardá una copia antes de cambios de esquema.
- La preparación de IA rechaza cambios de revisión que sobrescribirían pesos existentes. Para actualizar modelos, hacé una copia del volumen y ejecutá explícitamente `python -m ml.prepare --classifier-only --force-model-revision` dentro del contenedor de `clasificador`; omití `--classifier-only` si habilitaste Qwen. Reiniciá esa Application después. No se forza ese cambio en cada despliegue.
- Una API y SQLite son la configuración actual. Para escalar a varias instancias de API hace falta migrar la persistencia a una base compartida.

## Si ya desplegaste la configuración conjunta con Compose

Las instrucciones de este apartado aplican solo si migrás una instalación anterior desde Compose a Applications. Podés reutilizar los datos existentes configurando en cada Application los nombres reales de los volúmenes previos. Consultá esos nombres en Dokploy. Pausá la API anterior antes de iniciar la nueva sobre SQLite y conservá su clave de cifrado. No borres los volúmenes al retirar el recurso anterior.

El antiguo [`deploy/dokploy.compose.yaml`](../deploy/dokploy.compose.yaml) permanece como alternativa conjunta manual; el workflow descrito arriba usa las tres Applications y la API de Dokploy.

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
