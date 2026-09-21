# Feature Specification: Correccion Grafica

**Feature Branch**: `002-correccion-grafica`

**Created**: 2026-09-21

**Status**: Draft

**Input**: User description: "correccion grafica. Al entrar a la pagina debe verse una pagina de inicio en la que esta el logo arriba a la derecha, por ahora un circulo, una frase como 'las decisiones las tomas vos' y un boton de iniciar sesion a la derecha. Las partes mas alla de inicio, login y register requieren estar logueado. El resto deben tener el token jwt."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Ver inicio publico (Priority: P1)

Como visitante, quiero entrar al sitio y ver una pagina de inicio clara con identidad visual, frase principal y acceso a inicio de sesion para entender donde estoy y como continuar.

**Why this priority**: Es la primera pantalla del producto y define el acceso al resto del sistema sin exigir autenticacion previa.

**Independent Test**: Puede probarse abriendo la ruta inicial sin sesion y verificando que se muestra el logo circular arriba a la derecha, la frase principal y el boton para iniciar sesion.

**Acceptance Scenarios**:

1. **Given** un visitante sin sesion, **When** abre la ruta inicial, **Then** ve una pagina de inicio publica sin ser redirigido.
2. **Given** un visitante en la pagina de inicio, **When** observa la cabecera, **Then** ve un logo circular ubicado arriba a la derecha.
3. **Given** un visitante en la pagina de inicio, **When** busca la accion principal, **Then** ve un boton para iniciar sesion ubicado hacia la derecha.
4. **Given** un visitante en la pagina de inicio, **When** lee el mensaje principal, **Then** encuentra una frase equivalente a "las decisiones las tomas vos".

---

### User Story 2 - Acceder a login y registro sin sesion (Priority: P1)

Como visitante, quiero poder abrir login y register sin estar autenticado para iniciar sesion o crear una cuenta.

**Why this priority**: Sin acceso publico a login y registro, los usuarios no pueden obtener una sesion valida.

**Independent Test**: Puede probarse abriendo las rutas de login y register sin token y verificando que ambas pantallas son accesibles.

**Acceptance Scenarios**:

1. **Given** un visitante sin sesion, **When** abre login desde la pagina de inicio, **Then** puede ver y usar la pantalla de inicio de sesion.
2. **Given** un visitante sin sesion, **When** abre register, **Then** puede ver y usar la pantalla de registro.
3. **Given** un visitante sin sesion, **When** intenta volver desde login o register a inicio, **Then** puede regresar sin autenticarse.

---

### User Story 3 - Proteger rutas privadas (Priority: P2)

Como usuario no autenticado, quiero que las rutas privadas no muestren informacion protegida para que mis datos y funciones personales no queden expuestos.

**Why this priority**: La proteccion de perfil, perfil tecnico y demas secciones privadas es necesaria para seguridad y privacidad.

**Independent Test**: Puede probarse abriendo cada ruta privada sin token JWT valido y verificando que no se muestra contenido protegido y que se ofrece iniciar sesion.

**Acceptance Scenarios**:

1. **Given** un visitante sin token JWT valido, **When** intenta abrir una ruta distinta de inicio, login o register, **Then** el sistema impide ver el contenido protegido.
2. **Given** un visitante bloqueado por falta de autenticacion, **When** el sistema muestra la respuesta, **Then** ofrece una accion clara para iniciar sesion.
3. **Given** un usuario con token JWT valido, **When** abre una ruta privada, **Then** puede ver la seccion solicitada.
4. **Given** un usuario con token JWT vencido o invalido, **When** abre una ruta privada, **Then** el sistema lo trata como no autenticado y no muestra contenido privado.

---

### User Story 4 - Mantener coherencia visual normativa (Priority: P2)

Como usuario, quiero que inicio, login, register y rutas protegidas respeten el sistema visual BloqIA para que la experiencia sea consistente y reconocible.

**Why this priority**: La correccion es grafica y debe cumplir el documento normativo `apartadoDIseñoGraficoBlocIA.md`.

**Independent Test**: Puede probarse inspeccionando las pantallas publicas y protegidas para verificar paleta, radios, chasis, ausencia de tarjetas flotantes y ausencia de elementos prohibidos.

**Acceptance Scenarios**:

