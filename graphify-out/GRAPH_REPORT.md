# Graph Report - BlocIA  (2026-10-26)

## Corpus Check
- 353 files · ~632,950 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 31 file(s) not represented in the graph (top: .css 12, (none) 7, .example 5)

## Summary
- 2262 nodes · 5595 edges · 150 communities (106 shown, 44 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 611 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2b51e7f7`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- deploy_dokploy.py
- Icon
- pytest
- useChatController.ts
- router.tsx
- PerfilTecnico.tsx
- User
- postgres_repositories.py
- AIProviderRepository
- test_inference_service.py
- conftest.py
- local_models.py
- test_chat_flow.py
- ai_responder.py
- list_available_models.py
- auth.ts
- dependencies.py
- create_app
- test_google_oauth_security.py
- UserRepositoryImpl
- Workspace.tsx
- chat_routes.py
- test_inference_client.py
- json
- common.ps1
- send_message.py
- EmailVerificationError
- train.py
- ChatRepository
- auth_routes.py
- User Module Implementation Plan
- ChatSettings
- test_google_account_connection.py
- schema.postgresql.sql
- Database
- Dokploy Deployment Guide
- ProviderToken
- google_ai_routes.py
- package.json
- UserRepository
- ProviderOAuthRepository
- @playwright/test
- google_ai_connection.py
- compilerOptions
- Correccion Grafica Tasks
- technical_profile_routes.py
- test_smtp_email_sender.py
- UsageEvent
- AbuseLimitRepository
- Landing.tsx
- Workspace
- GoogleConnectionError
- test_google_callback_contract.py
- verify-mockup.cjs
- re
- UsageAnalyticsRepository
- test_usage_analytics.py
- dependencies
- schema.sql
- run.sh
- Register.tsx
- smtp
- BloqIA Desktop Chat Empty State Screen
- smoke_containers.sh
- Public Login and Registration Routes
- Eight-Color Adobe Palette
- Prompts para tres videos de BloqIA
- GoogleDouble
- devDependencies
- profile_routes.py
- BloqIA Desktop Classification Conversation Screen
- BloqIA Mobile Landing Page
- BloqIA Mobile Registration Screen
- BloqIA Desktop Landing Page Mockup
- BloqIA Desktop Landing Page Mockup
- inference_main.py
- mobile-responsive.spec.ts
- Google AI External Provider Connection
- BloqIA Desktop Registration Screen
- BloqIA Mobile Login Screen
- BloqIA Graphic Design Guidance
- InMemoryUserStore
- hashlib
- review-mockup-fixes.cjs
- Desktop Profile Screen Mockup
- Mobile Chat Screen Mockup
- Mobile Google Callback Mockup
- Mobile Conversation History Mockup
- Mobile Profile Screen Mockup
- FakeClassifier
- LocalTextModel
- Quiet Study Architectural Photograph
- setup.ts
- create_app
- scripts
- test_generation_starts_after_classification_and_progress_is_private
- Desktop Landing Page Hero Screenshot
- Mobile Landing Page Hero Screenshot
- Mobile Providers and Models Screen Screenshot
- deploy_dokploy_applications.py
- Editorial Thinking Desk Image
- Spec Kit Analyze Skill
- Desktop Google Profile Completion Mockup Screenshot
- Desktop Landing Page Scroll Screenshot
- Desktop Activity Dashboard Screenshot
- Mobile Activity Dashboard Screenshot
- Spec Kit Full SDD Cycle Workflow
- ExternalLoginLink
- inference-entrypoint.sh
- os
- BloqIA Ultramarine Geometric Logo Mark
- 001_user_module.sql
- correccion-grafica-responsive.spec.ts
- correccion-grafica-visual.spec.ts
- create_deployment_network.sh
- Quiet Study Image Prompt
- service-worker.js
- visual-prohibitions.spec.ts
- visual-responsive.spec.ts
- Spec Kit Checklist Skill
- Spec Kit Constitution Skill
- US1 Login Curl Evidence
- US3 Profile Curl Evidence
- BloqIA Application Entry
- BloqIA Design Prototype Entry
- Lora SIL Open Font License
- Manrope SIL Open Font License
- Spec Kit Clarify Skill
- Spec Kit Converge Skill
- Spec Kit Implement Skill
- Spec Kit Tasks to Issues Skill
- bloc-ia-user-module
- Authenticated Session JWT States
- Protected Route Guard
- Public and Protected Route Access Rule
- email_verifier
- verify_nginx_dns.py
- useSheetMotion

## God Nodes (most connected - your core abstractions)
1. `Database` - 65 edges
2. `User` - 63 edges
3. `Icon()` - 51 edges
4. `EmailVerificationError` - 38 edges
5. `GoogleConnectionError` - 35 edges
6. `AIModel` - 35 edges
7. `UserRepository` - 35 edges
8. `react` - 35 edges
9. `apiRequest()` - 32 edges
10. `ProviderToken` - 30 edges

## Surprising Connections (you probably didn't know these)
- `mismatched_network()` --calls--> `load_mapping()`  [INFERRED]
  back/tests/unit/test_deployment_validation.py → scripts/validate_deployment.py
- `Google Gemini Account OAuth Connection` --semantically_similar_to--> `Google OAuth State and Callback Flow`  [INFERRED] [semantically similar]
  docs/provider-account-connections.md → back/GOOGLE_OAUTH_SETUP.md
- `test_models_warm_before_requests_and_transport_closes_on_shutdown()` --indirect_call--> `main()`  [INFERRED]
  back/tests/unit/test_chat_startup.py → front/tests/docker/verify_nginx_dns.py
- `test_unavailable_classifier_does_not_prevent_startup_or_log_user_text()` --indirect_call--> `main()`  [INFERRED]
  back/tests/unit/test_chat_startup.py → front/tests/docker/verify_nginx_dns.py
- `Spec Kit Plan Skill` --references--> `Implementation Plan Template`  [INFERRED]
  .github/skills/speckit-plan/SKILL.md → .specify/templates/plan-template.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Public Entry and JWT-Gated Private Routes** — specs_002_correccion_grafica_spec, specs_002_correccion_grafica_contracts_route_access, specs_002_correccion_grafica_data_model_protected_route_guard [EXTRACTED 1.00]
- **Route Access Validation** — specs_002_correccion_grafica_evidence_frontend_tests, specs_002_correccion_grafica_evidence_playwright_tests, specs_002_correccion_grafica_evidence_story_acceptance [EXTRACTED 1.00]
- **Quiet Architectural Study Scene** — front_public_mockup_images_quiet_study_contemporary_concrete_study, front_public_mockup_images_quiet_study_tall_window_and_diagonal_sunlight, front_public_mockup_images_quiet_study_simple_study_desk_and_books, front_public_mockup_images_quiet_study_ultramarine_blue_chair, front_public_mockup_images_quiet_study_soft_lime_book [EXTRACTED 1.00]
- **Desktop Chat Empty State Composition** — impeccable_review_desktop_chat_desktop_chat_screen, impeccable_review_desktop_chat_suggested_prompts, impeccable_review_desktop_chat_prompt_composer [EXTRACTED 1.00]
- **Classification Result and Review Details** — impeccable_review_desktop_classification_personal_decision_category, impeccable_review_desktop_classification_low_confidence_status, impeccable_review_desktop_classification_example_classification_confidence_values, impeccable_review_desktop_classification_human_review_required [EXTRACTED 1.00]
- **Provider, Credential, Status, and Model Configuration** — impeccable_review_desktop_providers_google_ai_external_connection, impeccable_review_desktop_providers_masked_api_key, impeccable_review_desktop_providers_demo_connection_status, impeccable_review_desktop_providers_example_model_catalog [EXTRACTED 1.00]
- **Registration Form and Validation** — impeccable_review_desktop_register_email_password_fields, impeccable_review_desktop_register_age_profession_fields, impeccable_review_desktop_register_email_validation_error, impeccable_review_desktop_register_create_demo_account_action [EXTRACTED 1.00]
- **Mobile Landing Page Story Sequence** — impeccable_review_mobile_mobile_hero_value_proposition, impeccable_review_mobile_mobile_product_capability_sections, impeccable_review_mobile_mobile_product_interface_previews, impeccable_review_mobile_mobile_faq_section, impeccable_review_mobile_mobile_final_call_to_action_and_footer [EXTRACTED 1.00]
- **Login Methods, Credentials, and Demo Entry** — impeccable_review_mobile_login_google_demo_login, impeccable_review_mobile_login_email_password_fields, impeccable_review_mobile_login_primary_demo_login_action [EXTRACTED 1.00]
- **Mobile Registration Form and Actions** — impeccable_review_mobile_register_email_password_fields, impeccable_review_mobile_register_age_profession_fields, impeccable_review_mobile_register_create_demo_account_action [EXTRACTED 1.00]
- **Spec Kit Feature Workflow** — github_skills_speckit_specify_skill, github_skills_speckit_clarify_skill, github_skills_speckit_checklist_skill, github_skills_speckit_plan_skill, github_skills_speckit_tasks_skill, github_skills_speckit_implement_skill [EXTRACTED 1.00]
- **Four user module stories** — specs_001_modulo_usuario_spec_login_registration_profile_technical_profile_stories, specs_001_modulo_usuario_contracts_openapi_user_module_api_contract, specs_001_modulo_usuario_quickstart_user_module_quickstart [INFERRED 0.85]

## Communities (150 total, 44 thin omitted)

### Community 0 - "deploy_dokploy.py"
Cohesion: 0.13
Nodes (13): Configuration, deploy(), deploy_services(), DeploymentError, DeploymentPlan, DokployClient, environment_value(), https_url() (+5 more)

### Community 1 - "Icon"
Cohesion: 0.11
Nodes (31): MeterZone, MobileSheet(), useMobileViewport(), SheetMotion, Notice(), ChatComposer(), ChatComposerInfo(), chatPrivacyDescription (+23 more)

### Community 2 - "pytest"
Cohesion: 0.05
Nodes (37): test_backend_resources_reject_public_exposure_and_missing_persistence_config(), test_resources_with_different_network_names_are_rejected(), mismatched_network(), test_runtime_version_cannot_disagree_with_the_published_image(), test_separate_resource_rejects_multiple_services_and_cross_resource_dependencies(), test_separate_resource_rejects_the_wrong_role(), test_separate_resources_reject_mutable_release_tags_and_project_scoped_networks(), environment() (+29 more)

### Community 3 - "useChatController.ts"
Cohesion: 0.06
Nodes (60): ChatProgress, ChatStatus, Classification, Conversation, ConversationDetail, createConversation(), deleteConversation(), getChatStatus() (+52 more)

### Community 4 - "router.tsx"
Cohesion: 0.09
Nodes (44): logout(), startGoogleLogin(), applicationPaths, handleInternalLink(), navigateTo(), base64UrlDecode(), base64UrlEncode(), canAccessRoute() (+36 more)

### Community 5 - "PerfilTecnico.tsx"
Cohesion: 0.09
Nodes (47): apiRequest(), ApiRequestError, getProfile(), updateProfile(), disconnectGoogle(), getGoogleConnection(), getGoogleProjects(), GoogleProject (+39 more)

### Community 6 - "User"
Cohesion: 0.10
Nodes (8): CompleteGoogleRegistration, DuplicateMailError, PasswordCredentialRepository, UserRepository, _now(), User, test_profile_update_validates_changed_values(), test_user_required_fields_validation()

### Community 7 - "postgres_repositories.py"
Cohesion: 0.11
Nodes (16): AIModel, AIProvider, LoginProviderStatus, ModelAvailabilityStatus, ProviderStatus, ProviderTokenStatusValue, TechnicalProfileStatus, AIModelRepositoryImpl (+8 more)

### Community 8 - "AIProviderRepository"
Cohesion: 0.27
Nodes (3): ListTechnicalProviders, AIModelRepository, AIProviderRepository

### Community 9 - "test_inference_service.py"
Cohesion: 0.16
Nodes (7): test_inference_operations_require_configured_private_token(), test_inference_service_instances_are_local_even_with_remote_url(), test_invalid_requests_do_not_echo_user_input_or_invoke_models(), test_model_failures_are_sanitized_without_logging_prompts(), fail(), test_prepare_downloads_only_requested_models_and_skips_complete_pinned_installations(), test_prepare_preserves_unverified_or_different_model_revision_until_explicit_replacement()

### Community 10 - "conftest.py"
Cohesion: 0.15
Nodes (11): _now(), PasswordCredential, PasswordPolicy, access_token(), clean_store(), seeded_user(), verified_email(), test_password_hash_is_non_displayable_and_invalid_attempt_does_not_lock() (+3 more)

### Community 11 - "local_models.py"
Cohesion: 0.13
Nodes (12): local_text_model(), local_free_models(), inference_client(), inference_url(), RemoteTextModel, _file_version(), local_models(), LocalModels (+4 more)

### Community 12 - "test_chat_flow.py"
Cohesion: 0.12
Nodes (12): classification(), test_chat_passes_current_profile_and_conversation_to_selected_model(), test_chat_persists_classification_and_idempotent_retries(), test_classifier_review_state_fails_closed_and_counts_as_personal(), test_google_global_key_does_not_advertise_model_from_legacy_credential(), test_google_rejects_unverified_or_zero_quota_model_before_processing(), test_personal_decision_does_not_call_any_answer_model(), unexpected() (+4 more)

### Community 13 - "ai_responder.py"
Cohesion: 0.11
Nodes (16): AIResponder, AIResponseUnavailableError, _read_provider_errors(), is_free_openrouter_model_id(), client(), test_chat_google_authorization_failure_explains_account_recovery_without_echoing_provider_body(), test_all_external_model_requests_include_the_deep_explanation_instruction(), test_connection_timeouts_remain_retryable_without_echoing_secrets() (+8 more)

### Community 14 - "list_available_models.py"
Cohesion: 0.08
Nodes (24): default_provider_token(), google_headers(), AnthropicModelsClient, AvailableModelList, _get_json(), GoogleModelsClient, GroqModelsClient, ListAvailableModels (+16 more)

### Community 15 - "auth.ts"
Cohesion: 0.12
Nodes (18): completeGoogleRegistration(), consumeGoogleSession(), forgetSession(), notifyAccountChange(), register(), rememberSession(), restoreSession(), subscribeToAccountChanges() (+10 more)

### Community 16 - "dependencies.py"
Cohesion: 0.06
Nodes (20): DatabaseRow, get_database(), ExternalLinkRepository, hydrate(), ModelRepository, ProviderRepository, Repository, serialize() (+12 more)

### Community 17 - "create_app"
Cohesion: 0.13
Nodes (13): create_application(), RuntimeSettings, create_app(), health(), ready(), test_models_warm_before_requests_and_transport_closes_on_shutdown(), test_unavailable_classifier_does_not_prevent_startup_or_log_user_text(), production_environment() (+5 more)

### Community 18 - "test_google_oauth_security.py"
Cohesion: 0.10
Nodes (14): verify_google_id_token(), signed_identity(), token(), test_explicit_callback_is_preserved_and_local_default_still_works(), test_google_id_token_forged_signature_is_rejected(), test_google_id_token_invalid_claims_are_rejected(), test_google_id_token_is_rejected_at_expiration_boundary(), test_google_id_token_signature_is_verified_with_bounded_request() (+6 more)

### Community 19 - "UserRepositoryImpl"
Cohesion: 0.14
Nodes (9): InvalidCredentialsError, LoginWithPassword, is_valid_email(), flush(), PasswordCredentialRepositoryImpl, UserRepositoryImpl, test_production_cookie_mutation_requires_origin(), test_login_success_and_safe_failure() (+1 more)

### Community 20 - "Workspace.tsx"
Cohesion: 0.11
Nodes (16): Activity, answers, Category, categoryNames, DemoChat, DemoClassification(), DemoMessage, navItems (+8 more)

### Community 21 - "chat_routes.py"
Cohesion: 0.10
Nodes (20): default_google_key(), default_google_models(), save_default_google_key(), default_openrouter_key(), remote_free_models(), save_default_openrouter_key(), ConversationNotFoundError, create_conversation() (+12 more)

### Community 22 - "test_inference_client.py"
Cohesion: 0.15
Nodes (10): generation_timeout_seconds(), InferenceClient, InferenceUnavailableError, ModelUnavailableError, test_invalid_generation_timeout_uses_default(), test_remote_client_rejects_credential_bearing_or_unsupported_urls(), test_remote_failures_are_safe_and_map_to_existing_domain_errors(), test_remote_local_inventory_does_not_check_models_on_api_machine() (+2 more)

### Community 23 - "json"
Cohesion: 0.17
Nodes (14): google_registration_secret(), registration_token(), _base64_url_decode(), _base64_url_encode(), create_access_token(), parse_access_token(), parse_access_token_claims(), _token_secret() (+6 more)

### Community 24 - "common.ps1"
Cohesion: 0.17
Nodes (17): Find-SpecifyRoot(), Format-SpecKitCommand(), Get-CurrentBranch(), Get-FeaturePathsEnv(), Get-InvokeSeparator(), Get-NormalizedPriority(), Get-Python3Command(), Get-RepoRoot() (+9 more)

### Community 25 - "send_message.py"
Cohesion: 0.10
Nodes (10): build_model_context(), _short(), _normalize(), predefined_response(), redact_personal_data(), guarded_classification(), send_chat_message(), UsageBlockedError (+2 more)

### Community 26 - "EmailVerificationError"
Cohesion: 0.11
Nodes (21): EmailVerification, EmailVerificationError, VerifyEmail, EmailVerificationRepository, email_verification(), headers(), test_code_is_bound_to_account_and_sender_failure_does_not_verify(), send_verification() (+13 more)

### Community 27 - "train.py"
Cohesion: 0.22
Nodes (6): generate_examples(), duplicate_groups(), extract_examples(), main(), normalized(), test_training_input_rejects_conflicting_labels()

### Community 28 - "ChatRepository"
Cohesion: 0.16
Nodes (8): ChatRepository, conversation(), now(), TurnConflictError, chat_repository(), test_recent_context_is_bounded_to_answered_turns_and_owned_conversation(), test_recent_personal_history_is_enforced_even_before_a_saved_lock(), test_three_hours_of_recorded_ai_time_create_a_24_hour_lock()

### Community 29 - "auth_routes.py"
Cohesion: 0.18
Nodes (15): authenticated_response(), complete_google_registration(), decode_result(), google_session(), login(), logout(), register(), session() (+7 more)

### Community 30 - "User Module Implementation Plan"
Cohesion: 0.13
Nodes (19): Specification Quality Checklist, User Module OpenAPI Contract, External Login Link, Provider Token, User Module Data Model, Backend Test Evidence, Frontend Test Evidence, PWA Private Response Cache Review (+11 more)

### Community 31 - "ChatSettings"
Cohesion: 0.20
Nodes (4): ChatSettings, ClassifierSettings, classifier(), test_generation_limit_accepts_maximum_question_with_full_profile_and_history()

### Community 32 - "test_google_account_connection.py"
Cohesion: 0.14
Nodes (12): GoogleAIConfig, authorize(), test_callback_uses_browser_session_and_does_not_put_tokens_in_redirect(), test_disconnect_removes_local_tokens_even_if_google_is_unreachable(), test_empty_redirect_variable_uses_public_frontend_callback(), test_expired_transaction_and_replay_are_rejected(), test_google_errors_are_actionable_and_do_not_echo_secrets(), test_invalid_authorization_never_saves_account() (+4 more)

### Community 33 - "schema.postgresql.sql"
Cohesion: 0.13
Nodes (28): abuse_counters, abuse_counters_by_window, active_chat_work, app_meta, chat_turns, conversations, conversations_by_user, credentials (+20 more)

### Community 34 - "Database"
Cohesion: 0.15
Nodes (8): Database, main(), connection(), postgres_email_account(), test_corrupt_legacy_data_is_not_overwritten(), test_concurrent_consumers_cannot_exceed_budget(), test_upgrade_seeds_lifetime_account_budget_from_existing_accounts(), usage()

### Community 35 - "Dokploy Deployment Guide"
Cohesion: 0.07
Nodes (28): User Module API Contract, Chat Configuration, Question Classification Categories, Question Classifier Configuration, Google OAuth Login Configuration, Google OAuth State and Callback Flow, Classifier Verification Report, Question Classifier Configuration Guidance (+20 more)

### Community 36 - "ProviderToken"
Cohesion: 0.08
Nodes (10): RemoveProviderToken, mask_token(), _now(), ProviderToken, ProviderTokenRepository, ProviderTokenRepositoryImpl, test_global_default_provider_token_is_used_and_personal_token_wins(), test_remote_default_uses_server_key_and_personal_key_takes_priority() (+2 more)

### Community 37 - "google_ai_routes.py"
Cohesion: 0.24
Nodes (10): callback(), disconnect(), failure(), projects(), ProjectSelection, same_origin(), select_project(), start() (+2 more)

### Community 38 - "package.json"
Cohesion: 0.12
Nodes (17): name, private, type, version, MarkdownContent(), jsdom, katex, react-markdown (+9 more)

### Community 39 - "UserRepository"
Cohesion: 0.14
Nodes (19): RegisterUser, SaveProviderToken, UpdateProfile, CredentialRepository, TokenRepository, UserRepository, token_repo(), main() (+11 more)

### Community 40 - "ProviderOAuthRepository"
Cohesion: 0.24
Nodes (5): credential_cipher(), digest(), ProviderOAuthRepository, google_ai_connection(), test_postgres_oauth_tokens_are_encrypted_and_refresh_serializes_across_workers()

### Community 43 - "compilerOptions"
Cohesion: 0.11
Nodes (17): compilerOptions, allowJs, allowSyntheticDefaultImports, esModuleInterop, forceConsistentCasingInFileNames, isolatedModules, jsx, lib (+9 more)

### Community 44 - "Correccion Grafica Tasks"
Cohesion: 0.16
Nodes (18): User Module Visual QA Evidence, Correccion Grafica Requirements Checklist, Correccion Grafica Route Access Contract, Correccion Grafica Data Model, Frontend Build Evidence, Frontend Test Evidence, Playwright Evidence, PWA Cache Review Evidence (+10 more)

### Community 45 - "technical_profile_routes.py"
Cohesion: 0.20
Nodes (12): ProviderUnavailableError, token_status(), confirm_email_verification(), email_verification_status(), list_providers(), request_email_verification(), save_token(), AIModelSchema (+4 more)

### Community 46 - "test_smtp_email_sender.py"
Cohesion: 0.18
Nodes (7): SmtpEmailSender, test_default_transport_is_starttls_and_custom_port_is_respected(), test_delivery_uses_verified_tls_before_authentication_and_does_not_log_secrets(), test_incomplete_configuration_fails_before_any_connection(), test_invalid_configuration_fails_closed_without_network(), test_recipient_header_injection_fails_before_connection(), test_transport_failure_is_sanitized_and_never_falls_back_to_plaintext()

### Community 47 - "UsageEvent"
Cohesion: 0.18
Nodes (6): GetUsageSummary, UsageEventRepository, now_utc(), UsageEvent, UsageEventRepositoryImpl, remove_token()

### Community 48 - "AbuseLimitRepository"
Cohesion: 0.19
Nodes (5): AbuseLimitRepository, configured_limit(), InMemoryAbuseLimitRepository, abuse_limits(), test_fixed_window_budget_is_shared_across_database_instances_and_resets()

### Community 49 - "Landing.tsx"
Cohesion: 0.13
Nodes (20): cancelViewChange(), changeView(), motionAllowed(), motionTiming(), trackMotionPreferences(), TransitionDocument, ViewChange, AnimatedDisclosure() (+12 more)

### Community 50 - "Workspace"
Cohesion: 0.33
Nodes (12): timeNow(), validPassword(), Workspace(), addActivity(), later(), navigate(), newChat(), openChat() (+4 more)

### Community 51 - "GoogleConnectionError"
Cohesion: 0.26
Nodes (4): GoogleConnectionError, GoogleAIConnection, test_google_account_uses_personal_project_and_never_falls_back_after_revocation(), revoked()

### Community 52 - "test_google_callback_contract.py"
Cohesion: 0.17
Nodes (6): encode_result(), test_google_callback_rejects_invalid_state_before_contacting_google(), test_google_result_cannot_be_used_as_transaction_cookie(), test_google_result_expiration_is_checked_on_server(), test_google_start_binds_identity_nonce_and_clears_previous_result(), test_signed_google_result_rejects_tampering()

### Community 53 - "verify-mockup.cjs"
Cohesion: 0.17
Nodes (7): databaseDirectory, assert, { chromium }, { expect }, fs, out, path

### Community 54 - "re"
Cohesion: 0.17
Nodes (11): _load(), load_dev_environment(), test_development_file_loads_values_without_overriding_process_environment(), test_production_does_not_load_development_file(), load_mapping(), main(), require(), validate_compose() (+3 more)

### Community 55 - "UsageAnalyticsRepository"
Cohesion: 0.24
Nodes (3): _iso(), UsageAnalyticsRepository, test_three_personal_questions_lock_chat_and_dashboard_reports_reasons()

### Community 56 - "test_usage_analytics.py"
Cohesion: 0.29
Nodes (10): complete_turn(), test_increasing_pause_does_not_extend_an_existing_lock(), test_invalid_or_missing_lock_duration_uses_default(), test_personal_allowance_and_configured_lock_duration(), test_rechecking_limits_keeps_original_expiry_and_combines_reasons(), test_reducing_daily_pause_releases_old_lock_without_erasing_history(), test_short_expired_lock_refreshes_allowance_and_preserves_activity(), test_shorter_configuration_shortens_existing_lock_from_original_start() (+2 more)

### Community 57 - "dependencies"
Cohesion: 0.17
Nodes (12): dependencies, katex, react, react-dom, react-markdown, rehype-katex, remark-gfm, remark-math (+4 more)

### Community 58 - "schema.sql"
Cohesion: 0.14
Nodes (27): abuse_counters, abuse_counters_by_window, active_chat_work, app_meta, chat_turns, conversations, conversations_by_user, credentials (+19 more)

### Community 59 - "run.sh"
Cohesion: 0.32
Nodes (11): BLOCIA_API_URL, fail(), find_python(), FRONTEND_URL, GOOGLE_REDIRECT_URI, log(), port_is_open(), process_matches() (+3 more)

### Community 60 - "Register.tsx"
Cohesion: 0.16
Nodes (13): login(), AuthAction, authErrorMessage(), AuthLayout(), PasswordField(), ProfessionField(), ProfessionFieldProps, professions (+5 more)

### Community 61 - "smtp"
Cohesion: 0.31
Nodes (10): smtp(), ehlo(), __enter__(), event(), __exit__(), factory(), connect(), login() (+2 more)

### Community 62 - "BloqIA Desktop Chat Empty State Screen"
Cohesion: 0.18
Nodes (11): BloqIA Brand in Sidebar, BloqIA Desktop Chat Empty State Screen, Local Classification Status, Model Selector, New Conversation Action, Profile and Recent Context Notice, Prompt Composer, Recent Conversation Links (+3 more)

### Community 63 - "smoke_containers.sh"
Cohesion: 0.36
Nodes (10): cleanup(), container_ip(), finish(), frontend_ready(), is_owned(), release_matches(), smoke_containers.sh script, stack_ready() (+2 more)

### Community 64 - "Public Login and Registration Routes"
Cohesion: 0.20
Nodes (11): US1 Public Home Evidence, Home Login Action, Public Home Route, BloqIA Block Chassis, US2 Public Authentication Evidence, Public Login and Registration Routes, US3 Protected Routes Evidence, Authentication Guard Screen (+3 more)

### Community 65 - "Eight-Color Adobe Palette"
Cohesion: 0.20
Nodes (10): Deep Charcoal #17212B, Cobalt Blue #1C489B, Teal #3F8585, Slate Gray #66727A, Muted Red #D95C5C, Coral #E98973, Warm Cream #FFF6DB, White #FFFFFF (+2 more)

### Community 66 - "Prompts para tres videos de BloqIA"
Cohesion: 0.09
Nodes (19): BloqIA · tres videos para comunicar la app, Investigación y dirección, Criterios de selección, Herramientas de IA para video publicitario, Qué recomiendo para BloqIA, Referencias de lenguaje publicitario, Capturas reales de la app, Hojas de referencia de campaña (+11 more)

### Community 68 - "devDependencies"
Cohesion: 0.20
Nodes (10): devDependencies, jsdom, @playwright/test, @testing-library/jest-dom, @testing-library/react, @testing-library/user-event, @types/react, @types/react-dom (+2 more)

### Community 69 - "profile_routes.py"
Cohesion: 0.19
Nodes (8): GetProfile, ProfileNotFoundError, validation_error_response(), get_profile(), update_profile(), ProfileUpdateRequest, UserProfile, user_profile()

### Community 70 - "BloqIA Desktop Classification Conversation Screen"
Cohesion: 0.22
Nodes (10): BloqIA Desktop Classification Conversation Screen, Example Classification Confidence Values, Human Review Required, Local Classification Notice, Local Processing Disclosure, Low Confidence Status, Personal Decision Category, Predefined Demo Response (+2 more)

### Community 71 - "BloqIA Mobile Landing Page"
Cohesion: 0.22
Nodes (9): Compact Brand Header and Navigation, Conversation Workflow Overview, Frequently Asked Questions Section, Final Call to Action and Footer, Hero Value Proposition and Primary CTA, BloqIA Mobile Landing Page, Understand, Organize, and Explore Capabilities, Product Interface Previews (+1 more)

### Community 72 - "BloqIA Mobile Registration Screen"
Cohesion: 0.22
Nodes (10): Age and Profession Fields, Compact Brand Introduction Panel, Create Demo Account Action, Demo Mode and Fictional Data Notice, Email and Password Registration Fields, Ephemeral Demo Data Disclosure, Existing Account Login Link, Google Demo Registration Action (+2 more)

### Community 73 - "BloqIA Desktop Landing Page Mockup"
Cohesion: 0.28
Nodes (8): Ask Classify Explore Narrative, Chat Classification Example, BloqIA Desktop Landing Page Mockup, Getting Started FAQ, Landing Page Conversion Actions, Perspective Focused Hero Section, Question Understanding Pathways, Workspace Capabilities Overview

### Community 74 - "BloqIA Desktop Landing Page Mockup"
Cohesion: 0.28
Nodes (8): Ask Classify Explore Narrative, Chat Classification Example, BloqIA Desktop Landing Page Mockup, Getting Started FAQ, Landing Page Conversion Actions, Perspective Focused Hero Section, Question Understanding Pathways, Workspace Capabilities Overview

### Community 75 - "inference_main.py"
Cohesion: 0.17
Nodes (6): close_inference_client(), application_lifespan(), ClassifyRequest, GenerateRequest, WarmupRequest, test_shared_client_closes_without_breaking_cached_factory_references()

### Community 76 - "mobile-responsive.spec.ts"
Cohesion: 0.22
Nodes (6): classification, conversation, limits, messages, model, profile

### Community 77 - "Google AI External Provider Connection"
Cohesion: 0.25
Nodes (9): Demo Connection Status, Demo Credential Storage and Connection Disclosure, Example Gemini Model Catalog, Google AI External Provider Connection, Local Qwen Model Option, Masked API Key Display, BloqIA Desktop Providers and Models Screen, Provider Management Actions (+1 more)

### Community 78 - "BloqIA Desktop Registration Screen"
Cohesion: 0.25
Nodes (9): Age and Profession Fields, Create Demo Account Action, Fictional Demo Data and Session Disclosure, Email and Password Fields, Email Format Validation Error, Existing Account Login Link, Google Demo Registration Action, BloqIA Desktop Registration Screen (+1 more)

### Community 79 - "BloqIA Mobile Login Screen"
Cohesion: 0.25
Nodes (9): Compact Brand Introduction Panel, Demo Mode and Fictional Data Notice, Email and Password Login Fields, Ephemeral Demo Data Disclosure, Google Demo Login Action, BloqIA Mobile Login Screen, Password Requirement Hint, Primary Demo Login Action (+1 more)

### Community 80 - "BloqIA Graphic Design Guidance"
Cohesion: 0.29
Nodes (6): BloqIA Graphic Design Guidance, BloqIA Design System, Contemporary Editorial Notebook Visual Identity, BloqIA Product Definition, BlocIA Library Education System Constitution, Layered Responsibility Boundaries

### Community 82 - "hashlib"
Cohesion: 0.42
Nodes (4): google_quota_models(), snapshot(), test_missing_or_invalid_snapshot_does_not_grant_access(), test_quota_requires_chat_and_all_positive_limits()

### Community 83 - "review-mockup-fixes.cjs"
Cohesion: 0.25
Nodes (6): assert, { chromium }, { expect }, fs, out, path

### Community 84 - "Desktop Profile Screen Mockup"
Cohesion: 0.38
Nodes (6): Account Summary, Demo Profile State, Personal Information Form, Desktop Profile Screen Mockup, Provider Management Link, Workspace Sidebar Navigation

### Community 85 - "Mobile Chat Screen Mockup"
Cohesion: 0.38
Nodes (6): Local Qwen Model Option, Chat Message Composer, Mobile Chat Screen Mockup, Mobile Navigation Header, Model Selector, Suggested Question Categories

### Community 86 - "Mobile Google Callback Mockup"
Cohesion: 0.33
Nodes (6): Age and Profession Fields, Demo Google Account, Email Login Alternative, Google Registration Profile Completion, Mobile Google Callback Mockup, OAuth Cancellation and Error States

### Community 87 - "Mobile Conversation History Mockup"
Cohesion: 0.38
Nodes (6): Conversation History List, Delete Conversation Action, Conversation Last Activity Timestamp, Mobile Conversation History Mockup, New Conversation Action, Resume Conversation with Context

### Community 88 - "Mobile Profile Screen Mockup"
Cohesion: 0.33
Nodes (7): Account Identity Summary, Demo Profile Data, Display Name Field, Mobile Profile Screen Mockup, Personal Information Form, Profession and Age Fields, Save Profile Action

### Community 89 - "FakeClassifier"
Cohesion: 0.19
Nodes (6): FakeClassifier, FakeGenerator, inference(), test_classifier_only_service_disables_qwen_even_when_preload_requested(), test_lifespan_warms_direct_models_and_logs_only_failure_type(), test_production_requires_token_before_serving_requests()

### Community 91 - "Quiet Study Architectural Photograph"
Cohesion: 0.33
Nodes (7): Contemporary Concrete Study Interior, Quiet Contemplative Mood, Quiet Study Architectural Photograph, Simple Desk with Books and Notebook, Soft Lime Book Accent, Tall Window and Diagonal Sunlight, Ultramarine Blue Chair

### Community 94 - "scripts"
Cohesion: 0.33
Nodes (6): scripts, build, dev, test, test:e2e, test:local

### Community 95 - "test_generation_starts_after_classification_and_progress_is_private"
Cohesion: 0.20
Nodes (6): FakeModels, sql_chat(), test_generation_starts_after_classification_and_progress_is_private(), classify(), test_pending_turn_prevents_parallel_personal_usage_in_another_conversation(), classify()

### Community 96 - "Desktop Landing Page Hero Screenshot"
Cohesion: 0.33
Nodes (5): Editorial Example Question, Desktop Landing Page Hero Screenshot, Primary Workspace and Secondary Discovery Actions, Public Navigation and Account Actions, Thinking Desk Editorial Photography

### Community 97 - "Mobile Landing Page Hero Screenshot"
Cohesion: 0.33
Nodes (5): Editorial Example Question, Mobile Landing Page Hero Screenshot, Primary Workspace and Secondary Discovery Actions, Mobile Responsive Header and Menu, Thinking Desk Editorial Photography

### Community 98 - "Mobile Providers and Models Screen Screenshot"
Cohesion: 0.40
Nodes (5): Demonstration API Credential and Disclosure, External AI Provider Connection, Mobile Providers and Models Screen Screenshot, Provider-Specific Model Catalog, Qwen Local Model

### Community 99 - "deploy_dokploy_applications.py"
Cohesion: 0.17
Nodes (8): Configuration, deploy_applications(), DeploymentError, DokployClient, https_origin(), main(), NoRedirects, required()

### Community 100 - "Editorial Thinking Desk Image"
Cohesion: 0.40
Nodes (4): Blue Geometric Blocks, Editorial Thinking Desk Image, Notebook Diagram, Reflective Sketching

### Community 101 - "Spec Kit Analyze Skill"
Cohesion: 0.40
Nodes (5): Spec Kit Analyze Skill, Spec Kit Plan Skill, Spec Kit Specify Skill, Spec Kit Tasks Skill, Implementation Plan Template

### Community 102 - "Desktop Google Profile Completion Mockup Screenshot"
Cohesion: 0.40
Nodes (4): BloqIA Editorial Brand Panel, Google Profile Completion Demonstration, Desktop Google Profile Completion Mockup Screenshot, Two-Column Authentication Layout

### Community 103 - "Desktop Landing Page Scroll Screenshot"
Cohesion: 0.40
Nodes (4): Desktop Landing Page Scroll Screenshot, Personal Decision Conversation Example, Query Classification Context, Workspace and Conversation Tools Preview

### Community 104 - "Desktop Activity Dashboard Screenshot"
Cohesion: 0.40
Nodes (4): Activity Dashboard, Demonstration Activity and Provider Data, Desktop Activity Dashboard Screenshot, Workspace Sidebar Navigation

### Community 105 - "Mobile Activity Dashboard Screenshot"
Cohesion: 0.40
Nodes (4): Demonstration Query and Provider Metrics, Mobile Activity Dashboard Screenshot, Recent Activity Feed, Responsive Activity Dashboard

### Community 107 - "Spec Kit Full SDD Cycle Workflow"
Cohesion: 0.67
Nodes (3): Feature Specification Template, Feature Tasks Template, Spec Kit Full SDD Cycle Workflow

### Community 108 - "ExternalLoginLink"
Cohesion: 0.18
Nodes (5): GoogleAuth, ExternalLoginLink, _now(), ExternalLoginLinkRepository, ExternalLoginLinkRepositoryImpl

### Community 110 - "os"
Cohesion: 0.18
Nodes (7): GoogleCompletionRequired, lock_duration_minutes(), callback_url(), frontend_url(), google_callback(), google_identity(), google_start()

### Community 111 - "BloqIA Ultramarine Geometric Logo Mark"
Cohesion: 0.67
Nodes (3): BloqIA Ultramarine Geometric Logo Mark, Offset Rectangular Tile Pattern, Ultramarine Brand Color #244ADA

### Community 112 - "001_user_module.sql"
Cohesion: 0.52
Nodes (6): ai_models, ai_providers, external_login_links, password_credentials, provider_tokens, users

### Community 148 - "verify_nginx_dns.py"
Cohesion: 0.21
Nodes (9): main(), check_container_health(), docker(), docker_directive(), main(), identity(), start_api(), request() (+1 more)

### Community 152 - "useSheetMotion"
Cohesion: 0.54
Nodes (8): useSheetMotion(), animate(), dismiss(), finish(), paint(), preferenceChanged(), stop(), tick()

## Knowledge Gaps
- **165 isolated node(s):** `bloc-ia-user-module`, `BLOCIA_PRELOAD_LOCAL_CHAT`, `@types/react`, `@types/react-dom`, `jsdom` (+160 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 706 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **44 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `Database`, `ProviderToken`, `profile_routes.py`, `UserRepository`, `postgres_repositories.py`, `test_inference_service.py`, `conftest.py`, `ExternalLoginLink`, `InMemoryUserStore`, `UserRepositoryImpl`, `json`, `test_usage_analytics.py`, `send_message.py`, `EmailVerificationError`, `ChatSettings`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `Database` (e.g. with `LoginProviderStatus` and `ProviderTokenStatusValue`) actually correct?**
  _`Database` has 16 INFERRED edges - model-reasoned connections that need verification._
- **What connects `bloc-ia-user-module`, `BLOCIA_PRELOAD_LOCAL_CHAT`, `@types/react` to the rest of the system?**
  _165 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `deploy_dokploy.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12873563218390804 - nodes in this community are weakly interconnected._
- **Why does `Database` connect `Database` to `test_google_account_connection.py`, `UserRepository`, `postgres_repositories.py`, `ProviderOAuthRepository`, `conftest.py`, `test_chat_flow.py`, `dependencies.py`, `InMemoryUserStore`, `AbuseLimitRepository`, `email_verifier`, `create_app`, `test_usage_analytics.py`, `EmailVerificationError`, `test_generation_starts_after_classification_and_progress_is_private`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Are the 16 inferred relationships involving `User` (e.g. with `build_model_context()` and `CompleteGoogleRegistration`) actually correct?**
  _`User` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Should `Icon` be split into smaller, more focused modules?**
  _Cohesion score 0.10572390572390572 - nodes in this community are weakly interconnected._