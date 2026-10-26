# BloqIA — cobertura del mockup

Inventario verificado el 5 de octubre de 2026 a partir de las pantallas, contratos, servicios y rutas existentes. La propuesta se consulta desde `/mockup`. Los datos de sus vistas son demostrativos; no crean cuentas, envían consultas ni guardan credenciales reales.

## Pantallas y funciones implementadas

| Apartado actual | Funciones verificadas | Estados relevantes para el diseño |
|---|---|---|
| Inicio `/` | Presentación del producto, ejemplo de conversación, enlaces a acceso y registro; con sesión, nuevo chat y configuración técnica | Visitante, usuario autenticado |
| Acceso `/login` | Correo, contraseña, iniciar sesión, pasar a registro | Campos vacíos, validación, credenciales inválidas, sesión iniciada |
| Registro `/register` | Correo único, contraseña segura, edad y profesión; creación de cuenta y sesión | Contraseña incompleta/segura, edad inválida, correo duplicado, error, cuenta creada |
| Google `/auth/google/callback` | Consumir resultado de OAuth; acceder a una cuenta o completar edad/profesión faltantes | Verificando cuenta, datos faltantes, error/cancelación, regresar al acceso |
| Chat `/nuevo-chat` | Crear conversaciones, listar historial propio, abrir un chat por URL, borrar chat y mensajes, elegir modelo, componer consultas, recibir Markdown | Chat vacío, historial vacío, carga, consulta pendiente, respuesta, error y reintento, confirmación de borrado |
| Clasificación de consultas | Consulta general, análisis personal y decisión personal; mostrar confianza, estado de aceptación, revisión humana y probabilidades | Aceptada, baja confianza, requiere revisión, decisión personal |
| Perfil `/perfil` | Editar nombre visible, edad y profesión; guardar cambios; consultar correo, método de acceso y estado técnico; cerrar sesión | Cargando, error/reintento, sin cambios, editado, guardando, actualizado |
| Configuración `/perfil-tecnico` | Google AI, Groq, OpenRouter, OpenAI y Anthropic; agregar/reemplazar/quitar clave; ver clave enmascarada, modelos y capacidades; actualizar catálogo; mostrar más/menos modelos; abrir condiciones y consola del proveedor | Sin clave, conectada, credencial inválida/atención, catálogo vacío, cargando, error, proveedor no disponible |
| Uso — panel global | Mensajes enviados hoy, consultas de catálogos hoy, proveedores conectados y última actividad | Datos vacíos, datos con actividad, carga, error, abrir/cerrar panel |
| Navegación global | Inicio, chat, configuración, perfil desde avatar, uso y cierre de sesión | Navegación pública/privada, vista móvil, sesión vencida o inválida |
| Acceso requerido | Impedir mostrar contenido privado sin sesión válida; ofrecer iniciar sesión | Sesión ausente, inválida o vencida |

## Comportamiento que la propuesta debe respetar

- El producto ayuda a comprender y ordenar ideas, manteniendo la decisión en manos del usuario.
- `no_personal` y `personal_informativa` pueden generar una respuesta con el modelo seleccionado. `personal_decision` no se envía al generador: guarda una respuesta fija y su clasificación.
- La clasificación se realiza localmente. La generación puede realizarse localmente o con un proveedor externo, según la selección y la disponibilidad.
- El selector integra modelos habilitados por claves propias y opciones gratuitas disponibles desde el servidor. Qwen3-0.6B local sólo está disponible si sus archivos están instalados.
- Los modelos dependen del catálogo y del estado de la conexión. Un catálogo visible no garantiza crédito disponible ni una generación exitosa.
- OpenRouter limita la selección y el envío a rutas gratuitas.
- La espera tiene dos fases: clasificar la consulta y esperar la respuesta del modelo. El compositor y los cambios de conversación se deshabilitan mientras hay un envío en curso.
- El límite de entrada configurado actualmente es de 4.000 caracteres. El campo crece hasta su altura máxima; Enter envía y Shift + Enter añade un salto.
- Los ejemplos del chat rellenan el compositor, sin enviar inmediatamente.
- El historial es privado por usuario, se guarda en este equipo y admite eliminación. El nombre del chat se toma automáticamente de la primera consulta.
- El perfil editable incluye nombre visible, edad y profesión. El correo y los métodos de acceso se muestran como información protegida.
- Las claves guardadas aparecen enmascaradas. La interfaz debe distinguir el acceso con Google de una clave de Google AI, y una clave de OpenAI de una suscripción de ChatGPT.
- El aviso de contexto explica que nombre visible, edad, profesión e intercambios recientes pueden enviarse al proveedor externo junto con la consulta.
- La versión móvil necesita acceso explícito al historial, navegación accesible y un compositor que conserve espacio de lectura.