1. **Given** cualquier pantalla de esta feature, **When** se revisa su composicion, **Then** usa bloques macizos, filetes y superficies permitidas por el sistema visual.
2. **Given** cualquier pantalla de esta feature, **When** se revisan colores y radios, **Then** solo se usan la paleta, opacidades y radios permitidos.
3. **Given** cualquier pantalla de esta feature, **When** se revisa la interfaz, **Then** no aparecen gradientes decorativos, tarjetas flotantes, botones pildora, sombras difusas, emojis ni iconografia prohibida.

---

### Edge Cases

- Un visitante intenta abrir directamente `/perfil` o `/perfil-tecnico` sin JWT valido.
- Un visitante intenta abrir una ruta privada con JWT mal formado, vencido o perteneciente a otra sesion.
- Un usuario autenticado abre `/login` o `/register`; el sistema debe evitar confundirlo y ofrecer una salida coherente hacia una zona autenticada.
- El logo temporal es solo un circulo y no debe introducir iconografia no permitida.
- La frase principal no cabe en pantallas chicas; debe adaptarse sin superponerse con el logo ni el boton.
- La ruta inicial se abre en mobile y debe mantener el logo, frase y accion visibles sin usar tarjetas flotantes.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST provide a public start page as the first visible page for unauthenticated visitors.
- **FR-002**: The public start page MUST show a temporary circular logo positioned at the top right.
- **FR-003**: The public start page MUST show a main phrase equivalent to "las decisiones las tomas vos".
- **FR-004**: The public start page MUST show a clear login action positioned toward the right side of the page.
- **FR-005**: The start page, login page, and register page MUST be accessible without authentication.
- **FR-006**: Every route outside start, login, and register MUST require an authenticated user.
- **FR-007**: The system MUST require a valid JWT token before showing protected route content.
- **FR-008**: When a protected route is requested without a valid JWT token, the system MUST prevent protected content from being shown and MUST provide a clear path to login.
- **FR-009**: When a protected route is requested with an invalid or expired JWT token, the system MUST treat the request as unauthenticated.
- **FR-010**: Authenticated users MUST be able to access protected pages without being redirected back to login.
- **FR-011**: The start page, login page, register page, and protected-route guard states MUST comply with `apartadoDIseñoGraficoBlocIA.md`.
- **FR-012**: The UI MUST NOT introduce visual elements prohibited by `apartadoDIseñoGraficoBlocIA.md`, including decorative gradients, floating cards as primary layout, pill buttons, diffuse shadows, emoji, or prohibited AI iconography.
- **FR-013**: The temporary logo MUST remain a circle until a final brand asset is specified.
- **FR-014**: The layout MUST keep logo, phrase, and login action visible and non-overlapping on desktop, tablet, and mobile viewports.

### Key Entities *(include if feature involves data)*

- **Public Start Page**: Represents the unauthenticated first screen, including temporary logo, main phrase, and login action.
- **Route Access Rule**: Represents whether a route is public or protected.
- **Authenticated Session**: Represents the user's current authenticated state based on a valid JWT token.
- **Protected Route Guard**: Represents the rule that prevents private content from appearing without valid authentication.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of unauthenticated visits to the root/start route show the public start page instead of a protected page.
- **SC-002**: 100% of unauthenticated visits to login and register can reach those screens without a token.
- **SC-003**: 100% of protected routes deny private content when no JWT token, an invalid token, or an expired token is present.
- **SC-004**: Users with a valid JWT token can reach protected routes in at least 95% of test attempts without an unnecessary redirect to login.
- **SC-005**: Visual QA across desktop, tablet, and mobile confirms the logo, main phrase, and login action are visible and do not overlap.
- **SC-006**: Visual QA finds zero prohibited visual elements from `apartadoDIseñoGraficoBlocIA.md` on the start, login, register, and protected-route guard screens.

## Assumptions

- The root route is treated as the public start page unless a later plan chooses a separate public path.
- Login and register remain public routes because they are required to obtain authentication.
- Perfil, perfil tecnico, and future application sections are protected unless explicitly documented as public.
- JWT is the required authentication token type for this correction because the user explicitly requested it.
- The temporary logo is a plain circle and does not represent final branding.
- The visual system in `apartadoDIseñoGraficoBlocIA.md` is normative for this feature.
