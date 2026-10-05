# Phase 12 — Animated Project Intelligence Analyst

Current phase: 12. Owner-approved order: **12 → 13 → 14 → 11 → 15**. Phase 11 is deferred. This design implements the updated Groq/NVIDIA/multilingual prompt and preserves React/Vite, FastAPI, SQLAlchemy/PostgreSQL, Alembic, deterministic matching and PM confirmation.

## Architecture

Dashboard robot → central frontend API → authenticated assistant service → deterministic intent catalogue → authorized read tools → existing intelligence/memory/dependency calculations → provider adapter or labelled guided template. The existing OCR/ASR/ranking placeholder is kept separate from chat. No migrations or operational writes are required.

Groq and hosted NVIDIA use their documented chat-completion transports. Server-controlled retrieval avoids assuming model tool or structured-output support. The model receives bounded projected evidence and must return a locally validated JSON explanation referencing server-issued evidence IDs. No native model tools, browsing, SQL, files or mutation endpoints are provided. Provider/model compatibility and multilingual quality still require live account checks.

## Permissions and scope

| Role | Assistant scope |
|---|---|
| Admin | Own organization project information; paged organization project summary |
| PM | Current owned projects only |
| TL | Assigned team's project, team activities/updates and team-derived metrics only |
| Workforce / Department | Denied by default |

Detailed project intelligence endpoints retain their existing Admin/PM restriction. Narrow TL reads filter SQL before calculation/retrieval; team health cannot be presented as whole-project health. Every request/read/source/final response checks the persisted session and current assignment. Conversation tokens bind user/org/role/session/project/team and assignment timestamp, using the existing random-session digest as the server-only signing key. Bounded previous questions are signed; old AI answers are never fed back as facts. No conversation database storage. Widget history is memory-only and clears on context/logout/expiry changes.

## Read tools

Allowlisted capabilities: get_project_summary, get_project_health, get_delayed_activities, get_pending_reviews, get_execution_warnings, get_schedule_variance, get_activity_timeline, get_dependency_impact, search_project_memory. Strict inputs: optional authorized activity ID, literal search, recent-days filter, at-risk switch, bounded pagination. Server identity/project scope cannot be model-overridden. Existing calculation/retrieval services are reused; refresh/acknowledge/review/assignment are never invoked.

Outputs carry stable evidence IDs, generated application source routes, retrieval/source timestamps, data category (synthetic/imported/recorded/derived), scope, empty/missing/stale/partial indicators. Null actuals remain null. Current health alone proves no decline or cause; bounded persisted refresh snapshots are used where available. Memory is execution-only: confidential HR, workforce dumps, credentials, attachments and private provisioning exports are excluded before provider context construction. Retrieved text is untrusted.

## Providers, fallback and bounds

Explicit AI_PROVIDER=none disables external calls. Auto tries only configured providers in AI_PROVIDER_ORDER. Provider-specific values take precedence; generic AI_API_KEY / AI_MODEL / AI_BASE_URL apply only to an explicitly selected provider. Configurable timeout, retries, context/response/output bounds, tool reads, cooldown, per-user rate limit, concurrency and optional per-worker daily request budget bound costs. Actual retry-after governs cooldown; authentication/model errors are not retried. Safe context reduction removes history and whole evidence records without dropping instructions or orphaning citations. Cancellation cancels HTTP transport and prevents failover. Database sessions end before provider I/O.

Maintainable intent and language catalogues provide English, Hindi and Hinglish static workflow guidance and deterministic data templates without external calls. Ambiguous intent requests clarification; unrelated requests receive a scope reminder. Live AI and fallback are visibly labelled. Fallback never bypasses authentication/authorization/application throttling. Per-worker cooldown/budget/concurrency are not a globally distributed billing guarantee; production per-user throttling reuses PostgreSQL's existing limiter.

## Interface and completion

Shared floating launcher/chat panel on Admin/PM/TL only, inline SVG mascot inspired by supplied white/blue robot. Real idle/typing/loading/answer/fallback/error states, minimize, keyboard focus, reduced-motion support. No runtime temp assets or new animation dependency. Languages, context, suggested questions, sources, timestamps, retry/cancel and insufficient evidence are explicit. Full UI polish remains Phase 11.

