# BloqIA — validación del mockup

Estado de verificación original del 5 de octubre de 2026. Ese registro describe el primer prototipo en `/mockup` y la versión de la aplicación anterior a la implementación posterior.

## Implementación posterior en la aplicación

Después de este estado de verificación, el usuario pidió llevar el diseño del prototipo a la aplicación actual. La portada real reutiliza su composición por secciones, imágenes y recorrido de lectura; acceso, registro y callback de Google comparten la identidad editorial; el marco de navegación presenta chat, historial, perfil, proveedores y actividad. Los datos de chat, perfil, claves y actividad siguen usando las APIs de la aplicación. La ruta `/mockup` conserva los ejemplos y respuestas simulados. La compilación de la aplicación pasó después de estos cambios; no se volvió a ejecutar la suite de pruebas en esa tanda.

## Resultado disponible

| Verificación | Resultado |
|---|---|
| Compilación de TypeScript y Vite | Correcta: `tsc + vite` completados |
| Suite Vitest existente | Resultado recibido: `12 passed / 3 failed`; los tres fallos corresponden a las discordancias preexistentes detalladas abajo |
| Pruebas de navegador del mockup | Correctas: ocho grupos de pruebas de interacción, todos los apartados a 390 px, scroll por capítulos y ausencia de solicitudes reales a APIs |
| Sintaxis de `NuevoChat.tsx` | Parser de TypeScript sin diagnósticos de sintaxis; no se modificó la fuente |

La compilación y el resultado de Vitest fueron ejecutados y comunicados por el agente coordinador. La comprobación siguiente fue independiente, de sólo lectura, sin repetir las pruebas ni cambiar sus expectativas.

## Tres fallos preexistentes de la suite

| Prueba | Expectativa del test | Código actual | Hallazgo |
|---|---|---|---|
| `front/tests/integration/register.test.tsx:8` | Texto que coincida con `/Minimo 10 caracteres/` | `front/src/pages/Register.tsx:8` usa «Mínimo 10 caracteres, una letra, un número y un símbolo» | La búsqueda distingue la letra acentuada; el test espera una variante sin tilde |
| `front/tests/integration/inicio.test.tsx:15` | Región llamada «Un espacio simple, a tu manera.» | `front/src/pages/Inicio.tsx:9` usa «Inicio público» o «Inicio personal», según sesión | El nombre accesible esperado no coincide con la pantalla existente |
| `front/tests/integration/perfil_tecnico.test.tsx:24` | Enlace «Solicitar acceso privado» a la solicitud de cliente privado de OpenAI | `front/src/pages/PerfilTecnico.tsx` no contiene ese enlace; muestra consola de claves y condiciones/cupos de cada proveedor | El test espera contenido que la pantalla actual no ofrece |

Las seis fuentes implicadas coinciden con `HEAD` (`3919f237ffdb14dbe812da3c61db8efcdbbeb696`). Se verificó tanto la ausencia de diferencias con Git como la igualdad de los identificadores de contenido del archivo de trabajo y de `HEAD`.

| Archivo | Contenido idéntico a HEAD |
|---|---|
| `front/src/pages/Register.tsx` | Sí |
| `front/src/pages/Inicio.tsx` | Sí |
| `front/src/pages/PerfilTecnico.tsx` | Sí |
| `front/tests/integration/register.test.tsx` | Sí |
| `front/tests/integration/inicio.test.tsx` | Sí |
| `front/tests/integration/perfil_tecnico.test.tsx` | Sí |

Las incompatibilidades entre estas expectativas y las pantallas ya están presentes en el estado versionado anterior al mockup. No se corrigieron los tests ni las pantallas para ocultar o reinterpretar esos fallos. La compilación correcta confirma que el conjunto compila; no convierte la suite existente en una suite completamente aprobada.

## Alcance de la revisión

El prototipo utiliza datos demostrativos y debe comprobarse por separado en escritorio y móvil, incluyendo navegación, formularios simulados, clasificación, gestión visual de proveedores, panel de uso y reducción de movimiento. El resultado se conserva en `.impeccable/review/verification.json` junto con capturas de escritorio, móvil y ancho de 1000 px. La revisión visual independiente se informa por separado.

## Cierre de revisión visual

La revisión independiente inicial identificó dos defectos materiales (espacios del titular móvil y desplazamiento heredado entre apartados) y una corrección de registro del proceso. Los tres fueron corregidos. El veredicto posterior fue `ship` al alcance de esas tres correcciones, con cinco recapturas válidas; no se presenta como aprobación humana.

La verificación final `review-fixes.json` confirma espacios, encabezados/métricas visibles, navegación volver/avanzar y ambas entradas (`/mockup` y `/mockup.html`). Compilación final completada después de las correcciones. Las pruebas antiguas conservaron los tres fallos documentados, ajenos a esta incorporación.

## Abrir la propuesta

Vista previa local: http://127.0.0.1:4175/mockup.html. Cuando se inicia el frontend habitual en el puerto 5173, también se puede abrir `/mockup` o `/mockup.html`. El mockup está separado de la sesión real y todos sus datos son de demostración.
