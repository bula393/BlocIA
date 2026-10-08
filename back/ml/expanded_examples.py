"""Deterministic, varied Spanish examples that complement the supplied seed set.

The examples intentionally cover questions, statements, fragments, and direct
requests. Classification depends on the request's meaning, not punctuation.
"""

LABELS = ("no_personal", "personal_informativa", "personal_decision")

NO_PERSONAL_TOPICS = """
la raíz cuadrada principal de un número
la diferencia entre una raíz exacta y una aproximada
las propiedades de las potencias
la regla de los exponentes negativos
la factorización de un polinomio
la resolución de una ecuación cuadrática
el método de sustitución en un sistema de ecuaciones
la fórmula para calcular el área de un círculo
el perímetro de una figura irregular
la conversión de fracciones a decimales
la simplificación de una fracción algebraica
la regla de tres simple
el cálculo de un porcentaje con descuento
la diferencia entre media, mediana y moda
la interpretación de una desviación estándar
el cálculo de una probabilidad compuesta
la regla de la cadena en derivadas
la derivada de una función exponencial
la integral definida de una función continua
el teorema de Pitágoras aplicado a un triángulo
la conversión de grados a radianes
la pendiente de una recta a partir de dos puntos
la representación de una función cuadrática
la resolución de una desigualdad con valor absoluto
la notación científica para números pequeños
la suma de vectores en el plano
el producto escalar de dos vectores
la resolución de una matriz por eliminación gaussiana
la diferencia entre permutaciones y combinaciones
el cálculo de una progresión geométrica
la primera ley de Newton
la relación entre masa, fuerza y aceleración
la conservación de la energía mecánica
la diferencia entre energía cinética y potencial
el cálculo de velocidad en movimiento uniformemente acelerado
la presión de un fluido en reposo
la ley de Ohm en un circuito simple
la asociación de resistencias en paralelo
el funcionamiento de un transformador eléctrico
la diferencia entre corriente alterna y continua
la refracción de la luz al pasar de un medio a otro
la formación de imágenes en una lente convergente
la frecuencia y la longitud de onda de un sonido
el funcionamiento de un átomo según el modelo actual
la diferencia entre protones, neutrones y electrones
el balanceo de una ecuación química
la escala de pH de una solución
la diferencia entre un enlace iónico y uno covalente
la conservación de la masa en una reacción química
el proceso de fotosíntesis en las plantas
la función de las mitocondrias en una célula
la diferencia entre una célula animal y una vegetal
la replicación del ADN
el sistema circulatorio humano
la función de los anticuerpos
la clasificación de los seres vivos
el ciclo del agua en la naturaleza
la diferencia entre clima y tiempo meteorológico
las causas de las estaciones del año
la formación de las placas tectónicas
la estructura interna de la Tierra
el proceso de erosión de una montaña
la diferencia entre una fuente primaria y una secundaria
el contexto histórico de la Revolución de Mayo
las causas principales de la Revolución Industrial
la organización política de la antigua Roma
la estructura de un texto argumentativo
la diferencia entre sujeto tácito y sujeto expreso
el uso de la coma en una enumeración
la concordancia entre sujeto y verbo
la traducción de una expresión idiomática al inglés
la diferencia entre pasado simple y presente perfecto
el significado de la palabra polisemia
la formación de palabras por derivación
la métrica de un verso alejandrino
el uso de conectores para ordenar un ensayo
la declaración de una variable en Python
la diferencia entre una lista y una tupla en Python
el alcance de una variable local
la definición de una función en JavaScript
el uso de una clase abstracta en Java
la diferencia entre una interfaz y una clase
la herencia en programación orientada a objetos
el manejo de excepciones en Java
la lectura de un archivo CSV con Python
la creación de un entorno virtual de Python
la resolución de dependencias en npm
el funcionamiento de una promesa en JavaScript
la consulta JOIN entre dos tablas SQL
la diferencia entre LEFT JOIN e INNER JOIN
la creación de un índice en una base de datos
la normalización de una base relacional
el diseño de una API REST
la diferencia entre los métodos HTTP GET y POST
el formato JSON para intercambiar datos
el cifrado simétrico frente al asimétrico
la autenticación mediante tokens
el cálculo de una máscara de subred
la diferencia entre TCP y UDP
el funcionamiento de la memoria caché
la diferencia entre un disco SSD y uno HDD
la resolución y frecuencia de actualización de una pantalla
la configuración de un sensor ultrasónico con Arduino
la lectura de un circuito con un multímetro
la detección de colisiones en Godot
la generación de aldeanos en Minecraft
""".strip().splitlines()

