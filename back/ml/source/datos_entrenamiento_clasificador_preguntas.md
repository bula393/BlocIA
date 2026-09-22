# Datos de entrenamiento: clasificador de preguntas

## Objetivo

Clasificar cada consulta según si la persona está pidiendo información o si espera que la IA intervenga en una decisión personal.

## Etiquetas

- `no_personal`: solicita información, explicación, cálculo, código, instrucciones o una opinión general sin delegar una decisión propia.
- `personal_informativa`: habla de una situación propia, pero pide comprenderla, analizarla u obtener alternativas; no pide que la IA elija por la persona.
- `personal_decision`: pide explícita o implícitamente que la IA elija, recomiende una opción concreta o decida qué debería hacer la persona.

La etiqueta principal solicitada originalmente puede obtenerse agrupando `personal_informativa` y `personal_decision` como `personal`.

## Formato recomendado

Guardar también una copia en JSONL o CSV para entrenar el modelo. Cada fila debe tener:

```json
{"text":"¿Qué es una API REST?","label":"no_personal"}
```

## Ejemplos de entrenamiento

### No personales

```text
¿Qué es una API REST?                                      | no_personal
¿Cómo conecto un motor paso a paso a un Arduino Mega?      | no_personal
¿Cuál es la diferencia entre RAM y almacenamiento?         | no_personal
¿Cómo hago una consulta JOIN en SQL?                       | no_personal
¿Qué significa que una función sea derivable?              | no_personal
¿Cuánto es 25 por 18?                                      | no_personal
¿Cómo se instala Python en Windows?                        | no_personal
¿Qué ventajas tiene usar Docker?                           | no_personal
¿Qué es la fotosíntesis?                                   | no_personal
¿Cómo traduzco esta frase al inglés?                       | no_personal
¿Qué modelo de Arduino tiene más pines?                    | no_personal
¿Cómo arreglo este error de Java?                          | no_personal
¿Qué diferencia hay entre HTTP y HTTPS?                    | no_personal
¿Cómo funciona una resistencia eléctrica?                  | no_personal
¿Qué materiales necesito para una granja de hierro?        | no_personal
¿Podés resumir este texto?                                  | no_personal
¿Qué es una matriz LED?                                     | no_personal
¿Cómo creo una tabla en MySQL?                             | no_personal
¿Qué significa la palabra “ambiguo”?                       | no_personal
¿Cómo calculo la velocidad final en MRUV?                  | no_personal
¿Qué es un transistor?                                     | no_personal
¿Cómo configuro una red LAN?                               | no_personal
¿Qué diferencias hay entre una API gratuita y una paga?    | no_personal
¿Cómo convierto un archivo WAV a MP3?                      | no_personal
¿Qué es un marco teórico?                                  | no_personal
```

### Personales informativas: no delegan la decisión

```text
¿Qué factores debería considerar antes de cambiar de trabajo?| personal_informativa
¿Podés ayudarme a analizar mis gastos mensuales?            | personal_informativa
¿Qué opciones tengo si no me gusta mi carrera?              | personal_informativa
¿Cómo puedo organizar mejor mi tiempo?                      | personal_informativa
¿Qué preguntas debería hacer antes de alquilar un departamento?| personal_informativa
¿Cómo comparo dos ofertas laborales?                        | personal_informativa
¿Qué riesgos tiene pedir un préstamo?                       | personal_informativa
¿Cómo puedo preparar una conversación difícil?              | personal_informativa
¿Qué información debería reunir antes de comprar una PC?    | personal_informativa
¿Me ayudás a ordenar las ventajas y desventajas de mudarme?  | personal_informativa
¿Cómo puedo saber si un curso me conviene?                  | personal_informativa
¿Qué alternativas tengo para ahorrar dinero?                | personal_informativa
¿Cómo analizo si este proyecto es viable?                   | personal_informativa
¿Qué debería revisar en un contrato antes de firmarlo?      | personal_informativa
¿Cómo puedo hablar con mi familia sobre este problema?      | personal_informativa
```

### Personales: delegan una decisión

