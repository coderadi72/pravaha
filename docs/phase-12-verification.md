# Phase 12 verification — 2026-10-04

## Status

**PHASE 12 NOT COMPLETE.** Independent implementation/regression checks passed.
Real Groq and NVIDIA operation, live English/Hindi/Hinglish response quality,
and the browser's genuine AI-answer path remain pending valid private provider
configuration. Mock transport/response tests are not evidence of live inference.

At the last safe configuration inspection, `AI_PROVIDER=none`, with neither
provider-specific key configured. Only provider name/key-present booleans were
inspected; no `.env` secret values were displayed. The user's private setup is
not assumed to have happened until the running configuration confirms it.

Approved phase order: **12 → 13 → 14 → 11 → 15**. Phase 11 is deferred. No
Phase 13, 14, 11 or 15 implementation was started.

## Implemented

Authenticated read-only assistant on Admin, PM and TL dashboards; Groq and
hosted NVIDIA adapters; bounded configurable primary/failover; honest guided
fallback; English/Hindi/Hinglish catalogues; animated inline SVG robot and
responsive panel; server-generated validated sources; signed session/context
isolation; current-permission checks before each read and after provider I/O.
Existing deterministic matching, review, reconciliation and domain writes stay
authoritative. Worker/Department assistant access is denied by default.

No SDK, animation dependency, schema revision, reseed or canonical reset was
introduced. HTTPX already exists in the backend requirements. Central settings,
API client, existing intelligence/repository/memory/dependency services are
reused. Configuration-only chat status is separate from live verification and
from the unavailable advanced ranking/OCR/ASR adapters.

## Commands actually executed

| Command | Result |
| --- | --- |
| `node -v` | v24.21.0 |
| `npm -v` | 11.19.0 |
| `.venv/Scripts/python.exe --version` | Python 3.12.14 |
| `.venv/Scripts/python.exe -m scripts.verify_phase12` | 420 passed in 468.48 seconds after status correction; one existing Starlette TestClient/httpx deprecation warning |
| Targeted `backend/tests/test_phase12_assistant.py` | 53 passed, one existing warning, 123.24 seconds |
| `npm test` | 53 passed, zero failed/skipped |
| `npm run lint` | PASS |
| `npm run build` | PASS; lazy assistant chunk 17.13 kB JS / 5.54 kB CSS; main JS 494.67 kB |
| `.venv/Scripts/python.exe -m pip check` | No broken requirements found |
| `.venv/Scripts/alembic.exe -c backend/alembic.ini check` | No new upgrade operations detected |
| `.venv/Scripts/alembic.exe -c backend/alembic.ini current` | 0004_organization (head) |
| `.venv/Scripts/python.exe scripts/verify_phase12_assets.py` | Four actual production JS/CSS assets served unchanged over temporary loopback; inline robot/widget bundle present; /assets/ excluded from SPA rewrite |

Tests use disposable PostgreSQL schemas. `npm test` intentionally prints
simulated legacy audit failures while verifying rollback; these are expected
fault-injection output, not failed tests. The earlier complete backend run was
413 tests before seven additional assistant cases; the expanded suite passed
420. Build initially warned about the combined main chunk; lazy loading the
assistant kept the final main chunk below 500 kB without adding dependencies.

## Automated coverage

- Roles and SQL scope: Admin own organization, PM ownership, TL team filtering
  before calculation, cross-project/team/organization rejection; existing TL
  denial on detailed intelligence endpoints remains intact; Worker/Department
  denied.
- Sessions/conversations/sources: tampering, other user, same user/new session,
  Admin different authorized project, logout, expiry, assignment changes and
  reassignment during inference; no stale answer returned after revocation.
- Providers using isolated HTTPX mocks: Groq/NVIDIA request fields, actual usage,
  either alone/both/ordered selection, generic/specific precedence, no keys,
  explicit disabled, invalid configuration, 429 with actual seconds/date
  Retry-After, quota, budget, timeout, unavailable failure, truncated,
  oversized and malformed output, context reduction, bounded failover/cooldown.
- Cancellation: provider coroutine/transport cancellation and no subsequent
  failover; disconnect cleanup; real AbortError preserved by frontend client.
- Evidence: all nine allowlisted reads, strict argument bounds, null variance,
  empty and partial data, unavailable historical conclusions, execution-only
  memory, fabricated reference rejection and validation against the evidence
  actually supplied after context reduction.
- Security: input identity overrides/unknown fields rejected; injection text
  remains untrusted; no mutation tool/SQL/browser access; known credentials and
  confidential HR records excluded from provider projection; heuristic sensitive
  free-text withholding; application throttling also applies to fallback.
- Language/guidance: English/Hindi/Hinglish intent and deterministic templates,
  auto detection/persistence, unsupported language rejection, ambiguity,
  unrelated questions and static help with no external call.
- Frontend: catalogue parity, role placement, source-path restriction,
  cancellation/stale-response guards, keyboard controls, memory-only history,
  inline SVG state binding and reduced-motion CSS.

Failure cases above are controlled tests. There was no live invalid-key, quota,
429, timeout or failover experiment against an external account.

## Runtime and persistence

An isolated `p12_browser_<UUID>` schema copied the existing synthetic demo
organization without using/exporting private provisioning passwords. Dedicated
synthetic fixture accounts and API 8003 / Vite 5176 were used. Original API/Vite
processes were left alone. Phase 12 checks did not submit operational updates or
reviews; current review/actual data was read from the existing synthetic copy.
Workflow regression remained covered by the complete existing suite.

