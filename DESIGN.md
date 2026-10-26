---
name: "BloqIA — sistema editorial"
description: "Sistema visual compartido por la aplicación web de BloqIA y su prototipo navegable."
colors:
  ultramar: "#244ADA"
  idea: "#DAED9E"
  tinta: "#18252B"
  papel: "#F4F3EE"
  blanco: "#FFFFFF"
  canvas: "#FCFCF9"
  gris-landing: "#596267"
  gris-workspace: "#687176"
  linea-landing: "#D6D9D4"
  linea-workspace: "#DEDFDA"
  azul-hover-landing: "#193ABD"
  azul-hover-workspace: "#183DBF"
  campo-borde: "#CDD2CA"
  clasificacion-fondo: "#F0F3E9"
  clasificacion-texto: "#46533C"
  clasificacion-linea: "#DBE1D2"
  demo-fondo: "#EDF1E6"
  demo-texto: "#526049"
  demo-borde: "#D6DACE"
  peligro: "#A53530"
typography:
  display:
    fontFamily: "Manrope, sans-serif"
    fontSize: "clamp(52px, 5.35vw, 86px)"
    fontWeight: 500
    lineHeight: 1.11
    letterSpacing: "-.04em"
  headline:
    fontFamily: "Lora, Georgia, serif"
    fontSize: "clamp(31px, 3.3vw, 47px)"
    fontWeight: 500
    lineHeight: 1.18
    letterSpacing: "-.035em"
  title:
    fontFamily: "Manrope, sans-serif"
    fontSize: "16px"
    fontWeight: 650
    lineHeight: 1.4
  body:
    fontFamily: "Manrope, sans-serif"
    fontSize: "15px"
    lineHeight: 1.6
  body-workspace:
    fontFamily: "Manrope, sans-serif"
    fontSize: "14px"
    lineHeight: 1.6
  reading-example:
    fontFamily: "Lora, serif"
    fontSize: "14px"
    lineHeight: 1.8
  transcript:
    fontFamily: "Manrope, sans-serif"
    fontSize: "12px"
    lineHeight: 1.9
  label:
    fontFamily: "Manrope, sans-serif"
    fontSize: "10px"
    fontWeight: 650
    lineHeight: 1.6
rounded:
  marker: "2px"
  tag: "3px"
  badge: "4px"
  landing-action: "5px"
  field: "6px"
  workspace-surface: "7px"
  sidebar-action: "8px"
  composer: "9px"
  circle: "50%"
spacing:
  tight: "4px"
  compact: "8px"
  control: "12px"
  regular: "16px"
  group: "20px"
  section-inner: "24px"
  roomy: "28px"
  mobile-page: "23px"
components:
  button-landing-primary:
    backgroundColor: "{colors.ultramar}"
    textColor: "{colors.blanco}"
    rounded: "{rounded.landing-action}"
    padding: "17px 24px"
  button-landing-primary-hover:
    backgroundColor: "{colors.azul-hover-landing}"
  button-landing-light:
    backgroundColor: "{colors.papel}"
    textColor: "{colors.ultramar}"
    rounded: "{rounded.landing-action}"
    padding: "17px 24px"
  button-landing-light-hover:
    backgroundColor: "{colors.idea}"
  button-workspace-primary:
    backgroundColor: "{colors.ultramar}"
    textColor: "{colors.blanco}"
    rounded: "{rounded.workspace-surface}"
    padding: "11px 16px"
  button-workspace-primary-hover:
    backgroundColor: "{colors.azul-hover-workspace}"
  button-workspace-secondary:
    backgroundColor: "{colors.blanco}"
    textColor: "{colors.tinta}"
    rounded: "{rounded.workspace-surface}"
    padding: "11px 16px"
  button-new-chat:
    backgroundColor: "{colors.idea}"
    textColor: "{colors.tinta}"
    rounded: "{rounded.sidebar-action}"
    padding: "12px 11px"
  text-field:
    backgroundColor: "{colors.blanco}"
    textColor: "{colors.tinta}"
    rounded: "{rounded.field}"
    padding: "11px 12px"
    height: "42px"
  demo-badge:
    backgroundColor: "{colors.demo-fondo}"
    textColor: "{colors.demo-texto}"
    rounded: "{rounded.badge}"
    padding: "3px 7px"
  sidebar-nav:
    rounded: "{rounded.workspace-surface}"
    padding: "11px 12px"
  conversation-card:
    backgroundColor: "{colors.papel}"
    textColor: "{colors.tinta}"
    rounded: "{rounded.workspace-surface}"
  composer:
    backgroundColor: "{colors.blanco}"
    textColor: "{colors.tinta}"
    rounded: "{rounded.composer}"
    padding: "14px 15px 10px"
  classification:
    backgroundColor: "{colors.clasificacion-fondo}"
    textColor: "{colors.clasificacion-texto}"
    padding: "10px 12px"
