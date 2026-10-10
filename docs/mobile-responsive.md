# Interfaz móvil del sistema

El diseño del mockup se aplicó al frontend real en anchos de hasta 767 px. La aplicación mantiene la navegación lateral y los controles de escritorio en pantallas mayores.

- Portada pública con menú táctil, etapas del método y acceso fijo al chat.
- Barra inferior Inicio / Chats / Cuenta en las pantallas autenticadas.
- Historial con búsqueda, fecha de actualización y panel de confirmación para eliminar. La vista del historial se conserva al recargar.
- Selector de modelos, clasificación y configuración de proveedores en paneles inferiores con foco contenido, cierre con Escape y recuperación del foco.
- Perfil, actividad y formularios de acceso adaptados a una columna. Contraseña visible u oculta mediante un botón.
- Chat con altura dinámica, áreas seguras del dispositivo y ajuste al espacio disponible cuando aparece el teclado.
- Se conservan las API, el guardado de conversaciones, las cuotas, la confirmación de consultas personales, las verificaciones de correo y los bloqueos del sistema.

## Validación

Desde `front`, `npm test` ejecuta las pruebas de integración. `npx playwright test --config playwright.mobile.config.ts` ejecuta los recorridos responsive en Edge local con las API simuladas, sin cuentas ni consumo de modelos reales. La prueba también funciona con la configuración general de Playwright y su navegador instalado.

Los recorridos cubren 320 y 390 px, escritorio a 1440 px, acceso desde la portada, contraseña, envío, modelos, clasificación, búsqueda, recarga y eliminación confirmada, cuenta, perfil, proveedores, actividad, confirmación y cancelación personal, bloqueo y reducción del viewport por teclado. Son comprobaciones en navegador; no sustituyen pruebas en teléfonos físicos.

El prototipo HTML independiente continúa en `docs/mockups/bloqia-mobile.html` como referencia de diseño.
