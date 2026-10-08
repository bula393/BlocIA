"""Fixed replies for the four topic groups in the supplied training material."""
import re
import unicodedata


def _normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.casefold())
    without_marks = "".join(char for char in decomposed if not unicodedata.combining(char))
    return " ".join(re.findall(r"\w+", without_marks))


# If a message mentions more than one topic, prefer health, then relationship,
# then group plans, and finally everyday choices.
_GROUPS = (
    (
        "salud",
        (
            r"\b(salud|sintom\w*|dolor\w*|duele\w*|fiebre|tos|tobillo|abdomen|encias|"
            r"sangr\w*|esguince|fractur\w*|gingivitis|vitamin\w*|minerales?|medic\w*|"
            r"medico\w*|medicament\w*|tratamient\w*|cirugia|embaraz\w*|puntada|"
            r"inflamad\w*|frio.*(manos?|pies?)|manos?.*pies? frios?)\b",
        ),
        "No puedo evaluar síntomas ni dar un diagnóstico. Consultá con un profesional de la salud.",
    ),
    (
        "sentimental",
        (
            r"\b(amor|enamora\w*|romantic\w*|coquete\w*|pareja|novi[oa]|amistad|carino)\b",
            r"\b(mi|nuestra) relacion\b|\brelacion sentimental\b",
            r"\b(le gusto|si le gusto|le importo|me tiene carino|siente algo|que siente|"
            r"interesad\w* en mi|interes\w*.*conversacion|me atrae|me mir\w*|me habla|"
            r"hablarme|forma de hablarme|se aleja|alej\w* de mi|acerc\w*|enojad\w* conmigo|"
            r"cortant\w*.*ocupad\w*|distante|tard\w*.*responder|"
            r"molest\w* lo que hice|responderle a este mensaje|seguir hablando conmigo|"
            r"pasar tiempo conmigo|me afecta.*persona|persona.*me afecta|pienso tanto en|"
            r"me pongo nervios\w*|nervios\w* cuando hablamos|me importa.*(respuest\w*|respond\w*)|"
            r"sobrepens\w*|senales contradictorias|amabilidad.*interes|lo que siento|"
            r"mis sentimientos|me molesto algo|algo me molesto|acercarme.*incomodo|"
            r"se esta alejando|me estoy enamorando|senal\w*.*(gust|interes)|"
            r"senal\w*.*molest\w*|comportamient\w*.*interes|interes.*senal|"
            r"positiv\w*.*negativ\w*|sienta asi|me siento asi|causando.*sienta)\b",
            r"\b(interpret\w*|signific\w*|quiere decir)\b.*\b(chat|mensaje|respuesta)\b",
            r"\b(chat|mensaje|respuesta)\b.*\b(persona|pareja|interes|siente|gusto)\b",
            r"\bpersona\b.*\bsentir\w*\b|\bsentir\w*\b.*\bpersona\b|"
            r"\brecuerd\w*.*(sobre mi|de mi|detalles pequenos)\b|"
            r"\bbusque.*excusas.*hablarme\b|\bme gusta alguien\b|"
            r"\binteres.*comportamiento\b|\bpositiv\w* o negativ\w*\b",
        ),
        "No puedo saber con certeza qué siente otra persona. Si la situación te genera malestar, hablalo con alguien de confianza o consultá con un profesional.",
    ),
    (
        "planes",
        (
            r"\b(planes|juntada|salida|festej\w*|cumpleanos|merendar)\b",
            r"\bque podemos hacer\b|\bque hacemos\b",
            r"\bplan\w*.{0,70}\b(amigos|grupo|juntos|finde|fin de semana|cumpleanos|fiesta|"
            r"salida|noche|tarde|sin tener que organizar)\b",
            r"\b(amigos|grupo).{0,70}\b(que podemos hacer|planes?|salida|finde|fin de semana)\b",
            r"\b(grupo grande|grupo de [0-9]+ amigos|con mis amigos|con amigos)\b",
        ),
        "No puedo elegir un plan por vos. Tengan en cuenta el tiempo, el presupuesto y las preferencias de quienes participen; también podés consultarlo con el grupo.",
    ),
    (
        "cotidiano",
        (
            r"\b(comer|comida|desayun\w*|ropa|vestirme|outfit|zapatill\w*|manta|banarme|"
            r"pieza|habitacion|pelicula|serie|videos|ordenar|acostarme|dormir|musica|"
            r"quedarme en casa|guardar la plata|comprar esto|objeto)\b",
            r"\b(que queda mejor|que queda mas lindo|que deberia comer|que me pongo|"
            r"salir o quedarme|responder este mensaje ahora|ahora o mas tarde|"
            r"que plan.*(para hoy|hoy|solo|descansar)|hacer algo solo)\b",
        ),
        "No puedo tomar esa decisión por vos. Si te sirve, compará las opciones y pedile también su opinión a alguien de confianza.",
    ),
)

_COMPILED_GROUPS = tuple(
    (name, tuple(re.compile(pattern) for pattern in patterns), answer)
    for name, patterns, answer in _GROUPS
)


def predefined_response(text: str) -> tuple[str, str] | None:
    """Return (topic group, fixed answer) when text matches a supplied topic."""
    normalized = _normalize(text)
    for name, patterns, answer in _COMPILED_GROUPS:
        if any(pattern.search(normalized) for pattern in patterns):
            return name, answer
    return None