PERSONAL_SIGNALS = """
lo que siente esta persona por mí
si le gusto a la persona que me interesa
el interés que parece tener en mí
si de verdad le importo
el cariño que me demuestra
si siente algo más que amistad
la posibilidad de que le haya molestado lo que hice
su distancia después de nuestra conversación
el tono de este chat y lo que podría expresar
el posible sentido de su último mensaje
la interpretación de una respuesta que me dejó dudas
si su manera de hablarme muestra interés
si está siendo cortante o simplemente tiene muchas cosas que hacer
la demora con la que suele responderme
el cambio en la forma en que se comunica conmigo
las señales de que algo de lo que dije le molestó
quién parece mostrar más interés en nuestras conversaciones
si esta persona quiere seguir hablando conmigo
si intenta acercarse o tomar distancia
si lo que pasó puede ser una señal de que le gusto
la frecuencia con la que me mira cuando estamos juntos
que busque motivos para iniciar una charla conmigo
que recuerde detalles pequeños que le conté
que quiera pasar tiempo conmigo
si su actitud es normal entre personas que solo son amigas
si lo que hace parece coqueteo o amistad
si estoy confundiendo su amabilidad con interés
las señales contradictorias que recibo de esta persona
qué comportamientos parecen mostrar interés y cuáles no
por qué me afecta tanto lo que hace esta persona
por qué pienso tanto en él
si estoy enamorado o si simplemente me encariñé
los nervios que siento cuando hablamos
por qué me importa tanto que me responda
si estoy sobrepensando lo que pasó
si interpreto la situación de forma demasiado positiva o negativa
las razones por las que me siento así
lo que realmente siento por alguien que me atrae
la diferencia entre que alguien me guste y estar enamorado
la inseguridad que me aparece al conocer a alguien
el miedo a mostrar lo que siento
mi reacción cuando esa persona tarda en contestar
la tristeza que me queda después de una discusión
los celos que siento aunque no quiera sentirlos
la confusión que me produce una relación indefinida
el límite que necesito poner en esta relación
cómo expresar que algo me molestó sin generar una pelea
la forma de acercarme sin que la situación resulte incómoda
qué puede estar pasando si siento que se está alejando
la charla pendiente que tengo con mi pareja
la diferencia de expectativas entre mi pareja y yo
el silencio de mi pareja después de una discusión
la forma en que mi amigo reaccionó a lo que le conté
si mi familia entendió lo que quise decir
la culpa que siento después de poner un límite
la dificultad que tengo para pedir ayuda
el cansancio que me produce sostener esta rutina
por qué me cuesta mantener mis hábitos
la frustración que me da no avanzar con mis objetivos
las prioridades que quiero ordenar este mes
mi dificultad para organizar el tiempo entre estudio y trabajo
la presión que siento antes de un examen
la inseguridad que me genera elegir una carrera
mi malestar con el ambiente de mi trabajo actual
la conversación que necesito tener con mi jefe
las dudas que tengo sobre una propuesta laboral
la preocupación por mis gastos de este mes
la forma en que podría ordenar mis deudas
la inquietud que me genera compartir un gasto con mi familia
el estrés que siento antes de mudarme
las razones por las que me cuesta adaptarme a mi nueva casa
la tensión que tengo con una persona de mi grupo de amigos
la sensación de quedar afuera cuando se juntan sin mí
la incomodidad que me genera conocer gente nueva
el temor a decepcionar a alguien que quiero
la manera en que reaccioné cuando recibí una crítica
la vergüenza que sentí en esa reunión
mi dificultad para hablar de lo que necesito
la sensación de que siempre cedo para evitar conflictos
lo que me pasa cuando alguien no respeta mis límites
la incertidumbre que siento al empezar una relación
la distancia que se instaló entre una amiga y yo
la diferencia entre extrañar a alguien y querer volver
mi reacción al reencontrarme con una persona del pasado
lo que puede significar que mi pareja esté más callada
la confianza que siento en esta relación
el equilibrio entre el tiempo en pareja y mi espacio personal
el miedo que me da terminar una relación larga
la duda de si mi vínculo actual me hace bien
mi preocupación por un síntoma que viene apareciendo
la ansiedad que me da pedir un turno médico
la forma de registrar lo que siento antes de hablar con un profesional
mi dificultad para sostener una alimentación ordenada
la frustración que me genera empezar y abandonar el ejercicio
el agotamiento que arrastro durante la semana
la carga de responsabilidades que tengo en casa
la culpa que me aparece cuando descanso
mi tendencia a aceptar compromisos aunque no tenga tiempo
el motivo por el que me cuesta decir que no
las opciones que tengo para reorganizar mi semana
la sensación de estar estancado en este momento
el cambio que noto en mi ánimo últimamente
lo que necesito para sentirme escuchado en esta conversación
la forma en que puedo entender mejor mis propias emociones
""".strip().splitlines()