## Cobertura propuesta de `/mockup`

Las vistas se presentan dentro del prototipo y comparten identidad, componentes y navegación. Las rutas funcionales actuales permanecen separadas del entorno demostrativo.

| Vista del prototipo | Cobertura |
|---|---|
| Inicio | Mensaje de autonomía, identidad visual, imágenes editoriales, introducción del producto, ejemplo de conversación, recorrido de clasificación y explicación del uso local o con proveedores; CTA a acceso/registro |
| Chat | Historial, selección de conversación, nuevo chat, compositor, modelo, respuesta, detalles de clasificación, clasificación de decisión personal y confirmación de borrado |
| Perfil | Formulario personal, cambios pendientes, guardado simulado y datos protegidos de la cuenta |
| Proveedores y modelos | Los cinco proveedores, clave enmascarada, campo de conexión, estado de conexión, catálogo y capacidades, expansión de modelos y actualización simulada |
| Actividad | Panel de uso con las cuatro métricas reales y cierre del panel |
| Acceso | Correo/contraseña, validación demostrativa, entrada al prototipo autenticado y enlace al registro |
| Registro | Los cuatro datos reales, requisito de contraseña, validación y acceso a la cuenta demostrativa |
| Google | Estado de conexión y formulario de edad/profesión faltantes |
| Acceso requerido | Recuperar acceso ante una sesión no válida |
| Identidad visual | Logo, paleta y criterios de uso; exposición del sistema propuesto como parte del entregable de diseño |

La inclusión de imágenes, composición editorial y efectos de scroll responde a la solicitud de diseño. No implica una nueva función del chat ni una promesa de capacidades del modelo. El movimiento debe respetar `prefers-reduced-motion`, conservar la navegación por teclado y evitar interferir con lectura, formularios o composición de mensajes.

## Funciones parciales y ausencias deliberadas

### Google

El backend, la función de inicio de OAuth y la pantalla de callback existen. Los formularios actuales de acceso y registro no muestran el botón para iniciar Google. El prototipo puede presentar ese recorrido porque existe en el sistema, identificando la conexión como demostrativa; no debe afirmar que la integración del despliegue real está configurada.

### Cuotas, temporizador y bloqueo

El documento histórico de diseño propone tres consultas personales diarias, temporizador, medidor de tiempo y bloqueo de 24 horas. No hay implementación de esa política en las rutas de chat, servicios ni estado actual de la interfaz. El componente `MedidorTiempo` existe, pero no se usa. Por ello, el mockup no incluye una cuota inventada, cuenta regresiva ni bloqueo por consumo. La clasificación de una decisión personal sí se cubre.

### Otras funciones ausentes

No se presentan como funciones disponibles: recuperar o cambiar contraseña, cambiar correo, renombrar/buscar/exportar/compartir chats, favoritos, regenerar respuestas, adjuntar archivos, enviar imágenes, entrada de voz, compra de suscripciones, facturación de BloqIA ni gráficos históricos de clasificación. El manifiesto PWA existe sin iconos; no se promete una experiencia completa de instalación o chat sin conexión.

## Fuentes comprobadas

- `front/src/app/router.tsx`, `routeGuard.ts` y navegación.
- Pantallas `Inicio`, `Login`, `Register`, `GoogleCallback`, `NuevoChat`, `Perfil` y `PerfilTecnico`.
- `ChasisBloqIA`, `RielLateral`, `ProfessionField` y APIs de autenticación, chat, perfil, perfil técnico y uso.
- `back/app/presentation/chat_routes.py` y rutas de autenticación, perfil, proveedores y uso.
- Servicios de contexto, generación, catálogos y repositorio de conversaciones; `back/config/chat.yaml`.
- Specs de módulo de usuario y corrección gráfica; documento de identidad visual y README.

## Comprobación de sintaxis existente

La copia actual de `front/src/pages/NuevoChat.tsx` no tiene el supuesto cierre prematuro seguido de un estado fuera del componente. `ChatMessage` termina antes de la interfaz de opciones y de `providerLabel`; `sendPhase` está dentro de `export function NuevoChat()`. El parser de TypeScript sobre este archivo devolvió cero diagnósticos de sintaxis. Esta comprobación fue sólo de lectura, sin ejecutar una compilación ni modificar la fuente, y no sustituye una validación completa de tipos o del comportamiento de la aplicación.
