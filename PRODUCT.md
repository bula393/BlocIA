# BloqIA

<!-- impeccable:product-schema 1 -->

## Platform

web

## Product Purpose

Interfaz en español para estudiar, explorar ideas y resolver dudas de trabajo con asistencia de modelos de IA. El usuario conserva el criterio sobre decisiones personales.

## Users

La copia existente se dirige a personas que estudian o trabajan. No hay segmentación de público confirmada por el usuario; el mockup asume adultos que buscan un espacio de pensamiento claro.

## Capabilities and Constraints

React y TypeScript con Vite; backend Python. Inicio público y personal, acceso por contraseña, registro con correo/edad/profesión, callback Google, chat por usuario con historial y borrado, respuestas Markdown, selección de modelo, clasificación de consulta expandible, perfil editable, conexión de claves de Google/OpenAI/Anthropic/Groq/OpenRouter y actividad diaria.

Las consultas generales e informativas pueden generar respuestas; las decisiones personales reciben una respuesta fija y no se envían al generador. Las clases son no_personal, personal_informativa y personal_decision. Las decisiones sensibles pueden requerir revisión humana. Qwen local depende de los pesos instalados; los respaldos de servidor dependen de su configuración. El catálogo real depende de credenciales y proveedor.

No hay cuota personal, contador de bloqueo ni temporizador operativo en el código actual. No hay recuperación de contraseña ni carga de archivos implementada.

## Brand Commitments

Nombre BloqIA y voz rioplatense, con trato de vos. El usuario pidió una identidad editorial completa para el mockup y luego pidió aplicar esos diseños al programa actual. La paleta, el logo, las imágenes y el recorrido por secciones ya forman parte de la interfaz real; las rutas del prototipo siguen siendo un espacio de muestra.

## Evidence on Hand

README.md, front/src/pages, APIs frontend y backend, apartadoDIseñoGraficoBlocIA.md y specs. Hay cambios locales anteriores a esta tarea que se conservan. Los ejemplos de conversación y actividad del prototipo son sintéticos y se identifican como demostración.

## Product Principles

- Mantener las decisiones personales en manos del usuario.
- Hacer visible la clasificación y el modelo que responde.
- Conservar un espacio de lectura tranquilo.
- Distinguir demostraciones de actividad real.

## Open Decisions

La dirección editorial aplicada usa tinta, papel, ultramar y lima. El usuario autorizó incorporar este lenguaje visual a la aplicación funcional.