PERSONAL_CHOICES = """
aceptar la oferta laboral nueva|seguir en mi puesto actual
renunciar este mes|esperar a tener otra propuesta
pedir un aumento|buscar trabajo en otra empresa
estudiar una carrera universitaria|hacer una formación más corta
cambiarme de carrera|terminar la que ya empecé
estudiar por la mañana|estudiar por la noche
rendir esta materia ahora|dejarla para el próximo llamado
anotarme en ese curso|guardar el dinero para más adelante
trabajar horas extra|reservar ese tiempo para descansar
postularme aunque no cumpla todos los requisitos|esperar a otra vacante
seguir con este proyecto|cerrarlo y empezar otro
aceptar a esa persona como socia|continuar con el negocio por mi cuenta
abrir el emprendimiento ahora|esperar a tener más ahorros
pedir un préstamo para el negocio|avanzar más despacio sin endeudarme
invertir en publicidad|comprar más materiales
subir el precio de mi producto|mantener el precio actual
firmar el contrato|pedir que revisen las condiciones
renovar el alquiler|buscar otra vivienda
comprar este departamento|seguir buscando opciones
hacer la mudanza este fin de semana|postergarla un mes
vivir cerca del trabajo|pagar menos alquiler en otro barrio
contratar una empresa de mudanza|pedir ayuda a mis amigos
arreglar esta computadora|comprar una nueva
cambiar el teléfono ahora|esperar una oferta
comprar una computadora portátil|armar una de escritorio
contratar internet más rápido|mantener el plan que tengo
comprar esta herramienta|alquilarla cuando la necesite
reparar el electrodoméstico|reemplazarlo por uno nuevo
comprar muebles ahora|seguir ahorrando
pintar mi habitación de verde|elegir un tono neutro
aceptar la invitación a la fiesta|quedarme en casa
responderle ahora|esperar hasta mañana
escribirle a esa persona|darle espacio para que me busque
decirle que me gusta|esperar un poco más
aclarar el malentendido|dejar que baje la tensión
pedirle disculpas hoy|esperar a poder hablar con calma
continuar la relación|terminarla
proponer una conversación sincera|esperar a que mi pareja la inicie
contarle lo que me preocupa|guardármelo por ahora
poner un límite en esta relación|seguir cediendo para evitar una discusión
aceptar volver a ver a esa persona|mantener la distancia
invitar a mi amigo a hablar|esperar unos días
decir que algo me molestó|dejar pasar el comentario
acercarme en la próxima salida|esperar una señal más clara
contestar con sinceridad|responder de forma más neutral
viajar este año|guardar el dinero
reservar este alojamiento|buscar una opción más económica
tomar el vuelo de la mañana|elegir el vuelo nocturno
viajar solo|esperar a que alguien pueda acompañarme
llevar el auto|moverme en transporte público
cancelar el viaje|ir aunque tenga algunas dudas
visitar la montaña|pasar las vacaciones en la playa
alquilar una cabaña|quedarme en un hotel
comprar el pasaje ahora|esperar una posible promoción
invitar a esa persona al viaje|hacer el viaje por mi cuenta
comprar este auto usado|seguir usando el que tengo
elegir el plan de seguro más amplio|contratar el más económico
pedir este préstamo|esperar hasta juntar el dinero
comprar el celular que me gusta|guardar esa plata
pagar la suscripción anual|seguir pagando mes a mes
usar mis ahorros en este proyecto|mantenerlos como fondo de emergencia
comprar la consola|actualizar mi computadora
elegir la computadora más potente|quedarme con la opción económica
arreglar la bicicleta|comprar otra
anotarme en el gimnasio|empezar a entrenar en casa
salir a caminar hoy|descansar esta tarde
seguir entrenando aunque esté cansado|tomarme el día libre
pedir un turno médico ahora|esperar unos días
consultar por este síntoma|ver si desaparece solo
empezar terapia|seguir intentando resolverlo por mi cuenta
hablar primero de mi ansiedad|llevar el tema de mi familia a terapia
descansar este fin de semana|aprovechar para ponerme al día
preparar la comida hoy|pedir algo ya hecho
desayunar algo dulce|elegir un desayuno salado
comer algo liviano|pedir mi plato favorito
comprar este abrigo|usar uno de los que ya tengo
ponerme ropa cómoda|vestirme de manera más arreglada
salir con mis amigos|quedarme descansando en casa
ordenar mi habitación ahora|dejarlo para mañana
bañarme antes de cenar|hacerlo más tarde
acostarme temprano|quedarme despierto un rato más
responder este mensaje en el grupo|esperar a tener algo más claro
organizar la fiesta de cumpleaños|hacer una reunión más sencilla
adoptar este perro|esperar hasta tener más tiempo
prestarle dinero a mi familiar|explicarle que no puedo
aceptar la propuesta de mi amigo|rechazarla
hablar con mi vecino por el ruido|esperar a ver si se repite
dejar este proyecto grupal|seguir participando
hacer primero la tarea urgente|avanzar con la tarea más larga
priorizar el estudio esta semana|dedicar más horas al trabajo
tomarme vacaciones ahora|guardar los días para fin de año
vender estas cosas|seguir guardándolas
donar la ropa que no uso|esperar por si vuelvo a necesitarla
reservar la mesa para seis|buscar un lugar más grande
ir a la reunión familiar|usar ese tiempo para descansar
aceptar esa responsabilidad|decir que no tengo disponibilidad
contarle a mi familia lo que pasó|esperar un momento más adecuado
pedir ayuda con este problema|intentar resolverlo sin involucrar a nadie
seguir con este plan|empezar de nuevo con otra idea
elegir el primer tema de mi presentación|comenzar por el que más domino
inscribirme ahora|esperar al próximo período
seguir en mi ciudad actual|irme a otra provincia
vender mi bicicleta|conservarla para más adelante
""".strip().splitlines()

