# Configuración recomendada del clasificador

## Arquitectura

```text
texto de entrada
    ↓
normalización mínima
    ↓
modelo de embeddings multilingüe
    ↓
clasificador supervisado
    ↓
etiqueta, confianza y revisión opcional
```

## Configuración inicial recomendada

```yaml
language: es
embedding_model: intfloat/multilingual-e5-small
embedding_prefix_query: "query: "
classifier: LogisticRegression
labels:
  - no_personal
  - personal_informativa
  - personal_decision
primary_grouping:
  no_personal: no_personal
  personal_informativa: personal
  personal_decision: personal
test_size: 0.20
validation_size: 0.10
random_state: 42
class_weight: balanced
max_iter: 2000
confidence_threshold: 0.70
review_threshold: 0.55
```

`multilingual-e5-small` es una buena primera versión porque es pequeño, multilingüe y rápido. Si la precisión semántica no alcanza, cambiar solamente `embedding_model` por uno de estos:

```yaml
# Más calidad y más consumo
embedding_model: Qwen3-Embedding-0.6B

# Mejor para textos largos o variados
embedding_model: BAAI/bge-m3
```

## Instalación sugerida en Python

```bash
pip install sentence-transformers scikit-learn pandas joblib
```

## Entrenamiento

```python
from pathlib import Path
import joblib
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

df = pd.read_csv("datos.csv")  # columnas: text,label

model = SentenceTransformer("intfloat/multilingual-e5-small")
X = model.encode(
    [f"query: {text}" for text in df["text"]],
    normalize_embeddings=True,
    show_progress_bar=True,
)
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.20,
    random_state=42,
    stratify=y,
)

classifier = LogisticRegression(
    max_iter=2000,
    class_weight="balanced",
)
classifier.fit(X_train, y_train)

print(classification_report(y_test, classifier.predict(X_test)))

Path("modelo_clasificador").mkdir(exist_ok=True)
classifier_path = "modelo_clasificador/classifier.joblib"
joblib.dump(classifier, classifier_path)
model.save("modelo_clasificador/embeddings")
```

## Inferencia

```python
import joblib
import numpy as np
from sentence_transformers import SentenceTransformer

embedder = SentenceTransformer("modelo_clasificador/embeddings")
classifier = joblib.load("modelo_clasificador/classifier.joblib")

def clasificar(texto: str) -> dict:
    vector = embedder.encode(
        [f"query: {texto}"],
        normalize_embeddings=True,
    )
    probabilidades = classifier.predict_proba(vector)[0]
    indice = int(np.argmax(probabilidades))
    etiqueta = classifier.classes_[indice]
    confianza = float(probabilidades[indice])

    if confianza < 0.55:
        estado = "revision_manual"
    elif confianza < 0.70:
        estado = "baja_confianza"
    else:
        estado = "aceptada"

    grupo = "personal" if etiqueta.startswith("personal_") else "no_personal"

    return {
        "label": etiqueta,
        "group": grupo,
        "confidence": round(confianza, 4),
        "status": estado,
    }
```

## Reglas de seguridad y calidad

- La clasificación `personal_decision` no debe hacer que el sistema decida automáticamente asuntos médicos, legales o financieros.
- Para esos temas, devolver `personal_decision` junto con `needs_human_review: true`.
- No registrar preguntas personales completas si no es necesario; anonimizar nombres, teléfonos, direcciones y correos.
- Medir `macro F1`, precisión y recall por etiqueta, no solamente accuracy.
- Prestar especial atención al recall de `personal_decision`, porque perder una solicitud de decisión puede ser más importante que confundir una pregunta informativa.
- Si la confianza está por debajo de `0.55`, pedir reformulación o enviar a revisión.

## Ajuste según el hardware

| Hardware disponible | Configuración |
|---|---|
| Solo CPU y poca RAM | `multilingual-e5-small` + Logistic Regression |
| CPU moderna o GPU pequeña | `Qwen3-Embedding-0.6B` + Logistic Regression/SVM |
| GPU con bastante VRAM | `bge-m3` o fine-tuning de un encoder en español |
| Prototipo sin dataset | `Gemma 3 4B` o `Qwen3 4B` con salida JSON, pero validar manualmente |

## Salida JSON esperada

```json
{
  "label": "personal_decision",
  "group": "personal",
  "confidence": 0.93,
  "status": "aceptada",
  "needs_human_review": false
}
```

## Evolución posterior

Cuando haya al menos varios cientos de consultas etiquetadas y ejemplos suficientes por clase, comparar este enfoque contra un clasificador de texto entrenado directamente con `BETO` o `RoBERTa` en español. No conviene hacer fine-tuning desde el principio: primero hay que estabilizar las etiquetas y los casos límite.