---

# Design System: BloqIA — sistema editorial

## Overview

**Creative North Star: "Cuaderno editorial contemporáneo"**

El mockup combina papel, tinta, una retícula editorial y fotografías de materiales cotidianos. La interfaz deja aire alrededor de las preguntas y usa el ultramar para orientar la acción; la lima señala aperturas, estados y detalles puntuales. La voz conserva el trato de vos y acompaña el principio de que las decisiones personales pertenecen al usuario.

Este sistema se aplica a la portada, el acceso, el registro, el chat, el perfil, los proveedores y la actividad de la aplicación real, y también a la ruta independiente del prototipo. Se conservaron las APIs y los flujos de cuenta y conversación existentes; la portada incluye ejemplos editoriales y las páginas interiores muestran datos reales. El prototipo `/mockup` mantiene estados y respuestas simulados para revisión visual. Los archivos en `front/src/mockup/` y `front/public/mockup/` aportan marca, fuentes y recursos gráficos compartidos.

**Key Characteristics:**

- Papel claro, tinta grafito y acentos de ultramar y lima.
- Manrope para orientación; Lora para titulares del espacio personal y pasajes editoriales.
- Filas y divisores finos, superficies suaves y profundidad contenida.
- Logo de bloques e imágenes físicas que relacionan pensar con construir.
- Movimiento de lectura acotado, navegación explícita y datos de demostración visibles.

## Colors

La paleta se apoya en neutrales de papel y tinta; los colores de acción y de estado son intervenciones concretas.

### Primary

- **Ultramar:** logo, acciones principales, enlaces, foco y palabras destacadas. Sus dos variantes de hover pertenecen a landing y workspace, respectivamente.
- **Tinta:** texto de mayor jerarquía, panel del método, relato de acceso y navegación lateral.

### Secondary

- **Idea:** nueva conversación en el lateral, selección de texto, marcas de avance, flecha de exploración y énfasis sobre tinta. No es el color de todos los botones.

### Neutral

- **Papel / blanco / canvas:** fondo público, campos y superficies interiores del espacio de trabajo.
- **Gris landing / gris workspace:** texto secundario. Son dos valores reales de ámbitos distintos; no se unifican retrospectivamente.
- **Línea landing / línea workspace / campo borde:** divisores, contornos de las vistas y campos.
- **Clasificación fondo, texto y línea:** agrupación expandible de metadatos de una respuesta.
- **Demo fondo, texto y borde:** identificación explícita de datos de ejemplo.
- **Peligro:** acción de eliminación o desconexión. Los mensajes de error usan además tintes cálidos específicos en la fuente.

**The Action Rule.** El ultramar identifica acciones y foco; la lima funciona como acento de contexto y como contraste sobre tinta.

## Typography

**Display Font:** Manrope, con sans-serif como respaldo.
**Body Font:** Manrope para interfaz y respuestas; Lora, con Georgia/serif como respaldo en el workspace, para titulares y pasajes editoriales.