# These verbatim prompts come from the user's supplied material. The label
# follows the intent boundary documented in datos_entrenamiento_clasificador_preguntas.md.
USER_EXAMPLES = {
    "personal_informativa": """
¿Qué siente esta persona por mí?
¿Le gusto?
¿Está interesado en mí?
¿Le importo?
¿Me tiene cariño?
¿Siente algo más que amistad?
¿Le molestó lo que hice?
¿Está distante porque está enojado conmigo?
Analizá este chat y decime qué parece sentir esta persona.
¿Qué quiere decir realmente con este mensaje?
¿Cómo interpretarías esta respuesta?
¿Te parece que está interesado por cómo me habla?
¿Está siendo cortante o simplemente está ocupado?
¿Por qué habrá tardado tanto en responder?
¿Qué significa que haya cambiado la forma de hablarme?
¿Hay señales de que le molestó algo?
¿Quién parece tener más interés en la conversación?
¿Parece que quiere seguir hablando conmigo?
¿Está intentando acercarse o alejarse?
¿Cómo puedo interpretar que me mire tanto?
¿Qué significa que busque excusas para hablarme?
¿Qué significa que recuerde cosas pequeñas sobre mí?
¿Qué significa que quiera pasar tiempo conmigo?
¿Es normal que haga esto si solamente somos amigos?
¿Esto parece coqueteo o amistad?
¿Estoy confundiendo amabilidad con interés?
¿Hay señales contradictorias?
¿Qué comportamientos parecen mostrar interés y cuáles no?
¿Por qué me afecta tanto lo que hace esta persona?
¿Por qué pienso tanto en él?
¿Estoy enamorado o simplemente me encariñé?
¿Por qué me pongo nervioso cuando hablamos?
¿Por qué me importa tanto que me responda?
¿Estoy sobrepensando esta situación?
¿Estoy interpretando las cosas de manera demasiado positiva o negativa?
¿Qué puede estar causando que me sienta así?
¿Cómo puedo entender mejor lo que siento?
¿Cómo sé si realmente me gusta alguien?
¿Cómo puedo decirle que me molestó algo sin pelear?
¿Qué puedo hacer si siento que se está alejando?
Tengo una puntada en el costado derecho del abdomen cada vez que respiro profundo.
Me doblé el tobillo jugando y lo tengo inflamado.
Me sangran un poco las encías al cepillarme.
Tengo las manos y los pies fríos todo el tiempo, incluso con calor.
Quiero saber si mi alimentación me aporta las vitaminas y minerales necesarios.
Me dan dolores de cabeza recurrentes por la tarde.
¿Qué podemos hacer con mis amigos este finde?
¿Qué planes están buenos para hacer con amigos?
¿Qué podemos hacer si somos cinco amigos?
¿Qué podemos hacer si somos un grupo grande?
¿Qué podemos hacer de noche con amigos?
¿Qué podemos hacer de día con amigos?
¿Qué podemos hacer sin gastar mucha plata?
¿Qué podemos hacer si está lloviendo?
¿Qué podemos hacer si hace mucho calor?
¿Qué podemos hacer si no queremos quedarnos en casa?
¿Qué lugares están buenos para ir con amigos?
¿Qué podemos hacer un sábado?
¿Qué podemos hacer un domingo?
¿Qué podemos hacer después de comer?
¿Qué plan puedo organizar para mi grupo de amigos?
¿Qué podemos hacer si todos estamos aburridos?
¿Qué salida puedo organizar para mi cumpleaños?
¿Qué podemos hacer para festejar algo?
¿Qué planes están buenos para un grupo de adolescentes?
¿Qué podemos hacer si tenemos poca plata?
¿Qué salida puedo hacer con dos amigos?
¿Qué salida puedo hacer con diez amigos?
¿Qué podemos hacer que sea divertido y diferente?
¿Qué plan estaría bueno para una juntada espontánea?
¿Qué podemos hacer para pasar toda la tarde juntos?
¿Qué podemos hacer de noche que no sea ir a una fiesta?
¿Qué lugares están buenos para ir a merendar con amigos?
¿Qué podemos hacer después de ir al cine?
¿Qué podemos hacer si queremos hacer algo al aire libre?
¿Qué salida podemos hacer para conocer gente nueva?
¿Qué plan podemos hacer sin tener que organizar demasiado?
""",
    "personal_decision": """
¿Qué podría responderle a este mensaje?
¿Cómo puedo acercarme sin que sea incómodo?
¿Qué debería comer hoy: algo rico o algo más saludable?
¿Qué me tendría que poner hoy: algo cómodo o algo más lindo?
¿Cuál manta es más linda: la de un color o la estampada?
¿Me conviene bañarme ahora o más tarde?
¿Qué queda mejor: zapatillas blancas o negras con este outfit?
¿Hoy debería salir o quedarme en casa?
¿Qué debería mirar esta noche: una película, una serie o videos?
¿Me conviene ordenar mi pieza ahora o dejarlo para mañana?
¿Qué desayuno es mejor para hoy: dulce o salado?
¿Debería comprar esto que me gusta o guardar la plata?
¿Qué queda más lindo en mi pieza: dejar este objeto acá o cambiarlo de lugar?
¿Hoy me conviene acostarme temprano o aprovechar un rato más despierto?
¿Qué música pega más para este momento: algo tranquilo o algo movido?
¿Debería responder este mensaje ahora o esperar un rato?
¿Qué plan sería más lindo para hoy: hacer algo solo, invitar a alguien o descansar?
¿Qué hago: viajo este año o ahorro el dinero?
¿Elijo un plan tranquilo o uno más divertido para la juntada?
""",
}

