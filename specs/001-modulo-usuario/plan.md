# Implementation Plan: Modulo de Usuario

**Branch**: `001-modulo-usuario` | **Date**: 2026-09-20 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/001-modulo-usuario/spec.md`

## Summary

Implementar un modulo de usuario con Login, Register, Perfil y Perfil Tecnico.
El backend sera la fuente de verdad para identidad, perfil, vinculacion Google,
proveedores de IA y tokens. El frontend sera una PWA React + Vite + TypeScript
que consume estado de servidor mediante cache de servidor, guarda solo estado
local no autoritativo y nunca decide permisos, credenciales ni disponibilidad
real por cuenta propia.

Las historias se organizaran en tres fases de trabajo documental para la futura
generacion de tareas: Back, Front y Testing. La implementacion aun no se realiza
en esta fase.

El diseno visual se planifica como fases adicionales basadas en
`apartadoDIseñoGraficoBlocIA.md`: tokens/prohibiciones, estructura, componentes,
responsive y QA visual. Estas fases quedan documentadas en [visual-design.md](visual-design.md).

## Technical Context

**Language/Version**: Frontend TypeScript con React + Vite; backend FastAPI.

**Primary Dependencies**: React, Vite, TypeScript, TanStack Query para cache de
servidor, Zustand para store local, service worker PWA, proveedor de identidad
Google para login vinculado.

**Storage**: Persistencia transaccional para usuarios, vinculaciones externas,
proveedores/modelos de IA y tokens por usuario. La eleccion concreta se documenta
en [research.md](research.md) como PostgreSQL por unicidad, relaciones y manejo de
credenciales.

**Testing**: Tests de backend para reglas de negocio y seguridad; tests de
frontend para flujos de usuario; pruebas contractuales sobre interfaces externas;
validaciones end-to-end documentadas en [quickstart.md](quickstart.md).

**Target Platform**: Aplicacion web full-stack con frontend PWA y backend HTTP.

**Project Type**: Web application con backend, frontend y contratos HTTP.

**Performance Goals**: Login y registro visibles para el usuario en menos de 30
segundos en condiciones normales; Perfil Tecnico debe permitir identificar el
estado de proveedores en menos de 10 segundos; consultas de perfil y proveedores
deben paginar o filtrar si crecen mas alla de la pantalla util.

**Constraints**: El cliente no guarda tokens de sesion en `localStorage` ni
`sessionStorage`; los tokens de proveedores nunca se muestran completos; el
service worker cachea solo el shell y no respuestas privadas; el backend decide
autenticacion, identidad, propiedad de tokens y disponibilidad real. Los intentos
fallidos repetidos de login no bloquean la cuenta por si solos; cada intento se
rechaza con el mismo comportamiento seguro de credenciales invalidas.
El frontend debe respetar `apartadoDIseñoGraficoBlocIA.md`: chasis de bloques,
paleta cerrada, radios permitidos, tipografias indicadas, responsive definido y
prohibiciones visuales sin excepciones.

**Scale/Scope**: Un modulo de usuario con cuatro secciones, datos de perfil,
login mail/contrasenia, login Google, proveedores/modelos de IA y tokens por
usuario. Debe convivir con la escala constitucional del sistema educativo.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Specification traceability**: PASS. Cada decision de plan enlaza con las
  historias y requisitos FR-001 a FR-021 del spec.
- **Object-oriented/domain ownership**: PASS. Las reglas de identidad, perfil,
  token y proveedor quedan en entidades y servicios de dominio/aplicacion, no en
  componentes UI.
- **Layered responsibility boundaries**: PASS. Backend, frontend, contratos y
  validacion quedan separados; el frontend refleja estado, no decide reglas de
  negocio.
- **Backend quality and explicit types**: PASS. Los estados cerrados de login,
  proveedor, token y modelo se modelan como enums/value objects en el diseno.
- **Testing, verification, documentation**: PASS. La fase Testing queda separada
  y [quickstart.md](quickstart.md) define verificaciones antes de avanzar.
- **Scalable search and availability**: PASS. No aplica a busqueda de libros, y
  los listados de proveedores/modelos contemplan filtrado o paginacion si crecen.
- **Usable discovery interface**: PASS. El perfil tecnico prioriza claridad de
  estados de proveedor y modelos; el sistema visual normativo aporta reglas
  aplicables de forma, color, radio, tipografia, responsive y prohibiciones.
- **Phase discipline**: PASS. Esta fase solo crea/actualiza documentos de plan.

## Project Structure

### Documentation (this feature)

```text
specs/001-modulo-usuario/
├── plan.md
├── research.md
├── data-model.md
├── visual-design.md
├── quickstart.md
├── contracts/
│   └── openapi.yaml
├── checklists/
│   └── requirements.md
└── tasks.md
```

### Source Code (repository root)

```text
back/
├── app/
│   ├── domain/
│   │   └── user/
│   ├── application/
│   │   └── user/
│   ├── infrastructure/
│   │   └── user/
│   └── presentation/
│       └── user/
└── tests/
    ├── unit/
    ├── integration/
    └── contract/

