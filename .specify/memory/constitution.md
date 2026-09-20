<!--
Sync Impact Report
Version change: scaffold -> 1.0.0
Modified principles:
- Scaffold principle 1 -> I. Specification Traceability
- Scaffold principle 2 -> II. Object-Oriented Domain Model
- Scaffold principle 3 -> III. Layered Responsibility Boundaries
- Scaffold principle 4 -> IV. Backend Quality and Explicit Types
- Scaffold principle 5 -> V. Testing, Verification, and Documentation
Added principles:
- VI. Scalable Search and Availability
- VII. Usable Discovery Interface
- VIII. Phase Discipline
Added sections:
- Architectural Standards
- Development Workflow
Removed sections: None
Follow-up TODOs: None
-->
# BlocIA Library Education System Constitution

## Core Principles

### I. Specification Traceability
Every implemented feature MUST be traceable to an approved user story, requirement, or task in
the active Spec Kit artifacts. The specification governs implementation decisions; code that is
not backed by documented scope MUST NOT be added. Rationale: the project is used to teach
specification-driven development, so undocumented functionality undermines the learning model.

### II. Object-Oriented Domain Model
The domain model MUST use meaningful object-oriented design for business rules. Domain classes
MUST own behavior when they enforce borrowing, catalog, availability, client, or book-category
rules; anemic classes are only acceptable for pure transport structures. Rationale: the project
teaches object-oriented programming, so business behavior must be visible in the domain model.

### III. Layered Responsibility Boundaries
Responsibilities MUST remain separated by layer: domain contains business rules;
application/services contain use cases; infrastructure contains databases, repositories, and
persistence; presentation/API contains endpoints and DTOs; frontend contains the user interface.
Controllers MUST NOT contain business rules, repositories MUST NOT contain UI behavior, and DTOs
MUST NOT become domain substitutes. Rationale: clear boundaries make the full-stack system easier
to teach, test, and evolve.

### IV. Backend Quality and Explicit Types
Java backend code MUST avoid duplicated logic, oversized methods, controller-mixed validation,
and unnecessary `instanceof` checks. Closed sets of business values, including book categories,
MUST be represented with enums or value objects instead of raw strings or ad hoc constants.
Design patterns MAY be used only when they simplify the design or remove real duplication; forced
patterns are prohibited. Rationale: the codebase must demonstrate maintainable Java design, not
ceremonial architecture.

### V. Testing, Verification, and Documentation
Every important business rule and every function added or changed for a task MUST have relevant
tests. Before advancing between implementation tasks or phases, the team MUST run the appropriate
test suite or documented verification command and confirm the system still works. Any change made
to repair a problem, unblock execution, or alter behavior MUST be documented in the relevant Spec
Kit artifact, task notes, or project documentation. Rationale: educational work must leave an
auditable path from problem to fix.

### VI. Scalable Search and Availability
The system MUST support growth to at least 100,000 books and 10,000 clients. Availability search
and catalog lookup MUST NOT depend on scanning complete in-memory lists for normal application
flows; persistence queries, indexes, pagination, filtering, or equivalent scalable mechanisms MUST
be used. Rationale: performance constraints are part of the domain and must be taught early.

### VII. Usable Discovery Interface
The interface MUST make finding available books simple, fast, and clear. Screens that expose book
discovery MUST prioritize search, filters, availability status, and readable results over decorative
content. Web design work MUST respect the rules in `apartadoDIseñoGraficoBlocIA.md`; if that file
has no applicable rules, the phase output MUST explicitly state that no project-specific visual
rules were available. Rationale: usability is a core requirement for a library system.

### VIII. Phase Discipline
During specification, clarification, checklist, planning, and task-generation phases, contributors
MUST create or update only the documents required by that phase and MUST NOT implement application
code. Implementation is allowed only when executing approved tasks. Rationale: the project teaches
SDD discipline, and premature coding breaks the workflow.

## Architectural Standards

The backend API contract MUST stay synchronized with implementation. Every added or changed
endpoint MUST be documented in Swagger/OpenAPI and verified with curl or an equivalent HTTP command
against the actual URL. API verification evidence MUST be recorded with the task or documentation
for the change.

Domain rules MUST be expressed close to the domain objects that enforce them. Application services
coordinate use cases and transactions, infrastructure adapts storage or external systems, and
presentation code translates requests and responses. Cross-layer shortcuts require explicit
justification in the active task documentation.

Frontend work MUST optimize book discovery, availability clarity, and common user workflows.
Design choices MUST follow `apartadoDIseñoGraficoBlocIA.md` when it contains applicable rules.

## Development Workflow

Work MUST proceed through Spec Kit phases in order: specify, clarify when needed, checklist, plan,
tasks, then implementation. Phase outputs are documentation artifacts; they do not authorize code
changes until implementation tasks exist.

Each task that changes behavior MUST include its verification path before the next task begins.
Verification MAY include unit tests, integration tests, API curl checks, frontend checks, or other
commands appropriate to the changed layer. Failed checks MUST be fixed or explicitly documented as
known blockers before advancing.

Reviews MUST verify traceability to requirements, layer boundaries, test coverage for business
rules, Swagger/OpenAPI updates for endpoints, curl evidence for API changes, scalable availability
search behavior, and compliance with applicable web design rules.

## Governance

This constitution supersedes informal project practices. Spec Kit artifacts, implementation plans,
tasks, code reviews, and documentation MUST comply with these principles. When an artifact conflicts
with this constitution, the constitution governs unless it is amended first.

Amendments MUST be proposed as explicit documentation changes to this file. Each amendment MUST
include the reason for the change, its impact on existing Spec Kit artifacts, and any migration work
needed to bring active plans or tasks into compliance. Approval is required before dependent work
uses the new rule.

Versioning follows semantic versioning. MAJOR versions remove or redefine principles in a backward
incompatible way. MINOR versions add principles, sections, or materially expanded guidance. PATCH
versions clarify wording, fix typos, or make non-semantic refinements.

Compliance review is required at the end of each Spec Kit phase and before merging implementation
work. Reviewers MUST check this constitution against the changed artifacts or code and document any
exception, blocker, or required amendment.

**Version**: 1.0.0 | **Ratified**: 2026-09-20 | **Last Amended**: 2026-09-20