Current tests, runtime/source inspection, four widths (1440/1024/768/518), build/lint/dependency/Alembic checks and bounded live provider checks are required. Without keys, finish independent implementation and verification, report live checks pending and **PHASE 12 NOT COMPLETE**. Mock tests never count as genuine inference. Cloud deployment/PITR remain separate operational checks.

Official transport references: [Groq compatibility](https://console.groq.com/docs/openai), [Groq rate limits](https://console.groq.com/docs/rate-limits), [NVIDIA hosted LLM API](https://docs.api.nvidia.com/nim/reference/llm-apis).

## Read contracts and provenance

The orchestrator chooses tools from a maintained intent catalogue; the provider
cannot choose arbitrary tools or arguments. `ToolArgs` rejects unknown fields
and bounds `activity_id` (160 characters), literal `query` (200), `recent_days`
(1–90), `at_risk` (boolean), `limit` (1–50, further capped by configuration),
and `offset` (0–10,000). Identity and scope come only from the authenticated
session. The question endpoint uses configured first-page limits; internal
read contracts support bounded pagination. The widget paginates project
contexts, and shows partial evidence instead of claiming an exhaustive answer.

| Read tool | Authorized evidence / limitations |
| --- | --- |
| `get_project_summary` | Existing derived execution summary/data health; Admin organization mode returns paged project identity/status, not a fabricated portfolio aggregate |
| `get_project_health` | Existing current calculation plus bounded persisted refresh snapshots for Admin/PM; no continuous historical series; TL team-only current health |
| `get_delayed_activities` | Existing delayed/at-risk activity projections; no new forecast |
| `get_pending_reviews` | SQL-scoped count, bounded team grouping and field-update records; no assumption that reported actuals are confirmed |
| `get_execution_warnings` | Existing calculated warnings and persisted warning state; no refresh or acknowledgement |
| `get_schedule_variance` | Existing activity variance; missing actuals stay null/UNKNOWN |
| `get_activity_timeline` | Required authorized activity and execution-only memory; no invented decision/lesson |
| `get_dependency_impact` | Existing graph impact; TL edges require both endpoints in its team; no invented critical-path forecast |
| `search_project_memory` | Existing parameterized literal execution search; `search:` prefix supplies query; no HR/roster/attachment retrieval |

Each envelope carries current scope, checked-at time, total/limit/offset,
partial/status, dataset label, limitations and records. Record categories are
`RECORDED`, `DERIVED_METRICS` or `RECORDED_DERIVED_SNAPSHOT`; imported execution
facts may underlie current metrics, without claiming a separate import history
was retrieved. Synthetic dataset labels accompany source records. Source
timestamps may be unavailable and are not replaced with invented dates.
Generated source references bind the current session and assignment and reread
the same authorized tool; disappeared evidence returns SOURCE_CHANGED.

## Provider compatibility and interpretation

Groq uses `max_completion_tokens` and NVIDIA uses `max_tokens` with the configured
model cap. Both send only model, messages and non-streaming completion bounds;
no assumption of native tools, JSON-schema support or unsupported storage
parameters. See [Groq API contract](https://console.groq.com/docs/api-reference)
and [NVIDIA Llama 3.3 hosted model contract](https://docs.api.nvidia.com/nim/re/reference/meta-llama-3_3-70b-instruct-infer).
Non-200, async 202, truncated, oversized, invalid JSON or invalid citation output
becomes a normalized failure/fallback. 401/403/404/422 configuration errors are
not retried; actual Retry-After seconds/date control cooldown. Only actual
provider token usage is returned; no invented costs or reset times.

Local validation bounds prose and requires every claim to cite evidence
actually included in that attempt, including after context reduction. It
rejects fabricated references, external URLs and known secrets. This validates
structure/provenance, not a formal proof that every natural-language inference
is true. AI interpretation remains advisory and requires source inspection;
the existing deterministic matcher and PM decisions remain authoritative.

The model receives projected execution evidence and sanitized bounded text.
HR tables and account exports are never retrieved. Credential and sensitive
free-text redaction is heuristic; it cannot guarantee detection of arbitrary
personal information embedded in execution records. Provider retention/account
policies need an operator decision before production use.

Configuration/setup, API inputs and deployment checklist are in README.
Verification evidence and precise completion gaps are in
[Phase 12 verification](phase-12-verification.md). No later phase is implemented.