- `/api/health` and `/api/ready`: HTTP 200 with AI disabled/no keys.
- Admin/PM/TL login, authorized overview, honest DISABLED guided fallback and
  generated source opening: HTTP 200. Admin/PM scope PROJECT; TL scope TEAM.
- The recorded isolated API was restarted. The persisted session, signed
  conversation and source remained valid and returned HTTP 200.
- Canonical and isolated domain fingerprints matched before/after. Sessions,
  limiter buckets and session audit are excluded because login/request checks
  necessarily update them; project/team/assignment/schedule/review/contribution,
  organization module and non-session audit data remained unchanged.
- An additional late probe returned 409 CONVERSATION_EXPIRED after its normal
  30-minute source-token lifetime. The helper's exact failure was
  `AssertionError` at `assert client.get(probe["source"]).status_code==200`.
  This was verification timing/fixture expiry, not an application defect. A
  fresh probe, actual API restart and unchanged assertions passed afterward.
- Only validated recorded Phase 12 processes and the disposable schema were
  cleaned up successfully. Ignored audit state records `cleanedUp=true`; its
  private session probe was removed. Canonical data/processes were preserved.

Local evidence: `.audit/phase12-pytest.log`,
`.audit/phase12-runtime-fallback.json`, isolated browser process logs and
`.audit/phase12-browser-state.json`. Audit artifacts are ignored and are not
application inputs or public assets. Private session probes are removed on
fixture cleanup.

## Browser verification

The in-app browser was available; no API-only substitute was necessary.

| Check | Observed result |
| --- | --- |
| Home → Login → PM | Existing workspace and shared assistant opened |
| Home → Login → Admin | Existing portfolio and own-organization project selectors opened |
| Home → Login → TL | Existing field workspace; assistant showed one assigned project and one team activity |
| Worker | Access-restricted view; no assistant button/dashboard |
| Department | Existing granted department workspace preserved; no assistant button |
| Current source | PM pending-review answer opened current signed source; actual count 0 |
| Admin project change | Prior conversation cleared; next answer named the new project |
| Logout | Widget removed; next login did not inherit prior conversation |
| Keyboard/typing | Text entry selected attentive robot state; Escape minimized and returned focus to launcher |
| Processing/fallback | Real request showed processing/cancel control, then honest guided fallback state |
| English/Hindi/Hinglish | Localized catalogue/controls and pending-review templates displayed; identifiers retained |

PM panel screenshots were visually inspected at each requested width with
height 900. DOM bounds confirmed no document horizontal overflow:

| Width | Panel bounds (left/right/top/bottom) |
| --- | --- |
| 1440 | 953.2 / 1413.2 / 162 / 882 |
| 1024 | 537.2 / 997.2 / 162 / 882 |
| 768 | Approximately 282 / 742; full panel remained inside viewport |
| 518 | 39.6 / 499.6 / 10 / 890 |

Panel scroll and minimize keep underlying workflow controls reachable. These
checks cover the assistant on existing pages, not a Phase 11 redesign or full
site accessibility certification. Reduced-motion rules were inspected/tested;
changing the operating system preference was not exercised. Genuine AI-ready
and provider-error browser states remain pending live configuration. Screenshot
captures were inspected inline, but saving them to workspace or temporary files
returned EPERM under the browser tool's read-only filesystem; no saved screenshot
artifact is claimed.

## Corrections made during implementation

1. Hindi pending-review recognition overlapped with the delayed word; precise
   Devanagari word boundaries fixed the collision.
2. TL projected schedule team IDs now use persisted ORM team ownership before
   team calculation, rather than stale JSON ownership fields.
3. Citation validation now checks the records in the actual provider attempt
   after context trimming/reduction.
4. Pending-review count 0 and empty memory total remain honest; summary source
   gets a real checked-at timestamp.
5. Provider 422/configuration errors and context/response bounds were tightened;
   cancellation remains distinct from network failure.
6. System status now reports installed chat adapters/configuration separately
   from live inference; initial bundle warning resolved by lazy widget loading.

Initial test failures also exposed a revocation-test helper that unnecessarily
queried projects after revocation and shared limiter state between assertions;
the fixture helpers were corrected without weakening rejection assertions.

## Precise remaining work and deployment limits

1. Privately set `AI_PROVIDER=auto`, `GROQ_API_KEY` and `NVIDIA_API_KEY` plus
   account-accessible models in `backend/.env`. Restart the isolated verification
   API to pick up settings. Never paste keys into chat.
2. Run bounded real Groq and NVIDIA authorized answers with valid sources and
   English/Hindi/Hinglish checks. Review content quality and identifier/numeric
   preservation; a configured status or mocked completion is insufficient.
3. Verify genuine AI output/source opening and robot answer state in the browser,
   including real request cancellation where practical. Resolve any live API
   compatibility/quality defects found; rerun affected and full regression.

Vercel frontend → native Render Python backend → Neon PostgreSQL remains the
target. HTTPS/CORS/cookies/SSL/shared limiter are configuration-tested. Actual
cloud deployment, provider account model access/retention policies, global
cost control, enterprise load and Neon PITR are operational checks not performed
here. No fabricated provider/cloud evidence is recorded.

Technical limits: bounded first-page question retrieval; deterministic catalogue
may clarify complex phrasing; historical health depends on recorded snapshots;
team dependency edges cannot establish whole-project exposure; free-text
privacy redaction is heuristic; citation validation is not semantic proof;
cooldown/budget/concurrency are per worker. These limitations are explicit in
blueprint/setup and current-data answers.

**PHASE 12 NOT COMPLETE — LIVE GROQ/NVIDIA AND AI BROWSER VERIFICATION PENDING.**