```text
¿Qué carrera debería estudiar?                              | personal_decision
Elegí por mí entre estas dos computadoras.                  | personal_decision
¿Debería aceptar este trabajo?                              | personal_decision
¿Me conviene mudarme o quedarme donde estoy?                | personal_decision
Decime qué celular tengo que comprar.                       | personal_decision
¿Debería terminar mi relación?                              | personal_decision
¿Qué opción elegirías en mi lugar?                          | personal_decision
No sé qué hacer: ¿renuncio o sigo en este trabajo?          | personal_decision
Elegí una ciudad para que me vaya a vivir.                  | personal_decision
¿Compro ahora o espero?                                     | personal_decision
Decidí qué materia tengo que rendir primero.                | personal_decision
¿Acepto la propuesta de mi amigo?                           | personal_decision
¿Cuál de estos planes debería contratar?                    | personal_decision
Decime si tengo que comprar esta casa.                      | personal_decision
¿Debería estudiar programación o diseño?                    | personal_decision
¿Qué nombre le pongo a mi emprendimiento?                   | personal_decision
Elegí el mejor regalo para mi pareja.                       | personal_decision
¿Me conviene invertir mis ahorros en esta opción?            | personal_decision
¿Tengo que pedir disculpas o dejar pasar el tema?            | personal_decision
¿Qué hago: viajo este año o ahorro el dinero?               | personal_decision
```

## Casos límite importantes

```text
¿Qué ventajas tiene estudiar programación?                  | no_personal
¿Qué ventajas tiene para mí estudiar programación?          | personal_informativa
¿Debería estudiar programación?                             | personal_decision
¿Qué opinás sobre cambiar de trabajo?                       | personal_informativa
Decime si cambio de trabajo.                                | personal_decision
¿Podés comparar estas tres opciones?                        | personal_informativa
Elegí la mejor de estas tres opciones por mí.               | personal_decision
¿Cuál es el mejor celular del mercado?                      | no_personal
¿Cuál es el mejor celular para mí?                          | personal_informativa
Decime qué celular compro yo.                               | personal_decision
```

## Recomendaciones para ampliar el conjunto

1. Agregar preguntas reales del sistema, sin datos identificatorios.
2. Mantener cantidades parecidas por etiqueta.
3. Incluir errores de escritura, abreviaturas y español rioplatense.
4. Crear ejemplos negativos muy parecidos entre sí: `informar`, `analizar` y `decidir`.
5. Separar entrenamiento, validación y prueba por consulta completa; no copiar variantes casi idénticas entre conjuntos.
6. Revisar manualmente los errores del modelo y reincorporarlos como nuevos ejemplos.

## Campos opcionales para una versión más completa

```json
{
  "text": "¿Renuncio o sigo en este trabajo?",
  "label": "personal_decision",
  "group": "trabajo",
  "asks_for_choice": true,
  "needs_human_review": false
}
```

## Banco ampliado: 100 ejemplos adicionales por etiqueta

Estos ejemplos están pensados para agregar variedad temática, español rioplatense,
consultas breves y casos cercanos entre sí. En total hay 300 ejemplos nuevos.

### 100 ejemplos `no_personal`

