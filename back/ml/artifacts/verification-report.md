# Verificación de BloqIA — 22 de septiembre de 2026

## Actualización: solo clasificación

La capa generativa fue retirada del servicio, la configuración y la preparación de modelos. El chat muestra categoría, confianza y revisión humana. El encoder E5 y los pesos entrenados se conservan.

Verificación de esta actualización: 33 pruebas de backend aprobadas; compilación de frontend aprobada; recorrido con el clasificador real aprobado (registro, clasificación, recarga del historial, revisión humana, vista móvil y borrado). Aplicación reiniciada: frontend HTTP 200 y SQLite con integridad `ok`, sin errores de relaciones.

## Registro histórico anterior: chat con generación

Los resultados siguientes corresponden a la versión anterior a la retirada del generador.

### Resultado

El clasificador fue entrenado, el modelo generativo fue instalado y el chat completo fue verificado con ambos modelos reales. La instalación local responde en http://127.0.0.1:5173 y la base de datos reporta integridad correcta.

| Comprobación | Resultado |
|---|---|
| Entrenamiento con datos originales | Aprobado; 370 ejemplos |
| Particiones entrenamiento / validación / prueba | 259 / 37 / 74 |
| Macro F1 en prueba | 0,958629 |
| Recall de decisiones personales en prueba | 1,000000; 24 de 24 |
| Predicciones correctas en prueba | 71 de 74 |
| Pruebas de backend | 34 aprobadas |
| Pruebas de frontend | 14 aprobadas |
| Compilación del frontend | Aprobada |
| Recorrido de navegador con modelos reales | Aprobado |
| Comprobaciones sobre la base instalada | 10 aprobadas |
| Integridad SQLite | `ok` |
| Errores de relaciones | 0 |
| Frontend HTTP | 200 |

## Recorrido probado en navegador

Registro con profesión Estudiante, acceso al chat, consulta general, respuesta generada localmente, clasificación visible, recarga con recuperación del historial, decisión sensible con revisión humana, adaptación a 390 × 844 píxeles y eliminación del chat. El test usa una base temporal sin datos de usuarios reales. No se detectaron errores de JavaScript.

## Base de datos

Se verificaron persistencia de cuentas y perfiles, contraseñas, cifrado de tokens, reinicio de conexiones, rollback, concurrencia, unicidad, referencias, importación del JSON sin modificarlo, aislamiento entre usuarios, reintentos sin duplicados y borrado en cascada.

La comprobación adicional sobre `back/data/blocia.sqlite3` creó registros temporales dentro de una transacción y los revirtió. Confirmó registro/contraseña, edición del perfil, cifrado y descifrado, historial, idempotencia, rollback, integridad al reabrir, claves foráneas y modo WAL. El detalle queda en `back/data/database-verification.json`.

## Alcance

Estos resultados describen las comprobaciones ejecutadas, no una garantía de ausencia de fallos en cualquier condición. Las métricas del clasificador corresponden a ejemplos sintéticos aportados; el agrupamiento de preguntas parecidas es léxico. La generación local puede tardar en CPU, especialmente durante la primera carga, y su calidad corresponde a un modelo pequeño. Los filtros de datos personales son heurísticos.

Las instrucciones y datos originales están preservados en `back/ml/source`. La configuración ejecutable está en `back/config/classifier.yaml` y `back/config/chat.yaml`. Los pesos grandes permanecen en `back/models`, excluidos de Git.
