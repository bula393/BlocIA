# Privacidad de BloqIA — borrador para revisión

> Documento local, pendiente de aprobación. Describe el código revisado el 9 de octubre de 2026; no es una política vigente ni está publicado. Los campos **PENDIENTE** deben resolverse antes de presentarlo como política pública.

**Responsable del servicio:** PENDIENTE de identificar. **Contacto propuesto:** [bloqia.app@gmail.com](mailto:bloqia.app@gmail.com). **Fecha de vigencia:** PENDIENTE.

## Datos y finalidades

BloqIA procesa información para crear tu cuenta, autenticarte, mantener tu perfil y tus conversaciones, responder consultas y aplicar límites de uso:

- **Cuenta local:** correo electrónico y contraseña para registrarte e ingresar. La base guarda un resumen de la contraseña (hash), no su texto original.
- **Acceso con Google:** se solicitan los permisos `openid`, `email` y `profile` y se reciben datos de identidad de Google. Se usan el identificador, el correo y su estado de verificación; se conserva el vínculo con tu cuenta, con fechas de uso. El flujo implementado no solicita acceso a Gmail, Drive ni contactos.
- **Perfil:** edad, profesión o actividad y nombre visible opcional, además de fechas y estado de la cuenta.
- **Conversaciones y actividad:** preguntas, respuestas, títulos, clasificación de las consultas, proveedor y modelo utilizados, fechas, duración de los turnos y eventos de uso, incluidos los relacionados con conexiones de proveedores. Sirven para mostrar el historial, continuar conversaciones y controlar cupos.
- **Claves propias de IA:** el valor completo se guarda cifrado y se recupera para autenticar solicitudes al proveedor correspondiente. La interfaz muestra una etiqueta enmascarada. Antes de guardarlas, se requiere verificar el correo.
- **Verificación por correo:** se envía un código de seis dígitos, válido durante diez minutos. En la base se guarda un resumen HMAC del código, junto con su vencimiento, intentos y estado de verificación. El servicio de correo recibe la dirección y el mensaje con el código.

## Procesamiento y proveedores de IA

La aplicación procesa la pregunta original para clasificarla. Cuando corresponde generar una respuesta, el modelo elegido recibe **la consulta actual, el nombre visible si existe, la edad, la profesión y hasta cuatro intercambios anteriores** de esa conversación. Si elegís un proveedor externo, esos datos salen hacia su API. El código contempla OpenAI, Anthropic, Google AI, Groq y OpenRouter, además del servicio de modelos locales de la aplicación. Las claves también se usan para consultar catálogos y disponibilidad del proveedor.

Antes de guardar la pregunta y al reconstruir el historial enviado al modelo, el código intenta sustituir algunos correos, teléfonos, nombres y direcciones. **Esa sustitución es parcial: no garantiza anonimato, no se aplica a la consulta actual enviada al generador ni elimina todos los datos que puedan aparecer en las respuestas.** Las consultas etiquetadas como decisiones personales no se envían al generador en el flujo actual; la clasificación automática puede equivocarse.

El código no permite determinar los usos posteriores, ubicaciones o plazos de conservación de cada proveedor externo. Deben revisarse sus condiciones y las cuentas efectivamente utilizadas antes de completar esta política.

## Cookies y almacenamiento en el navegador

Se usa `bloqia_session` para mantener la sesión y cookies temporales `bloqia_google_state` y `bloqia_google_result` para completar el acceso con Google. Están configuradas con `HttpOnly` y `SameSite=Lax`, y con `Secure` en producción. La cookie de sesión no tiene un vencimiento persistente explícito; el token de acceso vence a las 24 horas. Las cookies de Google tienen límites de diez minutos y dos minutos, respectivamente. El frontend mantiene el token en memoria; guarda la preferencia de la barra lateral en `localStorage` y la del modelo, por cuenta, en `sessionStorage`. El service worker guarda recursos públicos de la aplicación.

## Controles, conservación y contacto

Podés actualizar el perfil, eliminar conversaciones, desconectar una clave propia y cerrar la sesión. La eliminación de una conversación borra sus mensajes y turnos de la base de la aplicación; desconectar una clave elimina su registro y secreto cifrado. Esto no define el tratamiento de otros eventos de uso, respaldos o datos ya enviados a terceros.

**PENDIENTE:** establecer los criterios de conservación, el procedimiento para solicitar eliminación de la cuenta y otros datos, y el alcance sobre respaldos. El código revisado no implementa un plazo general de borrado automático ni una función de eliminación de cuenta. Para consultas sobre tus datos, el contacto propuesto es **bloqia.app@gmail.com**; no incluyas contraseñas ni claves API.

---

## Notas para quien revisa — no forman parte del texto público final

Antes de aprobar, faltan tres definiciones: **(1)** identidad del responsable y fecha de vigencia; **(2)** conservación y atención de solicitudes de eliminación; **(3)** proveedores efectivos de alojamiento y correo, ubicaciones, accesos operativos y respaldos. No se han revisado secretos ni configuración desplegada. El código por sí solo no permite certificar prácticas operativas o de terceros sobre acceso humano, registros, usos comerciales o entrenamiento, ni establecer garantías de seguridad.

Base técnica comprobada: [cuenta y perfil](../back/app/domain/user/user.py), [acceso y cookies](../back/app/presentation/user/auth_routes.py), [contexto enviado a IA](../back/app/application/chat/context.py), [flujo y redacción](../back/app/application/chat/send_message.py), [claves cifradas](../back/app/infrastructure/user/sqlite_repositories.py), [verificación de correo](../back/app/application/user/verify_email.py), [borrado de conversaciones](../back/app/infrastructure/chat_repository.py).

Google pide describir con exactitud el acceso, uso, almacenamiento y comunicación de sus datos. Su sección **Limited Use** añade requisitos para los alcances de productos a los que resulte aplicable; este borrador no declara su cumplimiento sin revisar las prácticas completas. [Google API Services User Data Policy](https://developers.google.com/terms/api-services-user-data-policy). La guía de producción exige una homepage pública con enlace a privacidad y contempla términos de servicio opcionales. [Guía oficial de Google](https://developers.google.com/identity/protocols/oauth2/production-readiness/policy-compliance#host-home-page).