Manrope se sirve desde `/mockup/fonts/Manrope.ttf` con pesos variables (200–800). Lora se sirve desde `Lora.ttf` y `Lora-Italic.ttf`, con pesos (400–700). Las tres fuentes son locales y sus licencias OFL acompañan los archivos. La cursiva de Lora en palabras como “pregunta” o “criterio” utiliza la fuente italic real.

### Hierarchy

- **Display:** titular público amplio, con espaciado cerrado y ajuste fluido. Los títulos de sección públicos usan Manrope (500), un tamaño fluido entre (32px) y (46px) y altura de línea (1.25).
- **Headline:** títulos de páginas personales en Lora. La bienvenida del chat crece entre (37px) y (52px); el relato de acceso entre (39px) y (64px).
- **Title:** nombres de secciones interiores en Manrope semibold; jerarquías menores se sitúan en (14px).
- **Body:** base pública y base del workspace distintas. El párrafo principal de landing usa (16px) y altura de línea (1.85).
- **Reading example:** Lora en el ejemplo de conversación y en capítulos del método. Los capítulos usan (31px), peso (400) y altura de línea (1.4).
- **Transcript:** respuestas y consultas del chat usan Manrope, con máximo de (72ch). Markdown conserva títulos, listas, enlaces, citas, código y tablas con desplazamiento horizontal.
- **Label:** etiquetas compactas de formularios. Los metadatos actuales incluyen tamaños de (8–11px); esa densidad observada no establece una norma de lectura para futuras pantallas.

**The Two Voices Rule.** Manrope organiza la interfaz y el transcript; Lora introduce pausa editorial en los titulares y ejemplos donde ya se utiliza.

## Layout

La landing alterna bloques amplios y secciones de dos columnas; la retícula pública utiliza márgenes fluidos de `max(30px, 6.6vw)`. El hero tiene una proporción (1.08:1) y el workspace una columna lateral de (240px) junto a un lienzo flexible. El contenido interior usa un máximo de (1150px), mientras transcript y compositor se limitan a (790px). El formulario de acceso se limita a (420px).

La navegación pública mide (96px) en escritorio. A (800px) pasa a menú expandible; a (600px) las composiciones se apilan y los bloques principales adoptan relleno de (68px 24px). El método pierde su posición fija en móvil y muestra todos los capítulos con opacidad completa. Por encima de (1600px), la landing se contiene en (1800px).

En el workspace, a (1100px) el lateral baja a (216px) y se reducen márgenes; a (850px) perfil y cuenta se apilan. A (700px) aparece una barra móvil de (58px), el lateral se convierte en un panel de (250px) con fondo de cierre y la barra interior mide (49px). Actividad pasa de tres columnas a filas; las probabilidades se apilan y el transcript pierde su sangría. El compositor conserva su lugar debajo del área que desplaza los mensajes. Las vistas de acceso apilan relato y formulario. Una adaptación adicional contempla escritorio de altura menor a (740px).

El desplazamiento público usa progreso superior de (3px), capítulos observados por intersección y una conversación fija con `top: 90px`. La foto inicial admite un desplazamiento máximo de (32px), calculado desde el scroll mediante un listener pasivo y un frame de animación; el contenido sigue el desplazamiento nativo. Los indicadores de paso permiten cambiar el ejemplo manualmente.

**The Reading Rule.** El movimiento acompaña la posición de lectura y mantiene los controles operables; con `prefers-reduced-motion` se desactivan animaciones, transiciones, parallax y desplazamiento suave.

**Continuidad entre secciones.** Los enlaces internos cambian de vista sin recargar el documento. Las rutas utilizan un fundido nativo de 160ms con la curva compartida `cubic-bezier(.23, 1, .32, 1)`; los navegadores sin esa función reciben un fundido de entrada mediante Web Animations. La navegación rápida cancela la transición anterior y conserva el último destino solicitado. El encabezado de la vista recibe el foco al llegar. Atrás/Adelante y enlaces modificados conservan su función. Las preguntas frecuentes abren y cierran con altura medida y opacidad durante 200ms, retomando el estado visible si se invierte la acción; los ejemplos del recorrido cambian con un fundido breve. La navegación con teclado y la preferencia de movimiento reducido actualizan el contenido inmediatamente. Los saltos a secciones de la portada conservan el desplazamiento nativo y un margen de lectura de 24px.