```text
1. ¿Qué es una variable en programación? | no_personal
2. ¿Cómo se declara una clase en Java? | no_personal
3. ¿Qué diferencia hay entre una lista y un arreglo? | no_personal
4. ¿Cómo se calcula el área de un círculo? | no_personal
5. ¿Qué es la ley de Ohm? | no_personal
6. ¿Cómo funciona un sensor ultrasónico? | no_personal
7. ¿Qué significa compilar un programa? | no_personal
8. ¿Qué es una base de datos relacional? | no_personal
9. ¿Cómo se crea una clave primaria en SQL? | no_personal
10. ¿Qué es una función cuadrática? | no_personal
11. ¿Cómo se resuelve una ecuación de segundo grado? | no_personal
12. ¿Qué diferencia hay entre masa y peso? | no_personal
13. ¿Cómo se produce una reacción química? | no_personal
14. ¿Qué es el número atómico? | no_personal
15. ¿Cómo se mide la tensión de una batería? | no_personal
16. ¿Qué es un circuito en serie? | no_personal
17. ¿Cómo se usa un multímetro? | no_personal
18. ¿Qué significa que una señal sea analógica? | no_personal
19. ¿Qué es PWM en Arduino? | no_personal
20. ¿Cómo se conecta un display LCD? | no_personal
21. ¿Qué es una API? | no_personal
22. ¿Cómo se envía una petición POST? | no_personal
23. ¿Qué diferencia hay entre JSON y XML? | no_personal
24. ¿Cómo se protege una contraseña en una aplicación? | no_personal
25. ¿Qué es una función hash? | no_personal
26. ¿Cómo funciona el cifrado AES? | no_personal
27. ¿Qué diferencia hay entre cifrado simétrico y asimétrico? | no_personal
28. ¿Qué es una firma digital? | no_personal
29. ¿Cómo se configura un puerto en un servidor? | no_personal
30. ¿Qué es una dirección IP privada? | no_personal
31. ¿Cómo se calcula una máscara de subred? | no_personal
32. ¿Qué función cumple un router? | no_personal
33. ¿Qué es el protocolo UDP? | no_personal
34. ¿Qué diferencia hay entre TCP y UDP? | no_personal
35. ¿Cómo se instala una dependencia de Node.js? | no_personal
36. ¿Qué es un entorno virtual de Python? | no_personal
37. ¿Cómo se ejecuta un proyecto de Spring Boot? | no_personal
38. ¿Qué es una entidad en JPA? | no_personal
39. ¿Cómo se define una relación uno a muchos? | no_personal
40. ¿Qué significa una migración de base de datos? | no_personal
41. ¿Cómo se escribe una consulta SELECT? | no_personal
42. ¿Qué es una transacción en una base de datos? | no_personal
43. ¿Cómo se ordenan resultados en SQL? | no_personal
44. ¿Qué diferencia hay entre INNER JOIN y LEFT JOIN? | no_personal
45. ¿Cómo se capturan excepciones en Java? | no_personal
46. ¿Qué es una interfaz en programación? | no_personal
47. ¿Qué significa herencia en programación orientada a objetos? | no_personal
48. ¿Cómo se usa un constructor? | no_personal
49. ¿Qué es una expresión regular? | no_personal
50. ¿Cómo se lee un archivo de texto en Python? | no_personal
51. ¿Qué es un algoritmo de ordenamiento? | no_personal
52. ¿Cómo funciona la búsqueda binaria? | no_personal
53. ¿Qué es la complejidad temporal? | no_personal
54. ¿Cómo se representa un grafo? | no_personal
55. ¿Qué es una cola circular? | no_personal
56. ¿Cómo se calcula un promedio ponderado? | no_personal
57. ¿Qué es la regla de la cadena? | no_personal
58. ¿Cómo se deriva un polinomio? | no_personal
59. ¿Qué significa integrar una función? | no_personal
60. ¿Cómo se calcula la probabilidad de un evento? | no_personal
61. ¿Qué diferencia hay entre media y mediana? | no_personal
62. ¿Cómo se interpreta una desviación estándar? | no_personal
63. ¿Qué es una variable aleatoria? | no_personal
64. ¿Cómo se construye un gráfico de barras? | no_personal
65. ¿Qué es el método científico? | no_personal
66. ¿Cómo se redacta una hipótesis? | no_personal
67. ¿Qué funciones cumple un marco teórico? | no_personal
68. ¿Qué diferencia hay entre una fuente primaria y una secundaria? | no_personal
69. ¿Cómo se cita un libro en formato APA? | no_personal
70. ¿Qué es una técnica de estudio activa? | no_personal
71. ¿Cómo funciona la memoria RAM? | no_personal
72. ¿Qué diferencia hay entre SSD y HDD? | no_personal
73. ¿Qué es una tarjeta gráfica? | no_personal
74. ¿Cómo se mide la resolución de una pantalla? | no_personal
75. ¿Qué significa que un monitor tenga 144 Hz? | no_personal
76. ¿Cómo se crea una copia de seguridad? | no_personal
77. ¿Qué es un sistema operativo? | no_personal
78. ¿Cómo se comprime una carpeta? | no_personal
79. ¿Qué diferencia hay entre un proceso y un hilo? | no_personal
80. ¿Qué es la memoria caché? | no_personal
81. ¿Cómo se generan aldeanos en Minecraft? | no_personal
82. ¿Qué materiales hacen falta para un portal al Nether? | no_personal
83. ¿Cómo funciona una granja de hierro? | no_personal
84. ¿Qué es el nivel de experiencia en Minecraft? | no_personal
85. ¿Cómo se domestica un lobo en Minecraft? | no_personal
86. ¿Qué es un nodo RigidBody2D en Godot? | no_personal
87. ¿Cómo se detecta una colisión en Godot 4? | no_personal
88. ¿Qué es una escena en Godot? | no_personal
89. ¿Cómo se reproduce una animación en Godot? | no_personal
90. ¿Qué significa que un cuerpo tenga gravedad cero? | no_personal
91. ¿Cómo se calcula la velocidad en MRUV? | no_personal
92. ¿Qué es el momento de una fuerza? | no_personal
93. ¿Cómo se aplica la segunda ley de Newton? | no_personal
94. ¿Qué diferencia hay entre energía cinética y potencial? | no_personal
95. ¿Cómo se calcula la resistencia equivalente? | no_personal
96. ¿Qué es la inducción electromagnética? | no_personal
97. ¿Cómo se comporta un diodo en polarización directa? | no_personal
98. ¿Qué es un transformador eléctrico? | no_personal
99. ¿Cómo se mide la continuidad con un tester? | no_personal
100. ¿Qué significa que un componente esté en corto? | no_personal
```

