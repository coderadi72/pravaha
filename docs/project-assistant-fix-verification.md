# Project Assistant fix and UI verification

Date: 2026-10-05. Scope: the existing Project Assistant only.

## Result

Real hosted NVIDIA answers and Groq-to-NVIDIA failover were observed over an
isolated copy of the existing **Greenfield Refinery / ORG-OIL-DEMO** synthetic
records, with an authorized **PROJECT_MANAGER** identity. The compact UI was
verified in the browser at all four requested widths. This report does not
claim a cloud production deployment or reliable Groq account availability.

## Root causes and corrective changes

1. Supported workflow help bypassed the provider and returned `STATIC_GUIDANCE`.
   The frontend labelled any non-AI response as an AI outage. Workflow help now
   supplies approved application guidance through the existing authorized
   summary tool. Clarification, scope reminders and missing evidence use local
   `GUIDANCE`; genuine provider failures use `GUIDED_FALLBACK`.
2. The configured Groq model was unavailable to the account. The previous NVIDIA
   model returned HTTP 410; a legacy replacement listed in inventory returned
   404. Listing a model did not prove that its completion endpoint worked.
3. The replacement NVIDIA reasoning model consumed the bounded output allowance.
   Its documented chat-template setting now disables thinking when configured
   with `NVIDIA_REASONING_EFFORT=none`.
4. Provider responses sometimes had malformed JSON, unexpected schema fields or
   unsupported citations. Configurable JSON object mode, an explicit response
   template and one bounded validation-repair attempt improve reliability.
   Schema/citation/secret validation still rejects invalid answers; it is never
   weakened to make a live check pass.
5. A typed `await PM review` question did not match the existing `awaiting` alias.
   All ten displayed questions now have free-text routing regression coverage.
6. One inspected answer incorrectly generalized missing actuals across a group
   containing SA-1024, which has confirmed progress. Instructions now explicitly
   prohibit that generalization. The final inspected NVIDIA answer distinguished
   SA-1024's 65% progress and recorded actual start from activities with null
   actuals. Its dates, threshold, progress and delay values were checked against
   the supplied warning evidence. Citation validation is provenance validation,
   not a proof of arbitrary prose semantics; AI interpretation remains advisory.
7. Alembic's logging configuration disabled existing application loggers during
   earlier tests. `disable_existing_loggers=False` preserves safe provider/API
   diagnostics. No migration revision or database schema was added.

## Provider configuration and live evidence

The existing central settings loader and variable names remain authoritative.
`AI_PROVIDER=auto`, with `AI_PROVIDER_ORDER=groq,nvidia`, was retained. Both
credentials are **Configured**. Only non-secret model/response settings changed
in the private backend environment; no credentials were printed or changed.

| Setting | Selected value |
| --- | --- |
| Groq model | `openai/gpt-oss-20b` |
| NVIDIA model | `nvidia/nemotron-3-super-120b-a12b` |
| NVIDIA reasoning effort | `none` |
| Response format | `json_object` |
| Request bounds | Existing 30-second attempt timeout, 1,800 output tokens, 24,000 context characters, response-byte cap and request/concurrency limits |

Explicit `groq` or `nvidia` makes that provider primary and retains configured
secondary providers from the existing order. Missing keys are skipped; primary
failures attempt the available secondary. `none` still disables external calls.

| Live check | Observed result |
| --- | --- |
| Groq | Requests reached the API. Early completions returned normalized `PROVIDER_QUOTA` errors. One later automatic-provider check yielded an accepted Groq answer, but subsequent requests also produced truncated/invalid output. Stable selected-provider operation is not claimed. The user's request to finish with the Groq limitation documented was respected. |
| NVIDIA selected alone | Final execution-priorities and field-update-help questions both returned accepted real AI answers; signed sources reopened successfully. |
| Actual automatic failover | Groq returned `OUTPUT_TRUNCATED`; the real NVIDIA secondary returned an accepted answer. |
| Controlled primary outage | Only the primary was deliberately made unavailable; the actual hosted NVIDIA secondary returned an accepted answer. This was not a mocked AI response. |
| Both providers fail | Mocked transport/validation regressions retain useful guided fallback and clean retry UI. An earlier browser request also exercised rejection of both invalid provider responses. |
| Browser live request | The synthetic PM received a real AI answer with pending reviews, execution warnings and project metrics. Source FU-1048 reopened inside the widget. |

Safe logs distinguish configuration, missing keys, authentication, unavailable
models, quota/rate limits, timeout, truncation, invalid response and success.
They do not print request bodies, keys or raw provider error bodies. Provider
identity is retained in backend diagnostics and removed from client answers.

