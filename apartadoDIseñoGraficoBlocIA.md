# BloqIA — Sistema visual

Reglas de forma, color, radio y disposición. Documento normativo: si algo no está
acá, no se usa.

---

## 1. Concepto de forma

El nombre manda la geometría: **bloque**. La interfaz está construida con
rectángulos macizos que se encastran sin separación, no con tarjetas flotantes.
La referencia no es una app de chat, es un **instrumento de medición**: un
contador de consumo, una ficha de control, un tablero con lecturas siempre
visibles. El producto existe para que el usuario vea cuánto está gastando, así
que la medición no se esconde en un menú.

Tres decisiones de forma que definen todo lo demás:

1. **El chasis es oscuro y rígido; la lectura es clara y acotada.** La columna
   de conversación es una inserción de papel dentro de una estructura de
   grafito. Nunca al revés, y nunca fondo crema a sangre completa.
2. **La máquina no imita a la persona.** Los mensajes del usuario son bloques
   rellenos con esquinas suavizadas. Las respuestas de BloqIA no tienen relleno
   ni radio: son texto corrido con una barra vertical de 3 px a la izquierda que
   lleva el color de estado. La IA se lee como un registro impreso, no como un
   interlocutor.
3. **El medidor vive en el borde de la pantalla,** no en una tarjeta. Es una
   franja vertical de 10 px pegada al canto derecho del viewport, que se llena
   desde abajo. Es el único elemento ambiental del sistema y es donde se gasta
   toda la audacia visual. Todo lo demás se mantiene callado.

### Formas permitidas

| Forma | Uso | Medidas |
|---|---|---|
| Rectángulo macizo | Paneles, chasis, superficies | radio según §4 |
| Filete de 1 px | Separación entre regiones | `#17212B` al 12 % |
| Barra vertical 3 px | Marca de autoría de BloqIA en cada respuesta | altura del bloque de texto |
| Franja vertical 10 px | Medidor de tiempo en el canto derecho | alto completo del viewport |
| Cuadrado 14 × 14 | Pip del contador de preguntas personales | radio 2 px, gap 6 px |
| Corte diagonal 45° de 16 px | Esquina inferior derecha de un ítem bloqueado | solo en historial y pantalla de bloqueo |
| Círculo | Únicamente avatar (32 px) y punto de sesión activa (8 px) | nada más |

Cualquier otra forma queda fuera. No hay excepciones por «un solo lugar».

---

## 2. Reparto de la paleta

Cada color tiene **un** trabajo. Un color de estado nunca decora, y un color de
marca nunca comunica estado. Esta separación es lo que hace que el bloqueo se
entienda sin leer.

| Hex | Nombre interno | Función exclusiva |
|---|---|---|
| `#17212B` | Grafito | Chasis: riel lateral, pantalla de bloqueo, pie. Texto principal sobre superficies claras. Filetes (al 12 %). |
| `#FFF6DB` | Papel | Superficie de lectura: la columna de conversación y el historial. Texto sobre grafito. |
| `#FFFFFF` | Blanco | Superficies elevadas sobre papel: compositor, campos, diálogos, panel de estado. Texto sobre azul y sobre grafito. |
| `#1C489B` | Azul BloqIA | Marca y acción primaria. Un solo botón azul por pantalla. Enlaces y anillo de foco. **Nunca** como estado ni como fondo de sección. |
| `#3F8585` | Verde académico | Estado seguro: consulta clasificada como académica o profesional, cuota disponible, tramo 0–60 % del medidor, pip 1. |
| `#E98973` | Salmón | Estado de atención: tramo 60–90 % del medidor, pip 2, avisos de cuota, segunda pregunta personal. Solo como relleno o indicador. |
| `#D95C5C` | Rojo límite | Bloqueo consumado, error, 3/3, tramo 90–100 %, pip 3, cuenta regresiva de 24 h. |
| `#66727A` | Gris dato | Metadatos, horarios, estados deshabilitados, riel vacío del medidor, bordes de campos en reposo. |

### Salvedad importante sobre el salmón

`#E98973` está a un paso del terracota que aparece en prácticamente toda
interfaz generada por IA. Para que no se lea como esa muletilla: **no es el
acento de marca, no va en botones, no va en titulares, no va en fondos de
sección.** Aparece solo como estado intermedio, en superficies chicas
(medidor, pip, borde de aviso). Si se lo saca de la escala de estado, el sistema
pierde su significado y gana un tic.

### Verde → amarillo → rojo sin amarillo

El documento original describía una escala verde / amarillo / rojo. La paleta no
tiene amarillo y no se agrega uno. La escala real es **verde académico → salmón
→ rojo límite**, en tres saltos discretos, sin degradado intermedio. El corte
brusco entre tramos es información: avisa que algo cambió de categoría, cosa que
un degradado disimula.

