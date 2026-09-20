# Feature Specification: Modulo de Usuario

**Feature Branch**: `001-modulo-usuario`

**Created**: 2026-09-20

**Status**: Draft

**Input**: User description: "modulo de usuario. El modulo de usuario debe tener 4 apartados principales: Login con mail y contrasenia, y login con GMAIL directamente vinculado; Register con mail como primary key, contrasenia segura, edad y profesion; si se usa Gmail se obtiene la informacion correspondiente y, si no es posible, se piden los cuadros faltantes; perfil muestra todos los campos disponibles y permite cambiar informacion; perfil tecnico muestra modelos de diferentes proveedores de IA disponibles y permite cargar token aclarando el proveedor para poder usar mas."

## Clarifications

### Session 2026-09-20

- Q: ¿Qué debe hacer el sistema cuando una cuenta tiene varios intentos fallidos de login seguidos? → A: Solo mostrar error; no bloquear por intentos fallidos.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Login de usuario (Priority: P1)

Como usuario registrado, quiero ingresar al sistema con mi mail y contrasenia o con mi cuenta de Google para acceder a las funciones personalizadas de la biblioteca.

**Why this priority**: Sin acceso autenticado no se puede usar de forma confiable el perfil ni asociar preferencias, credenciales tecnicas o actividad de usuario.

**Independent Test**: Puede probarse creando un usuario valido, cerrando sesion y verificando que el usuario pueda acceder con mail y contrasenia, o con una cuenta de Google vinculada, y que vea su identidad correcta al ingresar.

**Acceptance Scenarios**:

1. **Given** un usuario registrado con mail y contrasenia validos, **When** ingresa ambos datos correctamente, **Then** el sistema inicia sesion y muestra el estado autenticado del usuario.
2. **Given** un usuario con una cuenta de Google vinculada, **When** elige ingresar con Google y la identidad es aceptada, **Then** el sistema inicia sesion con el perfil asociado.
3. **Given** un intento de ingreso con credenciales invalidas, **When** el usuario envia el formulario de login, **Then** el sistema rechaza el ingreso y muestra un mensaje claro sin revelar informacion sensible.

---

### User Story 2 - Registro de cuenta (Priority: P1)

Como visitante, quiero registrarme con mail, contrasenia segura, edad y profesion para crear una cuenta completa que pueda usar en el sistema.

**Why this priority**: El registro crea la identidad primaria del usuario y habilita el resto del modulo.

**Independent Test**: Puede probarse completando el registro con datos validos, verificando que la cuenta queda creada con todos los campos requeridos y que no se aceptan mails duplicados ni contrasenias inseguras.

**Acceptance Scenarios**:

1. **Given** un visitante sin cuenta, **When** completa mail, contrasenia segura, edad y profesion con datos validos, **Then** el sistema crea la cuenta y permite usarla para iniciar sesion.
2. **Given** un mail ya registrado, **When** un visitante intenta registrarse con ese mail, **Then** el sistema impide el duplicado e informa que debe iniciar sesion o usar otro mail.
3. **Given** una contrasenia que no cumple las restricciones de seguridad, **When** el visitante intenta registrarse, **Then** el sistema explica las reglas incumplidas y no crea la cuenta.
4. **Given** un visitante que inicia el registro con Google, **When** Google entrega parte de la informacion requerida, **Then** el sistema completa esos campos y solicita solamente los datos faltantes antes de finalizar la cuenta.

---

### User Story 3 - Gestion de perfil (Priority: P2)

Como usuario autenticado, quiero ver todos los campos disponibles de mi perfil y modificar mi informacion para mantener mis datos actualizados.

**Why this priority**: El perfil permite corregir informacion del usuario y mantiene consistencia entre registro, login y datos personales.

**Independent Test**: Puede probarse ingresando con una cuenta existente, abriendo el perfil, editando campos permitidos y verificando que los cambios quedan visibles en una nueva visita al perfil.

**Acceptance Scenarios**:

1. **Given** un usuario autenticado, **When** abre su perfil, **Then** el sistema muestra mail, edad, profesion, proveedor de ingreso vinculado y demas campos disponibles.
2. **Given** un usuario autenticado en su perfil, **When** modifica campos editables con datos validos, **Then** el sistema guarda los cambios y muestra la informacion actualizada.
3. **Given** un usuario autenticado, **When** intenta cambiar un dato protegido sin cumplir las validaciones requeridas, **Then** el sistema rechaza el cambio y explica como corregirlo.

---

### User Story 4 - Perfil tecnico de IA (Priority: P3)

Como usuario autenticado, quiero ver los modelos de IA disponibles por proveedor y cargar mis tokens por proveedor para habilitar mas opciones de uso.

**Why this priority**: El perfil tecnico amplia el valor para usuarios que quieren usar proveedores de IA, pero depende de que la cuenta y el perfil basico ya existan.

**Independent Test**: Puede probarse ingresando con un usuario autenticado, abriendo el perfil tecnico, viendo proveedores y modelos disponibles, agregando un token asociado a un proveedor y verificando que queda disponible para ese usuario.

**Acceptance Scenarios**:

1. **Given** un usuario autenticado, **When** abre el perfil tecnico, **Then** el sistema muestra los proveedores de IA disponibles y los modelos asociados a cada proveedor.
2. **Given** un usuario autenticado en el perfil tecnico, **When** carga un token para un proveedor especifico, **Then** el sistema registra esa credencial para su cuenta y muestra el proveedor como configurado.
3. **Given** un usuario autenticado con tokens cargados, **When** consulta su perfil tecnico, **Then** el sistema muestra el estado de cada proveedor sin exponer el token completo.
4. **Given** un token invalido o incompleto, **When** el usuario intenta guardarlo, **Then** el sistema rechaza la carga y explica que debe corregirse.

---

### Edge Cases

- El mail ingresado tiene formato invalido o ya pertenece a otra cuenta.
- La contrasenia no cumple longitud, variedad de caracteres o reglas contra datos personales obvios.
- Google no entrega edad, profesion u otro dato requerido durante el registro.
- Un usuario intenta registrar con Google un mail que ya existe con contrasenia.
- Un usuario intenta editar el mail principal por uno ya usado por otra cuenta.
- Un usuario abre el perfil tecnico cuando no hay proveedores o modelos disponibles.
- Un token cargado deja de ser valido despues de haber sido guardado.
- Un usuario cancela el flujo de Google antes de completar la vinculacion.
- Un usuario realiza varios intentos fallidos de login seguidos; cada intento se rechaza con mensaje seguro y la cuenta no queda bloqueada por esos intentos.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a user module with four main sections: Login, Register, Profile, and Technical Profile.
- **FR-002**: The system MUST allow registered users to log in with mail and contrasenia.
- **FR-003**: The system MUST allow users to log in with a linked Google account.
- **FR-004**: The system MUST reject invalid login attempts with a clear message that does not reveal whether the mail or contrasenia was the failing value.
- **FR-005**: The system MUST allow visitors to register with mail, contrasenia, edad, and profesion.
- **FR-006**: The system MUST treat mail as the unique primary identifier for a user account.
- **FR-007**: The system MUST enforce secure contrasenia rules requiring at least 10 characters, at least one letter, one number, one special character, and no obvious reuse of the user's mail.
- **FR-008**: The system MUST prevent registration with a mail that already belongs to an existing account.
- **FR-009**: When registration or login uses Google, the system MUST request available profile information from Google and prefill matching user fields.
- **FR-010**: When Google does not provide required registration information, the system MUST ask the user to complete only the missing required fields before the account can be completed.
- **FR-011**: The system MUST show authenticated users all available profile fields, including mail, edad, profesion, login method or linked provider status, and technical profile status.
- **FR-012**: The system MUST allow authenticated users to update editable profile information and MUST validate the changed values before saving.
- **FR-013**: The system MUST protect non-editable or sensitive fields from direct profile changes unless the required validation flow is completed.
- **FR-014**: The system MUST show authenticated users the available AI providers and the models available for each provider.
- **FR-015**: The system MUST allow authenticated users to add, replace, or remove a token for a selected AI provider.
- **FR-016**: The system MUST associate each token with the owning user and the selected provider.
- **FR-017**: The system MUST never display a full saved token after it has been stored; only masked or status information may be shown.
- **FR-018**: The system MUST clearly indicate whether each AI provider is not configured, configured, invalid, or requires attention for the current user.
- **FR-019**: The system MUST keep user profile data and technical credential data scoped to the authenticated user.
- **FR-020**: The system MUST provide user-facing validation messages for missing fields, invalid age, invalid mail, weak contrasenia, provider not selected, and invalid token format.
- **FR-021**: The system MUST NOT block an account solely because of repeated failed login attempts; every failed attempt MUST be rejected with the same safe error behavior defined for invalid credentials.

### Key Entities *(include if feature involves data)*

- **User**: Represents a person with access to the system. Key attributes include mail, contrasenia status, edad, profesion, linked login provider status, and profile metadata.
- **External Login Link**: Represents the relationship between a user account and a Google identity used for login and registration prefill.
- **AI Provider**: Represents a provider that offers AI models available to users.
- **AI Model**: Represents a model available through a provider, including its display name and availability status.
- **Provider Token**: Represents a user-owned credential associated with one AI provider, with status information and masked display behavior.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: At least 95% of users can complete mail-and-contrasenia login in under 30 seconds when they already have valid credentials.
- **SC-002**: At least 90% of new users can complete registration in under 2 minutes when all required information is available.
- **SC-003**: At least 90% of Google-based registrations require users to fill only fields that were not provided by Google.
- **SC-004**: 100% of duplicate-mail registration attempts are rejected before a second account is created.
- **SC-005**: 100% of saved provider tokens are hidden from full display after saving.
- **SC-006**: Users can identify which AI providers are configured or missing credentials within 10 seconds of opening the technical profile.
- **SC-007**: At least 90% of profile edits with valid data are completed without support intervention.

## Assumptions

- Mail is the stable unique identifier for a user account in this feature.
- Google login refers to sign-in with a Google account and may provide only part of the required registration data.
- Edad is required for registration and must be a valid positive age suitable for the educational project context.
- Profesion is free-form text selected or entered by the user.
- Token management is limited to user-provided provider tokens and does not include billing, provider subscription purchase, or organization-wide credential sharing.
- Provider and model availability can change over time, so the profile tecnico must present current availability status to the user.
- This specification defines the user-facing behavior only; implementation details will be decided in later Spec Kit phases.