The final live questions were:

- What are the main execution items I should review for Greenfield Refinery?
- How do I submit a field update?

Evidence is in ignored local `.audit/assistant-live-{nvidia,auto,fallback}.json`
files. These contain synthetic evidence and safe diagnostics, without keys or
signed source URLs. Earlier failure artifacts are retained as failures.

## Authorization, preservation and runtime

- The assistant reuses the existing authenticated service layer and approved
  read tools; models have no database connection, native tools or write actions.
- PM project/org ownership, TL team scope, restricted-role denial, expired or
  revoked sessions, reassignment, source tampering and post-provider permission
  checks are covered by PostgreSQL regressions.
- Private HR/credential data is excluded before inference. Known-key scans
  passed across frontend source, production output, live evidence and runtime
  logs and this report; 72 files were checked. `backend/.env` and `.audit` remain Git-ignored.
- Runtime health/readiness returned 200. Admin, PM and TL login/context/source
  checks passed in the isolated fixture, without extra external calls. TL's
  returned context remained `TEAM`.
- Canonical and isolated business-data fingerprints were unchanged. Persisted
  sessions, signed sources and conversation context survived an isolated API
  restart.
- The existing reload-enabled development backend loaded the corrections and
  returned health 200. Its server was not replaced. The disposable verification
  processes/schema are cleaned up after checks.

## UI and responsive verification

| Section | Change and reason |
| --- | --- |
| Header | Small blue assistant mark, project/role subtitle, compact reset/minimize buttons; removes the large humanoid illustration. |
| Context | Compact Project/Language/Activity controls; project stacks above language/activity below 780px. Authorization context remains visible. |
| Empty conversation | Six compact chips plus More/Less, concise introduction. Chips disappear once conversation starts. |
| Messages | User bubbles, assistant headings/paragraphs/bullets, evidence and collapsible notes; safe React text rendering. |
| Loading/failure | Small animated dots, cancel control, neutral contextual failure notice and retry; raw failure codes are hidden. |
| Composer | Inline send, Enter to send, Shift+Enter newline, IME composition guard, counter and existing 1,200-character contract. |
| Interaction | Existing source inspection, cancellation, stale-response guards, session invalidation, Escape and focus behavior preserved. |

| Browser viewport | Panel | Outcome |
| --- | --- | --- |
| 1440 × 900 | 440 × 600 | No horizontal overflow; composer inside viewport. |
| 1024 × 768 | 440 × 600 | No horizontal overflow; controlled conversation scrolling. |
| 768 × 900 | 744 × 640 | Stacked context controls; no clipped selects/composer. |
| 518 × 800 | Approximately 494 × 640 | Almost full width; readable wrapping and source inspection; no horizontal overflow. |

Enter, Shift+Enter, More/Less, chip collapse and source reopening were exercised
in the browser. Console-error inspection returned an empty list. Screenshots
were captured and visually inspected inline; screenshot export to disk was
blocked with `EPERM` by the browser tool's filesystem restriction. This does
not mean browser automation was unavailable.

## Verification commands

| Command | Result |
| --- | --- |
| `node -v` | `v24.21.0` |
| `npm -v` | `11.19.0` |
| Python version | `3.12.14` |
| `npm test` | 54 passed |
| `npm run build` | Passed; existing lazy widget bundle preserved |
| `npm run lint` | Passed |
| `python -m pip check` | No broken requirements found |
| `python -m scripts.verify_phase12_assets` | Four production JS/CSS assets served correctly; local asset-routing check only |
| Complete PostgreSQL backend suite | 439 passed; 460.93 seconds |
| Final assistant regression suite | 73 passed; 124.12 seconds, including the final empty-evidence guard added after full-suite collection |
| `python -m scripts.verify_assistant_live nvidia` | Final two questions passed with genuine NVIDIA responses |
| `python -m scripts.verify_assistant_live auto` | Passed via actual NVIDIA fallback |
| `python -m scripts.verify_assistant_live fallback` | Passed via genuine NVIDIA secondary under controlled primary outage |
| Runtime smoke/restart/preservation | Passed in disposable synthetic fixture |

An earlier full backend run had **1 failed, 427 passed**:
`AssertionError: assert ('MODEL_UNAVAILABLE' in '')` in the newly added safe-log
test. This was a source logging-configuration interaction caused by migration
logger disabling, corrected as described above. The isolated test and a complete
rerun then passed (429 tests), before the final free-text/empty-evidence cases.
The existing Starlette TestClient/httpx deprecation warning remains dependency
technical debt; it is not a test failure. Live-provider errors are operational
limitations or rejected output, not fabricated PASS results.