### Contrastes verificados (no improvisar)

| Combinación | Ratio | Regla |
|---|---|---|
| Grafito sobre papel | 15,2:1 | Texto de cualquier tamaño |
| Azul sobre papel | 7,9:1 | Texto de cualquier tamaño |
| Gris dato sobre papel | 4,5:1 | Solo ≥ 14 px, nunca en peso ligero |
| Verde sobre papel | 4,0:1 | No apto para texto chico. Relleno, borde o texto ≥ 24 px |
| Blanco sobre verde | 4,3:1 | Solo ≥ 19 px en seminegra |
| Rojo sobre papel | 3,4:1 | Nunca como texto. Solo relleno |
| Grafito sobre rojo | 4,4:1 | Texto ≥ 16 px en seminegra |
| Grafito sobre salmón | 6,5:1 | Texto de cualquier tamaño |
| Blanco sobre azul | 8,6:1 | Texto de cualquier tamaño |
| Blanco sobre grafito | 16,3:1 | Texto de cualquier tamaño |

Consecuencia práctica: **el texto sobre rojo y sobre salmón siempre es grafito,
nunca blanco.**

### Derivados admitidos

Solo opacidades de colores de la paleta, nunca tonos nuevos:

- `#17212B` 12 % → filetes y bordes de tabla
- `#17212B` 6 % → fondo de bloque de código dentro de una respuesta
- `#66727A` 24 % → riel vacío del medidor
- `#1C489B` 8 % → fondo de la burbuja del usuario
- `#D95C5C` 10 % → fondo de banda de error

---

## 3. Tipografía

Dos familias, con roles claramente distintos.

- **Archivo** (Omnibus-Type): interfaz, titulares, cifras. Tiene cifras
  tabulares, que es lo que hace legible una cuenta regresiva que cambia cada
  segundo. Los números del contador y del temporizador van siempre en
  `font-variant-numeric: tabular-nums`.
- **Source Serif 4**: cuerpo de las respuestas de BloqIA. La serif marca que
  eso es una explicación para leer, no un mensaje para consumir. Interlínea
  1,6; ancho de línea máximo 72 caracteres.

Escala (base 16, razón 1,25):

| Rol | Tamaño / interlínea | Familia y peso |
|---|---|---|
| Cuenta regresiva de bloqueo | 76 / 0,95 | Archivo 600 |
| Título de pantalla | 31 / 1,15 | Archivo 600 |
| Subtítulo | 25 / 1,25 | Archivo 500 |
| Respuesta de BloqIA | 17 / 1,6 | Source Serif 4 400 |
| Mensaje del usuario | 16 / 1,5 | Archivo 400 |
| Interfaz y botones | 15 / 1,4 | Archivo 500 |
| Metadato | 13 / 1,35 | Archivo 400, gris dato |

Prohibido: versalitas rastreadas como etiqueta encima de cada bloque,
monoespaciada para rótulos chicos, resaltar una sola palabra del titular en otro
color, y cadenas de metadatos unidas con puntos medios.

---

## 4. Radios

El radio codifica jerarquía: **cuanto más estructural, más recto**. Un radio
único para todo es el tic más reconocible de una interfaz generada.

| Valor | Dónde |
|---|---|
| **0 px** | Riel lateral, cabecera, columna de lectura, panel de estado, medidor de borde, barra de autoría, pantalla de bloqueo, cajón lateral |
| **2 px** | Pips del contador, etiquetas de clasificación, segmentos del medidor |
| **4 px** | Botones, campos, chips de profesión, diálogos, avisos |
| **6 px** | Burbuja del mensaje del usuario, con la esquina inferior derecha en 0 px para anclarla a su lado |
| **Píldora (999 px)** | No se usa. Ni en botones ni en chips ni en etiquetas |

Las respuestas de BloqIA no llevan radio porque no llevan caja.

### Sombras

Una sola sombra en todo el sistema, y solo en diálogos modales y en la tarjeta
de bloqueo:

```
box-shadow: 6px 6px 0 #17212B;
```

Desplazamiento duro, sin difuminado, sin transparencia. Queda **prohibida**
cualquier sombra difusa del tipo `0 4px 12px rgba(0,0,0,.1)` en tarjetas, barras
o botones.

---

## 5. Retícula y espaciado

Base de 8 px con medio paso de 4 px. Valores admitidos: 4, 8, 12, 16, 24, 32,
48, 64, 96. Nada intermedio.

Las regiones se tocan: entre el riel y la columna de lectura hay un filete de
1 px, no un margen. La separación en esta interfaz se hace con línea y con
cambio de superficie, no con aire.

---

## 6. Ubicación de las ventanas

### 6.1 Pantalla de conversación — escritorio ≥ 1280 px