NO_PERSONAL_FORMS = (
    "Explicame {topic} con un ejemplo.",
    "Quiero entender {topic} desde cero.",
    "Necesito una definición sencilla de {topic}.",
    "{topic}: concepto y ejemplo, por favor.",
    "No me queda claro {topic}; desarrollalo paso a paso.",
    "Dame una explicación breve sobre {topic}.",
    "Estoy estudiando {topic}; prepará un resumen.",
    "¿Podés aclarar {topic} con palabras simples?",
    "Busco una introducción a {topic} y sus usos.",
    "Mostrame un ejemplo práctico de {topic}.",
    "Ayuda para aprender {topic} sin tecnicismos.",
)

PERSONAL_INFO_FORMS = (
    "Quiero entender mejor {signal}.",
    "Me cuesta interpretar {signal}; ayudame a mirarlo con contexto.",
    "Ayudame a analizar {signal} sin sacar conclusiones rápidas.",
    "Estoy intentando ordenar lo que siento frente a {signal}.",
    "Necesito una mirada equilibrada sobre {signal}.",
    "Me quedó dando vueltas {signal}; quiero comprenderlo mejor.",
    "Busco posibles interpretaciones de {signal}.",
    "No quiero asumir de más frente a {signal}; ayudame a distinguir hechos y suposiciones.",
    "¿Qué podría indicar {signal} en este contexto?",
    "¿Cómo puedo entender {signal} sin dar nada por seguro?",
    "Analizá conmigo {signal} y las distintas explicaciones posibles.",
)