**Interacciones físicas.** Las acciones discretas responden al presionar con una escala de 0.97 durante 120ms; la navegación frecuente conserva su posición. El panel compartido de modelos, clasificación, información, proveedores y menú permite arrastrar desde el tirador. Sigue el puntero, resiste en el límite superior y proyecta la velocidad al soltar para decidir entre volver o cerrar. El resorte usa respuesta de 0.3s y amortiguación de 1, o de 0.8 cuando recibe velocidad del gesto; el desplazamiento puede interrumpirse. Apertura y cierre recorren el mismo eje. Con movimiento reducido, el panel cambia de estado directamente y los botones conservan su tamaño. Escape, fondo y botón de cierre siguen disponibles; al cerrar se restaura el foco y el desplazamiento de la página. El contenido del panel desplaza independientemente del encabezado. El selector móvil no enfoca la búsqueda automáticamente y los campos de contraseña ofrecen mostrar/ocultar también en escritorio.

## Elevation & Depth

La profundidad surge principalmente del cambio de papel a tinta, del contraste de superficie y de divisores de un píxel. Las fotografías aportan sombras físicas. La interfaz emplea dos sombras tenues: el adelanto del workspace en la landing y el compositor, cuyo contorno conserva la estructura aun sin sombra.

### Shadow Vocabulary

- **Workspace preview:** `0 24px 45px -26px #18252B30`; separa el adelanto interior del fondo público.
- **Composer:** `0 6px 16px -10px #18252b1a`; sostiene el campo de escritura sin levantar todas las superficies.

**The Quiet Depth Rule.** Las filas de historial, catálogo, actividad y preguntas frecuentes se distinguen con divisores; las sombras se reservan para las dos superficies que ya las usan.

## Shapes

La geometría es rectangular, con esquinas discretas. Botones públicos, campos y superficies del workspace tienen radios diferentes registrados en el frontmatter. Avatares, puntos de estado y la flecha sobre la fotografía usan círculos. El panel de clasificación es una franja de bordes superior e inferior, sin adoptar una tarjeta redondeada.

El logo original del mockup se dibuja en código SVG: cuatro bloques rectangulares y dos aperturas componen una B abstracta. `Brand` usa un símbolo de (40×40) con `currentColor`; el archivo descargable `/mockup/logo.svg` utiliza ultramar. La marca textual “bloqia.” es Manrope, con “bloq” en (800), “ia” en (500), tracking (-.04em) y punto en tinta o lima según el fondo. El símbolo compacto es la versión usada en espacios limitados.

## Components

### Buttons

Acciones rectangulares, claras y de peso medio. Los botones públicos usan el radio landing y un espacio mayor entre texto y flecha; al hover oscurecen el azul y suben (2px). La variante clara del cierre usa papel sobre azul y cambia a lima. Las acciones interiores son más compactas, con transición de fondo y borde (150ms). Nueva conversación usa lima sobre tinta; sus estados hover y disabled están definidos. En foco, la landing muestra un contorno de (3px) con offset (5px), y el workspace uno de (3px) con offset (4px). El foco sobre navegación oscura es lima.

### Chips

Las marcas “Demo”, “Datos de ejemplo”, “Ejemplo” y los tags de catálogo son pequeños contornos o fondos suaves, con radios de (3–4px). Su propósito es distinguir procedencia o capacidad, y acompañan texto legible; no se depende únicamente del color para comunicar el estado.

### Cards / Containers

La conversación del método reúne encabezado, pregunta, clasificación, respuesta y pie dentro de una superficie de papel. El workspace evita encerrar cada fila en una tarjeta: historial, proveedores y actividad comparten divisores. El bloque de Qwen local es una superficie de tono verdoso con borde y radio de (7px). Los estados de error y confirmación inline usan tonos cálidos y acciones textuales.