### 100 ejemplos `personal_informativa`

```text
1. ¿Qué factores debería evaluar antes de cambiar de empleo? | personal_informativa
2. ¿Me ayudás a ordenar mis prioridades para este mes? | personal_informativa
3. ¿Cómo puedo comparar dos carreras que me interesan? | personal_informativa
4. ¿Qué preguntas conviene hacer en una entrevista laboral? | personal_informativa
5. ¿Cómo analizo mis gastos sin olvidarme de nada? | personal_informativa
6. ¿Qué información tendría que reunir antes de mudarme? | personal_informativa
7. ¿Cómo puedo saber qué tareas me están quitando más tiempo? | personal_informativa
8. ¿Qué aspectos debería revisar de mi rutina de estudio? | personal_informativa
9. ¿Me ayudás a entender por qué no llego a fin de mes? | personal_informativa
10. ¿Qué opciones tengo para organizar una deuda? | personal_informativa
11. ¿Cómo comparo el costo real de alquilar y comprar? | personal_informativa
12. ¿Qué debería preguntarle a un médico en una consulta? | personal_informativa
13. ¿Cómo registro mis síntomas para explicarlos mejor? | personal_informativa
14. ¿Qué información necesito antes de empezar a entrenar? | personal_informativa
15. ¿Cómo puedo preparar una conversación con mi jefe? | personal_informativa
16. ¿Qué alternativas tengo si mi horario laboral me complica estudiar? | personal_informativa
17. ¿Cómo ordeno las ventajas y desventajas de este proyecto? | personal_informativa
18. ¿Qué riesgos debería analizar antes de asociarme con alguien? | personal_informativa
19. ¿Cómo puedo evaluar si una propuesta es confiable? | personal_informativa
20. ¿Qué datos necesito para comparar dos préstamos? | personal_informativa
21. ¿Me ayudás a analizar una discusión que tuve con un amigo? | personal_informativa
22. ¿Cómo puedo expresar mis límites sin generar una pelea? | personal_informativa
23. ¿Qué temas debería conversar con mi pareja sobre el futuro? | personal_informativa
24. ¿Cómo distingo una crítica útil de un comentario hiriente? | personal_informativa
25. ¿Qué puedo observar para entender si una relación me hace bien? | personal_informativa
26. ¿Cómo preparo una charla para pedir una disculpa? | personal_informativa
27. ¿Qué alternativas tengo para resolver un conflicto familiar? | personal_informativa
28. ¿Cómo puedo explicar lo que necesito sin sonar agresivo? | personal_informativa
29. ¿Qué debería considerar antes de volver a hablarle a alguien? | personal_informativa
30. ¿Cómo analizo si estoy aceptando demasiados compromisos? | personal_informativa
31. ¿Qué información conviene revisar antes de comprar una computadora? | personal_informativa
32. ¿Cómo comparo dos teléfonos según mi uso? | personal_informativa
33. ¿Qué debería medir para saber si mi conexión a internet alcanza? | personal_informativa
34. ¿Cómo puedo revisar si una reparación quedó bien hecha? | personal_informativa
35. ¿Qué preguntas debo hacerle a un vendedor de autos usados? | personal_informativa
36. ¿Cómo evalúo el costo de mantenimiento de una moto? | personal_informativa
37. ¿Qué aspectos debería mirar antes de firmar un alquiler? | personal_informativa
38. ¿Cómo comparo las condiciones de dos seguros? | personal_informativa
39. ¿Qué documentación debería preparar para un trámite? | personal_informativa
40. ¿Cómo puedo organizar los papeles importantes de mi familia? | personal_informativa
41. ¿Qué pasos me conviene seguir para buscar mi primer trabajo? | personal_informativa
42. ¿Cómo puedo mejorar mi currículum para un puesto técnico? | personal_informativa
43. ¿Qué habilidades debería identificar antes de elegir un curso? | personal_informativa
44. ¿Cómo analizo si tengo tiempo suficiente para una capacitación? | personal_informativa
45. ¿Qué puedo hacer para estudiar cuando me cuesta concentrarme? | personal_informativa
46. ¿Cómo registro mi progreso en una materia? | personal_informativa
47. ¿Qué técnicas puedo probar para recordar mejor un tema? | personal_informativa
48. ¿Cómo organizo un plan de estudio realista? | personal_informativa
49. ¿Qué señales indican que necesito cambiar mi método de estudio? | personal_informativa
50. ¿Cómo puedo preparar un examen sin estudiar toda la noche? | personal_informativa
51. ¿Qué información necesito para planificar unas vacaciones? | personal_informativa
52. ¿Cómo comparo dos destinos según presupuesto y tiempo? | personal_informativa
53. ¿Qué cosas conviene revisar antes de reservar un alojamiento? | personal_informativa
54. ¿Cómo organizo un viaje con varias personas? | personal_informativa
55. ¿Qué alternativas tengo si se cancela mi transporte? | personal_informativa
56. ¿Cómo puedo calcular el presupuesto diario de un viaje? | personal_informativa
57. ¿Qué debería llevar para un viaje de pocos días? | personal_informativa
58. ¿Cómo analizo si un destino es accesible para mi familia? | personal_informativa
59. ¿Qué preguntas conviene hacerle a una agencia de viajes? | personal_informativa
60. ¿Cómo planifico una salida sin gastar de más? | personal_informativa
61. ¿Qué información debería darle a un profesional de salud mental? | personal_informativa
62. ¿Cómo puedo describir mi nivel de estrés de forma clara? | personal_informativa
63. ¿Qué hábitos puedo observar para entender mi cansancio? | personal_informativa
64. ¿Cómo organizo un registro de sueño? | personal_informativa
65. ¿Qué preguntas puedo hacer sobre los efectos de un medicamento? | personal_informativa
66. ¿Cómo puedo prepararme para hablar de un tema incómodo en terapia? | personal_informativa
67. ¿Qué diferencias hay entre descansar y postergar una tarea? | personal_informativa
68. ¿Cómo analizo qué situaciones me generan ansiedad? | personal_informativa
69. ¿Qué alternativas tengo para pedir ayuda cuando me siento desbordado? | personal_informativa
70. ¿Cómo puedo hablar de mis hábitos sin sentir vergüenza? | personal_informativa
71. ¿Qué criterios puedo usar para elegir un regalo? | personal_informativa
72. ¿Cómo comparo proveedores para mi emprendimiento? | personal_informativa
73. ¿Qué costos debería incluir en el precio de un producto? | personal_informativa
74. ¿Cómo analizo si una idea de negocio tiene clientes? | personal_informativa
75. ¿Qué preguntas conviene hacer a un posible socio? | personal_informativa
76. ¿Cómo organizo las tareas de mi emprendimiento? | personal_informativa
77. ¿Qué datos necesito para evaluar una venta online? | personal_informativa
78. ¿Cómo puedo medir si una publicidad funciona? | personal_informativa
79. ¿Qué riesgos debería contemplar antes de ofrecer un servicio? | personal_informativa
80. ¿Cómo preparo un presupuesto para un proyecto personal? | personal_informativa
81. ¿Qué factores debería considerar al adoptar una mascota? | personal_informativa
82. ¿Cómo organizo el cuidado de una mascota entre varias personas? | personal_informativa
83. ¿Qué información necesito antes de reparar algo en casa? | personal_informativa
84. ¿Cómo puedo priorizar arreglos urgentes del hogar? | personal_informativa
85. ¿Qué debería revisar antes de comprar herramientas? | personal_informativa
86. ¿Cómo comparo el consumo eléctrico de dos aparatos? | personal_informativa
87. ¿Qué alternativas tengo para hacer más seguro mi hogar? | personal_informativa
88. ¿Cómo puedo organizar una mudanza paso a paso? | personal_informativa
89. ¿Qué preguntas conviene hacer antes de contratar una reparación? | personal_informativa
90. ¿Cómo calculo cuánto espacio necesito para guardar mis cosas? | personal_informativa
91. ¿Qué debería tener en cuenta para elegir una actividad física? | personal_informativa
92. ¿Cómo puedo adaptar una rutina a mi nivel actual? | personal_informativa
93. ¿Qué información necesito antes de anotarme en un gimnasio? | personal_informativa
94. ¿Cómo analizo si una meta es alcanzable? | personal_informativa
95. ¿Qué alternativas tengo para mantener una rutina cuando viajo? | personal_informativa
96. ¿Cómo puedo dividir un objetivo grande en tareas pequeñas? | personal_informativa
97. ¿Qué señales muestran que estoy avanzando en un hábito? | personal_informativa
98. ¿Cómo organizo una revisión semanal de mis objetivos? | personal_informativa
99. ¿Qué puedo registrar para entender por qué abandono mis planes? | personal_informativa
100. ¿Cómo comparo mis prioridades con el tiempo que realmente tengo? | personal_informativa
```