## Files changed: section, change, reason

| File | Section / targeted change | Why |
| --- | --- | --- |
| `backend/app/core/config.py` | Provider defaults and typed optional JSON/reasoning settings | Retain one configuration system and usable model examples. |
| `backend/app/services/chat_provider.py` | Selection, transport, normalization, logs and bounded repair | Primary/secondary failover, safe diagnostics, compatible hosted requests. |
| `backend/app/services/assistant_service.py` | Help retrieval, prompt, validation and response modes | Request real AI for supported help, require grounded output, distinguish local guidance. |
| `backend/app/services/assistant_tools.py` | Approved workflow and zero-result summary projections | Supply authorized usable evidence without inventing execution facts. |
| `backend/app/services/assistant_catalogue.py` | Priorities intent and await alias | Route the requested free-text questions. |
| `backend/app/schemas/assistant.py` | Optional claim title and bounded guidance topic | Structured presentation and approved help selection. |
| `backend/alembic/env.py` | Existing logger preservation option | Keep application diagnostics enabled; no migration revision change. |
| `frontend/src/components/assistant/AssistantWidget.jsx` | Targeted header, controls, messages, chips and composer edits | Compact conversation-focused UX while retaining existing handlers. |
| `frontend/src/components/assistant/Robot.jsx` | Existing SVG contents | Friendly minimal mark with no humanoid face. |
| `frontend/src/components/assistant/catalogue.js` | Equivalent compact labels for three catalogues | Preserve language selection and useful suggestions. |
| `frontend/src/styles/assistant.css` | Scoped modernization overrides | Match existing tokens, bound panel/scrolling and responsive controls. |
| `backend/tests/test_phase12_assistant.py` | New routing, provider, help, logs and privacy regressions | Cover corrected behaviors alongside existing authorization tests. |
| `tests/phase12-frontend.test.js` | Compact UI contract regression | Preserve labels, keyboard bounds and provider-independent rendering. |
| `.env.example`, `backend/.env.example` | Safe model/response examples | Reproducible non-secret operator configuration. |
| `backend/.env` (private, ignored) | Non-secret model, JSON and reasoning values only | Load the working provider configuration; never commit secrets. |
| `README.md` | Assistant configuration and API mode descriptions | Match current selection, fallback and deployment limits. |
| `scripts/phase10_browser_setup.py` | Parameterized existing synthetic fixture | Copy only a verified demo organization and preserve original defaults. |
| `scripts/assistant_browser_setup.py` | Small Greenfield wrapper | Bound this verification to the requested synthetic project. |
| `scripts/verify_assistant_live.py` | Bounded selected/auto/fallback checks | Record real-provider evidence with no secret output or domain mutation. |
| `scripts/phase12_runtime.py` | Compatibility with private provider identity | Runtime checks use AI mode; backend live diagnostics verify actual identity. |
| This document | Current evidence and limitations | Make the targeted result reviewable without changing phase status. |

## Remaining limitations

- Groq account quota/access and output reliability are not resolved by this task;
  a one-off accepted answer is not a stable availability guarantee.
- Hosted providers can still return invalid or misleading prose. Bounded repair,
  validation, failover and useful guidance remain necessary. Provenance validation
  does not establish semantic truth; inspect source records before decisions.
- Final live checks used English and only the authorized synthetic Greenfield
  context. Live Hindi/Hinglish quality and cloud production deployment were not
  verified in this task.
- Existing per-worker cooldown/request-budget controls are not distributed
  billing controls. Existing production database throttling remains required.
- The TestClient dependency warning and blocked screenshot export are documented.

No unrelated phase implementation or application architecture rewrite was made.

## Provider references

- [NVIDIA Nemotron request API](https://docs.api.nvidia.com/nim/re/reference/nvidia-nemotron-3-super-120b-a12b-infer)
  documents bounded output and reasoning settings. The implementation uses the
  model's chat-template controls described in the [NVIDIA quickstart](https://docs.nvidia.com/nim/large-language-models/2.0.4/turbo/get-started-nemotron-3-super-120b-a12b.html).
- [NVIDIA structured generation](https://docs.nvidia.com/nim/large-language-models/1.15.0/structured-generation.html)
  and [Groq structured outputs](https://console.groq.com/docs/structured-outputs)
  describe JSON response modes. Configured hosted requests were also tested;
  documentation/model inventory alone is not counted as a live PASS.