### Inputs / Fields

Campos blancos con contorno suave, radio de campo y altura observada en el frontmatter. Las etiquetas permanecen fuera del placeholder. El foco cambia a un contorno azul de (2px) con offset (2px). Contraseña tiene control explícito para mostrar u ocultar; edad y profesión conservan sus controles nativos. Error y aviso muestran texto y `role="alert"` o `role="status"`. Los controles deshabilitados reducen la opacidad y cambian el cursor.

### Navigation

La cabecera pública ofrece enlaces a secciones, acceso y registro. El menú móvil presenta un control con `aria-expanded`. El lateral interior agrupa conversación, historial, perfil, proveedores y actividad; la vista activa usa `aria-current="page"`, fondo tinta más claro y texto blanco. En móvil, un botón y un fondo de cierre controlan el lateral. Los iconos se dibujan como SVG de trazo (1.6), con terminaciones redondeadas y nombres accesibles en controles sin texto.

El prototipo se carga de forma diferida al entrar a `/mockup`. La aplicación real utiliza la misma paleta y marca en sus rutas funcionales y presenta la actividad a través de su propia página.

Las rutas reales incluyen `/`, `/login`, `/register`, `/auth/google/callback`, `/nuevo-chat`, `/perfil`, `/perfil-tecnico` y `/actividad`. El prototipo se abre en `/mockup` o `/mockup.html`; sus hashes interiores son `#/chat`, `#/history`, `#/profile`, `#/providers`, `#/usage`, `#/login`, `#/register` y `#/google`.

### Composer and classification

El compositor combina consulta, selector de modelo y envío dentro de un contorno suave; el estado `focus-within` aclara el borde azul. La longitud máxima es (4000) caracteres, Enter envía y Shift + Enter crea un salto. Los ejemplos rellenan el campo. Las fases de clasificación y respuesta de demostración deshabilitan el envío y los cambios de conversación.

La clasificación del chat real es un `details` expandible con categoría, confianza, aceptación y revisión humana. El prototipo añade estados simulados para permitir explorar variaciones sin llamar a los servicios.

### Imagery and provenance

`thinking-desk.png` es una fotografía editorial horizontal (1536×1024) de manos, cuaderno y bloques azules; `quiet-study.png` es una escena de estudio vertical (1024×1536) con silla azul y luz diagonal. Ambas fueron generadas con la herramienta integrada `image_gen.imagegen` el 5 de octubre de 2026. Cada imagen conserva su prompt, origen y revisión visual en su JSON contiguo, además del prompt en metadata del PNG y en un archivo `.prompt.txt` contiguo. El hero carga primero; la segunda imagen utiliza carga diferida y ambas tienen descripción alternativa.

La ruta `/mockup` funciona con datos sintéticos y respuestas preparadas; sus formularios no crean cuentas ni guardan claves. La aplicación normal conserva los servicios reales de cuenta, conversación, perfil, proveedores y actividad. Las ilustraciones de conversaciones en la portada se identifican como ejemplos y sus acciones llevan a las funciones reales.

## Do's and Don'ts

### Do:

- **Do** conservar los ámbitos de tokens de landing y workspace al extender la aplicación y el prototipo.
- **Do** usar las fuentes locales, incluida Lora Italic para la cursiva editorial.
- **Do** mantener divisores, aire y ancho de lectura en conversación, historial y catálogo.
- **Do** acompañar categorías, estado y procedencia de demostración con texto.
- **Do** respetar reduced-motion y ofrecer los mismos controles en móvil y teclado.

### Don't:

- **Don't** presentar esta propuesta como identidad aprobada o reemplazo de las páginas originales.
- **Don't** convertir los metadatos de 8–10px observados en un tamaño universal para lectura.
- **Don't** extender el parallax o las animaciones de lectura a formularios o composición de mensajes.
- **Don't** representar datos de ejemplo, credenciales descartadas o respuestas preescritas como actividad real.
