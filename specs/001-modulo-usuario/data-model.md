# Data Model: Modulo de Usuario

## User

Represents a person who can access the system.

### Fields

- `mail`: unique primary identity for the account.
- `passwordStatus`: whether the account has a password credential configured.
- `age`: required positive age value.
- `profession`: required user profession text.
- `displayName`: optional name provided by Google or user profile data.
- `loginProviderStatus`: indicates whether the account uses password, Google, or both.
- `technicalProfileStatus`: summary of whether provider tokens are configured.
- `createdAt`: account creation timestamp.
- `updatedAt`: last profile update timestamp.

### Validation Rules

- `mail` must be present, valid, and unique.
- `age` must be present and positive.
- `profession` must be present before registration completes.
- Profile updates must validate every changed value before saving.
- Sensitive or protected fields require their own validation flow before changes are accepted.

### Relationships

- One User may have zero or more External Login Links.
- One User may have zero or more Provider Tokens.

## Password Credential

Represents the user's mail-and-contrasenia login capability.

### Fields

- `userMail`: owner account identity.
- `passwordHash`: non-displayable password verifier.
- `createdAt`: credential creation timestamp.
- `updatedAt`: last credential update timestamp.

### Validation Rules

- Password must have at least 10 characters.
- Password must include at least one letter, one number, and one special character.
- Password must not obviously reuse the user's mail.
- Full password values must never be displayed after submission.
- Repeated failed login attempts must not create an account lockout state by themselves.

### State Transitions

- `missing` -> `configured`: user completes valid registration or password setup.
- `configured` -> `configured`: user changes password through a valid update flow.
- Invalid login attempt: no credential state transition and no account lockout by this feature.

## External Login Link

Represents the relationship between a User and a Google identity.

### Fields

- `userMail`: owner account identity.
- `provider`: external identity provider; current feature uses Google.
- `externalSubject`: provider-specific user identity.
- `providedMail`: mail returned by the provider.
- `providedDisplayName`: optional display name returned by the provider.
- `createdAt`: link creation timestamp.
- `lastUsedAt`: last successful login timestamp.

### Validation Rules

- A Google identity may be linked to only one User.
- A Google login using an existing account mail must link to or authenticate the matching User, not create a duplicate account.
- Missing required User fields from Google must be completed by the user before account completion.

### State Transitions

- `unlinked` -> `pendingCompletion`: Google identity accepted but required fields are missing.
- `pendingCompletion` -> `linked`: missing required fields are completed.
- `unlinked` -> `linked`: Google identity accepted and all required fields are available.

## AI Provider

Represents a provider that can offer AI models to users.

### Fields

- `providerId`: stable provider identifier.
- `name`: display name.
- `status`: available, unavailable, or deprecated.
- `description`: optional provider description.

### Validation Rules

- Provider name must be visible to users.
- Unavailable providers must not accept new token configuration unless explicitly re-enabled.

### Relationships

- One AI Provider has zero or more AI Models.
- One AI Provider has zero or more Provider Tokens owned by different Users.

## AI Model

Represents a model available through an AI Provider.

### Fields

- `modelId`: stable model identifier.
- `providerId`: owning provider identifier.
- `displayName`: model name shown to users.
- `availabilityStatus`: available, unavailable, or deprecated.
- `capabilities`: optional user-facing capability labels.

### Validation Rules

- Every model must belong to a provider.
- Deprecated or unavailable models must remain visible only when useful for explaining existing configuration.

## Provider Token

Represents a user-owned credential for one AI Provider.

### Fields

- `tokenId`: stable token record identity.
- `userMail`: owner account identity.
- `providerId`: provider this token belongs to.
- `maskedTokenLabel`: non-secret display label.
- `status`: not configured, configured, invalid, or requires attention.
- `createdAt`: token creation timestamp.
- `updatedAt`: last token update timestamp.
- `lastValidatedAt`: last validation timestamp, if validation has run.

### Validation Rules

- A token must belong to exactly one User and one AI Provider.
- A User may have at most one active token per provider.
- Full token values must never be returned for display after save.
- Provider token status must be visible without exposing the token secret.

### State Transitions

- `not configured` -> `configured`: user saves a token accepted for the selected provider.
- `configured` -> `configured`: user replaces a token for the same provider.
- `configured` -> `invalid`: provider/token validation later fails.
- `invalid` -> `configured`: user replaces or fixes the token.
- `configured` -> `not configured`: user removes the token.
- `requires attention` -> `configured`: user resolves the provider-specific issue.