```
┌────┬──────────────────────────────────────────┬──────────────┬──┐
│    │ cabecera 56 px                           │              │▓▓│
│    │ Diseño gráfico · UTN        ▪ ▪ ▫        │  ESTADO      │▓▓│
│ 76 ├──────────────────────────────────────────┤  300 px      │▓▓│
│ px │                                          │              │▓▓│
│    │        columna de lectura                │  1 h 42      │▓▓│
│riel│        680 px, centrada                  │  de 3 h      │░░│
│    │                                          │              │░░│
│    │                                          │  2 de 3      │░░│
│    │                                          │  personales  │░░│
│    ├──────────────────────────────────────────┤              │░░│
│    │ compositor 64 px                         │              │░░│
└────┴──────────────────────────────────────────┴──────────────┴──┘
  0                                                            10px
```

- **Riel izquierdo.** 76 px fijos, `x: 0`, alto completo, fondo grafito, radio 0.
  Contiene la marca arriba (24 px desde el borde superior), tres destinos
  —conversación, historial, perfil— y el avatar abajo. Íconos de trazo 1,5 px
  con remates rectos, retícula de 20 px. El destino activo se marca con una
  barra de 3 px en azul pegada al canto izquierdo, no con un fondo redondeado.
- **Columna de lectura.** 680 px de ancho máximo, centrada en el espacio libre
  entre riel y panel, fondo papel, radio 0, filete de 1 px a cada lado. El
  contenido arranca a 32 px de la cabecera.
- **Cabecera.** 56 px de alto, fondo papel, filete inferior. A la izquierda la
  profesión declarada como chip (radio 4 px, borde 1 px gris dato). A la derecha
  los tres pips del contador, a 24 px del borde.
- **Compositor.** Fijo al pie de la columna, alto mínimo 64 px, crece hasta
  160 px, fondo blanco, radio 4 px, borde 1 px gris dato, y en foco borde 2 px
  azul. El botón de envío es cuadrado de 36 px, radio 4, azul macizo.
- **Panel de estado.** 300 px, anclado a la derecha con 10 px de reserva para el
  medidor, fondo blanco, radio 0, filete izquierdo. Siempre visible: tiempo
  consumido en cifras grandes, cuota de preguntas personales, y clasificación de
  la última consulta. No es un desplegable ni un menú; es la razón de ser del
  producto.
- **Medidor de tiempo.** 10 px de ancho, `position: fixed; right: 0; top: 0;
  height: 100vh`. Riel vacío en gris dato al 24 %. Se llena desde abajo: hasta el
  60 % en verde, de 60 a 90 % en salmón, de 90 a 100 % en rojo. Sin degradado ni
  animación continua; la transición entre tramos dura 200 ms y ocurre una sola
  vez por tramo.

### 6.2 Adaptaciones

| Ancho | Cambio |
|---|---|
| 1024–1279 | El panel de estado colapsa a 220 px y muestra solo cifras. La columna baja a 620 px. |
| 768–1023 | El panel de estado desaparece; sus datos pasan a la cabecera, que crece a 72 px. |
| ≤ 767 | El riel pasa a barra inferior de 56 px con `padding-bottom: env(safe-area-inset-bottom)`. El medidor pasa a franja horizontal de 4 px fija en el borde superior, debajo de la barra de estado del sistema. La columna ocupa el ancho completo con 16 px de margen. |

### 6.3 Diálogos

- **Ancho:** 440 px. Máximo 90 vw.
- **Posición:** centrado horizontalmente; verticalmente al 20 % del alto del
  viewport, no al 50 %. El centrado óptico queda más arriba que el matemático.
- **Radio:** 4 px. **Sombra:** el desplazamiento duro de §4.
- **Fondo de página:** grafito al 40 %, sin desenfoque.
- **Botones:** alineados a la derecha, 16 px entre ellos, la acción primaria
  última. Un solo botón azul.

### 6.4 Avisos de cuota

320 px de ancho, anclados a 16 px del borde superior y a 26 px del derecho
(despejando el medidor). Radio 4 px, fondo blanco, borde izquierdo de 3 px en el
color del estado que informan. Permanecen 6 segundos y se descartan con clic.
Nunca se apilan: un aviso reemplaza al anterior.

### 6.5 Cajón de perfil

360 px, entra desde la derecha, alto completo, radio 0, fondo blanco, filete
izquierdo. Entra con un desplazamiento de 180 ms; no se desvanece.

### 6.6 Pantalla de bloqueo

No es una ventana modal: es una ruta propia que reemplaza la conversación. El
producto retira la superficie de lectura, y esa ausencia es el mensaje.