front/
├── src/
│   ├── app/
│   ├── pages/
│   │   ├── Login.tsx
│   │   ├── Register.tsx
│   │   ├── Perfil.tsx
│   │   └── PerfilTecnico.tsx
│   ├── components/
│   │   ├── chasis/
│   │   ├── estado/
│   │   └── overlay/
│   ├── features/
│   │   └── usuario/
│   ├── api/
│   ├── sw/
│   ├── tokens/
│   └── types/
└── tests/
    ├── unit/
    ├── integration/
    └── e2e/
```

**Structure Decision**: Se usara una aplicacion web full-stack separada en
`back/` y `front/`. El backend mantiene dominio, casos de uso, infraestructura y
presentacion/API. El frontend sigue la arquitectura propuesta por el usuario:
React + Vite + TypeScript PWA, TanStack Query para cache de servidor, Zustand
solo para estado local no autoritativo, service worker limitado al shell y token
de acceso en memoria con refresco por cookie `httpOnly`.

## Story Phase Mapping

| Story | Back | Front | Testing |
|-------|------|-------|---------|
| Login de usuario | Identidad por mail/contrasenia, vinculacion Google, sesiones, mensajes de rechazo seguros y ausencia de bloqueo por intentos fallidos repetidos | Pantalla Login, accion Google, estados de error claros, cache de usuario autenticado | Tests de credenciales validas/invalidas, intentos fallidos repetidos sin bloqueo, Google vinculado, errores sin fuga de informacion |
| Registro de cuenta | Unicidad de mail, reglas de contrasenia, edad, profesion, prefill Google y completado de faltantes | Pantalla Register, formulario progresivo con datos faltantes, feedback de contrasenia segura | Tests de mail duplicado, contrasenia debil, registro Google incompleto y registro exitoso |
| Gestion de perfil | Lectura y actualizacion validada de campos editables, proteccion de campos sensibles | Pagina Perfil con todos los campos disponibles y edicion guiada | Tests de lectura, guardado valido, rechazo de datos invalidos y persistencia visible |
| Perfil tecnico de IA | Catalogo de proveedores/modelos, tokens por usuario/proveedor, estados de token y ocultamiento | Pagina Perfil Tecnico con proveedores, modelos, carga/reemplazo/remocion de token y tokens enmascarados | Tests de proveedor configurado/no configurado/invalido, ocultamiento total de token y propiedad por usuario |

## Visual Design Phase Mapping

| Phase | Purpose | Output |
|-------|---------|--------|
| V1 Tokens and Prohibitions | Convertir el sistema visual en restricciones verificables de paleta, tipografia, radios, sombras y formas permitidas | CSS variables and visual lint checklist |
| V2 Structural Layout | Sustituir superficies tipo tarjeta por chasis de bloques, filetes y regiones encastradas | Shared chassis components under `front/src/components/chasis/` |
| V3 User Module Components | Aplicar el lenguaje visual a Login, Register, Perfil y Perfil Tecnico sin crear nuevas formas | Page and component design tasks per story |
| V4 Responsive Adaptation | Cubrir escritorio, tablet and mobile segun los cortes definidos en el sistema visual | Responsive checks at >=1280, 1024-1279, 768-1023, and <=767 px |
| V5 Visual QA | Verificar screenshots, prohibiciones, contraste, foco, textos y ausencia de estado frontend autoritativo | Evidence under `specs/001-modulo-usuario/evidence/visual-qa.md` |

## Complexity Tracking

No constitution violations require justification.

## Post-Design Constitution Check

- **Specification traceability**: PASS. `research.md`, `data-model.md`,
  `contracts/openapi.yaml`, and `quickstart.md` trace back to the four user
  stories and FR-001 through FR-021.
- **Layer boundaries**: PASS. Data model, contracts, backend ownership,
  frontend cache/local-state rules, and validation guide keep domain,
  application, infrastructure, presentation/API, and frontend responsibilities
  separate.
- **Testing and documentation**: PASS. `quickstart.md` separates Back, Front,
  and Testing checks per story and requires curl evidence for endpoints.
- **Visual design compliance**: PASS. [visual-design.md](visual-design.md)
  translates `apartadoDIseñoGraficoBlocIA.md` into phased visual gates for the
  user module without changing implementation scope during planning.
- **Swagger/OpenAPI**: PASS. `contracts/openapi.yaml` defines the planned HTTP
  contract that must be reflected in Swagger/OpenAPI during implementation.
- **Phase discipline**: PASS. Only Spec Kit planning and design documents were
  created or updated.