### 100 ejemplos `personal_decision`

```text
1. ¿Qué carrera elijo para estudiar? | personal_decision
2. Decidí por mí si acepto este trabajo. | personal_decision
3. ¿Renuncio hoy o espero unos meses? | personal_decision
4. Elegí cuál de estas dos computadoras compro. | personal_decision
5. ¿Me mudo o sigo viviendo donde estoy? | personal_decision
6. Decime qué teléfono tengo que comprar. | personal_decision
7. ¿Termino mi relación o intento continuar? | personal_decision
8. ¿Qué opción debería elegir entre estas ofertas? | personal_decision
9. Elegí una carrera por mí. | personal_decision
10. ¿Compro una casa o sigo alquilando? | personal_decision
11. Decime si acepto la propuesta de mi jefe. | personal_decision
12. ¿Tengo que cambiar de trabajo? | personal_decision
13. Elegí el mejor curso para mí. | personal_decision
14. ¿Estudio de mañana o de noche? | personal_decision
15. Decidí qué materia rindo primero. | personal_decision
16. ¿Viajo ahora o ahorro la plata? | personal_decision
17. Elegí el destino de mis próximas vacaciones. | personal_decision
18. ¿Compro este auto usado o lo dejo pasar? | personal_decision
19. Decime si conviene pedir este préstamo. | personal_decision
20. ¿Invierto mis ahorros o los dejo en la cuenta? | personal_decision
21. Elegí qué computadora le regalo a mi hermano. | personal_decision
22. ¿Le pido disculpas o espero que se calme? | personal_decision
23. Decime si vuelvo a hablarle a mi amigo. | personal_decision
24. ¿Acepto la invitación o me quedo en casa? | personal_decision
25. Elegí por mí si compro o no compro esto. | personal_decision
26. ¿Le cuento la verdad a mi familia? | personal_decision
27. Decime si tengo que responder ese mensaje. | personal_decision
28. ¿Me anoto en el gimnasio o empiezo en casa? | personal_decision
29. Elegí qué hábito debería empezar primero. | personal_decision
30. ¿Cambio de carrera este año? | personal_decision
31. Decime qué especialización profesional hago. | personal_decision
32. ¿Acepto trabajar horas extra o las rechazo? | personal_decision
33. Elegí cuál de estos tres empleos me conviene. | personal_decision
34. ¿Pido un aumento de sueldo? | personal_decision
35. Decime si me conviene trabajar por mi cuenta. | personal_decision
36. ¿Me postulo a ese puesto aunque no cumpla todo? | personal_decision
37. Elegí si sigo con este proyecto o lo abandono. | personal_decision
38. ¿Contrataría este servicio si estuvieras en mi lugar? | personal_decision
39. Decime qué proveedor tengo que usar. | personal_decision
40. ¿Abro el emprendimiento ahora o espero? | personal_decision
41. Elegí el precio que debería cobrar. | personal_decision
42. ¿Acepto a este socio para el negocio? | personal_decision
43. Decime si vendo este producto o lo guardo. | personal_decision
44. ¿Invierto en publicidad o en materiales? | personal_decision
45. Elegí qué idea de negocio desarrollo primero. | personal_decision
46. ¿Pido un préstamo para comprar herramientas? | personal_decision
47. Decime si firmo este contrato. | personal_decision
48. ¿Renuevo el alquiler o busco otra vivienda? | personal_decision
49. Elegí qué seguro contrato. | personal_decision
50. ¿Compro este departamento o sigo buscando? | personal_decision
51. Decime si acepto las condiciones del vendedor. | personal_decision
52. ¿Reclamo por el problema o lo dejo pasar? | personal_decision
53. Elegí qué reparación hago primero en casa. | personal_decision
54. ¿Cambio el teléfono ahora o espero una oferta? | personal_decision
55. Decime qué herramienta compro. | personal_decision
56. ¿Arreglo la computadora o compro otra? | personal_decision
57. Elegí qué componente necesito para mi proyecto. | personal_decision
58. ¿Contrato internet más rápido o mantengo el plan? | personal_decision
59. Decime qué proveedor de internet elijo. | personal_decision
60. ¿Compro una consola o actualizo la PC? | personal_decision
61. Elegí qué destino visitamos en familia. | personal_decision
62. ¿Reservo este alojamiento o busco otro? | personal_decision
63. Decime si viajo solo o acompañado. | personal_decision
64. ¿Tomo el vuelo temprano o el de la noche? | personal_decision
65. Elegí si llevo auto o uso transporte público. | personal_decision
66. ¿Cancelo el viaje o voy igual? | personal_decision
67. Decime qué actividades hacemos durante el viaje. | personal_decision
68. ¿Cambio las fechas de las vacaciones? | personal_decision
69. Elegí el hotel por mí. | personal_decision
70. ¿Invito a esa persona a viajar conmigo? | personal_decision
71. Decime si empiezo terapia. | personal_decision
72. ¿Pido un turno médico ahora o espero? | personal_decision
73. Elegí qué tema llevo primero a terapia. | personal_decision
74. ¿Le cuento estos síntomas al médico? | personal_decision
75. Decime si cambio mi rutina de ejercicios. | personal_decision
76. ¿Sigo entrenando aunque hoy esté cansado? | personal_decision
77. Elegí una actividad física para empezar. | personal_decision
78. ¿Me quedo descansando o voy a entrenar? | personal_decision
79. Decime qué hábito saludable incorporo primero. | personal_decision
80. ¿Pido ayuda por este problema o intento resolverlo solo? | personal_decision
81. Elegí qué mascota adoptar. | personal_decision
82. ¿Adopto este perro o sigo buscando? | personal_decision
83. Decime si compro las herramientas para arreglar la casa. | personal_decision
84. ¿Hago la mudanza este fin de semana? | personal_decision
85. Elegí qué habitación arreglo primero. | personal_decision
86. ¿Tiro estas cosas o las guardo? | personal_decision
87. Decime si conviene comprar muebles nuevos. | personal_decision
88. ¿Contratamos una empresa de mudanza? | personal_decision
89. Elegí el color para pintar mi habitación. | personal_decision
90. ¿Le presto dinero a mi familiar? | personal_decision
91. Decime si acepto la invitación a esa reunión. | personal_decision
92. ¿Respondo ahora o mañana? | personal_decision
93. Elegí qué regalo compro para mi pareja. | personal_decision
94. ¿Organizo la fiesta o la cancelo? | personal_decision
95. Decime si hablo con mi vecino por el problema. | personal_decision
96. ¿Participo en ese proyecto con mis amigos? | personal_decision
97. Elegí qué prioridad atiendo primero. | personal_decision
98. ¿Sigo con este plan o empiezo uno nuevo? | personal_decision
99. Decime cuál de estas opciones es la correcta para mí. | personal_decision
100. Elegí por mí qué debería hacer. | personal_decision
```

## Resumen del banco ampliado

| Etiqueta | Ejemplos nuevos |
|---|---:|
| `no_personal` | 100 |
| `personal_informativa` | 100 |
| `personal_decision` | 100 |
| **Total** | **300** |