```
┌────────────────────────────────────────────────┐
│                                                │
│                                                │
│      BloqIA está cerrada                       │  31 px, papel
│                                                │
│      17:42:08                                  │  76 px, tabular, papel
│      Vuelve a abrirse mañana a las 09:14       │  15 px, gris dato
│                                                │
│      ▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬             │  10 px, rojo límite
│                                                │
│      Se alcanzó el límite de 3 consultas       │  17 px, papel
│      personales del día.                       │
│                                                │
│      [ Ver historial ]                         │  botón fantasma
│                                                │
└────────────────────────────────────────────────┘
```

Fondo grafito a sangre completa. Bloque de contenido alineado a la izquierda,
ancho 520 px, ubicado al 28 % del alto. Sin ilustración, sin ícono de candado,
sin mascota. El único botón es fantasma: borde 1 px papel, fondo transparente,
radio 4 px. No hay acción para desbloquear, porque no existe.

---

## 7. Contador de preguntas personales

Tres cuadrados de 14 × 14 px, radio 2 px, separados 6 px, en la cabecera.

| Estado | Aspecto |
|---|---|
| Disponible | Borde 1,5 px gris dato, relleno transparente |
| Primera consumida | Relleno verde académico |
| Segunda consumida | Relleno salmón |
| Tercera consumida | Relleno rojo límite, y la interfaz pasa a la pantalla de bloqueo |

El cambio se produce con un relleno instantáneo, sin animación de pulso ni de
escala. Lo que se gastó, se gastó.

---

## 8. Clasificación visible de la consulta

Cada respuesta de BloqIA lleva su barra de autoría de 3 px coloreada según la
clasificación: verde para académica o profesional, salmón para personal dentro
de cuota, rojo para la que produjo el bloqueo. Debajo del texto, un metadato de
13 px en gris dato indica la categoría en lenguaje llano: «Clasificada como
consulta personal. Quedan 2 hoy.» Sin etiqueta en mayúsculas, sin ícono.

---

## 9. Movimiento

- Transiciones de estado: 200 ms, `cubic-bezier(.2,0,0,1)`.
- Entrada del cajón y de diálogos: 180 ms de desplazamiento.
- Aparición de una respuesta: el texto se revela progresivamente mientras
  llega; nada más.
- `prefers-reduced-motion: reduce` anula todo excepto el cambio de color.

Prohibido: entradas de desvanecimiento y subida en cada sección, elevación al
pasar el cursor sobre tarjetas, pulsos en indicadores, rotación de íconos,
animaciones decorativas de fondo.

---

## 10. Lista de prohibiciones

Estas son las marcas reconocibles de una interfaz generada automáticamente.
Ninguna entra en BloqIA.

**Forma y superficie**
- Vidrio esmerilado, desenfoque de fondo, transparencias apiladas.
- Tarjetas idénticas con radio 16–24 px, sombra gris difusa y un ícono arriba.
- Degradados como decoración, en fondos, en textos o en bordes.
- Formas orgánicas, manchas, ondas, blobs, gotas.
- Cuadrículas de puntos, mallas y patrones geométricos de fondo.
- Bordes brillantes, resplandores, neón.
- Botones píldora con una flecha «→» al final del texto.

**Color**
- Violeta e índigo en cualquier proporción.
- Verde ácido sobre negro.
- Negro teñido (`#0B0B0B`, `#111`) en lugar del grafito de la paleta.
- Crema a sangre completa como fondo de página.
- Salmón usado como acento de marca.

**Tipografía y rótulos**
- Antetítulos en mayúsculas con interletrado abierto.
- Monoespaciada para etiquetas de dato.
- Numeración 01 / 02 / 03 en contenido que no es una secuencia.
- Metadatos unidos con puntos medios.
- Una palabra del titular resaltada en otro color.

**Iconografía e ilustración**
- Destellos, chispas o estrellitas como símbolo de IA.
- Robot, cerebro, bombilla, candado con cara.
- Ilustraciones isométricas, personajes planos genéricos, renders 3D.
- Emoji dentro de la interfaz.
- Burbuja de chat con colita.

**Escritura**
- Que la IA se disculpe en los errores.
- Verbos vacíos: «Enviar», «Continuar», «Aceptar» cuando existe un verbo
  concreto.
- Pantallas vacías con una frase de ánimo en lugar de una acción.

---

## 11. Voz de la interfaz

Tono llano, en sentencia normal, sin relleno. El botón dice lo que ocurre:
«Guardar profesión», no «Aceptar». El nombre de una acción no cambia a lo largo
del recorrido.

Los mensajes de límite informan, no regañan ni felicitan:

- Correcto: «Quedan 2 consultas personales hoy.»
- Correcto: «BloqIA está cerrada hasta mañana a las 09:14.»
- Incorrecto: «¡Ups! Parece que llegaste al límite 😅»
- Incorrecto: «¡Buen trabajo pensando por tu cuenta!»

La pantalla vacía de conversación no motiva: orienta. «Preguntá sobre lo que
estás estudiando. Las consultas personales están limitadas a 3 por día.»