DECISION_FORMS = (
    "Elegí por mí entre {left} y {right}.",
    "Estoy entre {left} y {right}; decime cuál debería elegir.",
    "Tomá la decisión por mí: {left} o {right}.",
    "No puedo decidirme entre {left} y {right}; resolvelo vos.",
    "Necesito una respuesta concreta: {left} o {right}. Decidí vos.",
    "Delego en vos esta elección: {left} o {right}.",
    "Decime exactamente cuál elijo: {left} o {right}.",
    "No quiero seguir dándole vueltas; elegí entre {left} y {right}.",
    "¿Cuál de estas opciones tomo? Elegila por mí: {left} o {right}.",
    "Quiero que definas mi próximo paso entre {left} y {right}.",
    "Me cuesta elegir entre {left} y {right}. Quedate con una por mí.",
)


def generate_examples():
    """Return deterministic, deduplicated examples as {text, label} rows."""
    rows = []
    for topic in NO_PERSONAL_TOPICS:
        rows.extend({"text": form.format(topic=topic), "label": "no_personal"} for form in NO_PERSONAL_FORMS)
    for signal in PERSONAL_SIGNALS:
        rows.extend({"text": form.format(signal=signal), "label": "personal_informativa"} for form in PERSONAL_INFO_FORMS)
    for pair in PERSONAL_CHOICES:
        left, right = pair.split("|", 1)
        rows.extend({"text": form.format(left=left, right=right), "label": "personal_decision"} for form in DECISION_FORMS)
    for label, block in USER_EXAMPLES.items():
        rows.extend({"text": text.strip(), "label": label} for text in block.strip().splitlines() if text.strip())

    # Keep generation deterministic and guard the intended three-class minimum.
    unique = {}
    for row in rows:
        key = " ".join(row["text"].casefold().split())
        existing = unique.get(key)
        if existing and existing["label"] != row["label"]:
            raise ValueError(f"Contradictory expanded labels: {row['text']}")
        unique[key] = row
    return list(unique.values())
