# Phase 10 business blueprint and implementation contract

## Purpose and scope

Organization management supports the requirement-to-schedule-to-confirmed-actual
bridge. Planning / Project Controls is a first-class department. Existing
FastAPI, PostgreSQL, deterministic matching and PM authority remain canonical.
The repository is D:/Coding/pravaha. No repository AGENTS instructions were found.

## Organization

Business: Marketing & Business Development, Finance & Accounts, Contracts &
Commercial, Legal & Compliance. Operations: Project Management, Planning /
Project Controls, Civil, Mechanical, Piping, Electrical, Instrumentation &
Controls, Structural, Survey, Commissioning, Maintenance, QA/QC, HSE.
Supply chain: Procurement, Materials, Warehouse / Stores, Logistics.
People: HR, Training & Development, IT / Digital.

Departments have units and locations. Employees have stable workforce codes,
designations, departmental/unit membership, reporting managers, disciplines and
skills. Person identity is separate from an optional application account.
Designation never grants access. Corporate staff report through departments;
execution staff are allocated to project teams led by a TL and managed by a PM.

## Entity model and relationships

- Existing Organization / User / Project / Team / ScheduleActivity are reused.
- Department -> DepartmentUnit; Location; Designation; Skill.
- Employee -> department/unit/location/designation/manager and optional User;
  EmployeeSkill is a many-to-many junction.
- ProjectDepartment and ProjectMember connect departments and employees to projects.
- WorkforceAssignment connects an employee to a project and its team, with
  effective start/end, active/ended state and append-only historical rows.
- DepartmentGrant authorizes named account capabilities explicitly.
- Client -> Contact / Opportunity -> Tender -> Proposal -> CommercialContract
  -> Project. Marketing does not purchase raw materials.
- Vendor / Material / Store -> MaterialRequest(project/activity/team) ->
  PurchaseOrder -> GoodsReceipt -> MaterialMovement(store/site). Receipt and
  stock movement commit atomically; issues cannot make stock negative.
- PeopleRecord tracks recruitment, attendance, leave, training, performance,
  employee relations, grievance and wellbeing cases with typed record kind,
  employee/team/project links, dates and status. Confidential narrative is
  isolated from normal employees and summaries.
- Inspection -> QualityIssue/NCR -> CorrectiveAction, linked to project/activity.
- SafetyEvent(observation/incident) -> CorrectiveAction linked to project/team.
  Corrective actions belong to exactly one quality or safety source.

## Permission matrix

| Actor | Organization / modules | Execution | Confidential HR |
| --- | --- | --- | --- |
| Admin | master data, accounts, grants, explicit allocations, all ordinary module records | existing Admin scope | only with explicit hr-confidential grant |
| PM | own project workforce and business/material/quality/HSE links | current assigned projects; historical updates stay with original project | denied unless explicitly granted |
| TL | own team roster, attendance, material requests, quality/HSE capture | existing own-team submission; own historic reports remain readable | denied unless explicitly granted |
| Department account | explicitly granted module; current organization and linked projects only | no PM/TL operations | only hr-confidential; membership alone never sufficient |
| Workforce | login/logout/me only; generic access-restricted screen | none | none |

Workers use unique login IDs and individual random initial passwords, stored
only as Argon2id hashes. A local administrator-operated generator writes a
private one-time demo credential file outside web/public/source paths, excluded
by Git. No routine API returns passwords or hashes. Sensitive records never
appear in ordinary workspace/search/audit narrative; audit contains kind/ID/status only.

## Assignment rules

An active employee has at most one active workforce assignment. Team and project
must belong to the same organization and the team must have a valid enabled TL;
project must have an enabled PM. Explicit transfer ends the previous assignment
and records a new one and audit in the same transaction. Start/end dates cannot
overlap or move backwards. Project members and departments are explicit links.
Existing PM/TL assignment endpoints remain authoritative; selection alone never
writes an assignment. Team movement with historic schedule/update/workforce links
is rejected; a new team or an explicit workforce transfer preserves history.
A former TL may read own historic reports; modifications require current team
ownership. PM history is visible to the current owning PM/Admin, not every former PM.

## Minimum complete module workflows and acceptance

| Module | Responsible users | Workflow | Acceptance |
| --- | --- | --- | --- |
| Business | Admin / business grant; PM reads own project | client/contact -> opportunity -> tender -> proposal -> contract -> project | all foreign links scoped; status actions audited; project traceable |
| Materials | Admin / procurement grant; PM approves own requests; TL captures own request | request -> approved -> order -> receipt -> stock -> issue/site | no premature order, overreceipt or negative stock; rollback with audit |
| People | Admin / people grant; TL own attendance | recruitment -> hired; attendance recorded; leave requested -> approved/rejected; training planned -> completed; performance/relations recorded -> closed | employee scope enforced; valid dates; confidential kinds require separate grant |
| Quality | Admin / quality grant / scoped PM/TL | inspection planned -> inspected -> issue/NCR open -> corrective action -> verified/closed | activity project and team scope validated; open actions block closure |
| HSE | Admin / hse grant / scoped PM/TL | observation/incident open -> corrective action -> verified/closed | scoped capture; PM/authorized reviewer closes; no invented metrics |

## Schema, migration, API, UI and verification slices

Incremental revision 0004 follows 0003. Add normalized tables, indexes, FKs,
partial unique active-allocation constraints and two least-privilege account
roles; retain all existing rows. Before migration capture canonical fingerprints
and a PostgreSQL dump. Tests use genuine disposable PostgreSQL schemas.

New /api/organization endpoints provide paged/searchable master records,
overview, grants, memberships and explicit assignments. /api/modules provides
typed module resources and explicit status transitions, receipt and issue
operations. New Admin sections use reusable tables/forms/selectors with loading,
empty/error/success states; PM/TL retain their dashboards with scoped support
panels. Department accounts receive the same permission-aware module console;
workers receive the existing generic access restriction.

Default generator: 20 PMs x 8 teams x 20 named workers = 3,200 workers, 160 TLs,
plus PM/support employees, projects and connected module examples. Scale is
configurable and bounded, namespace-tagged and repeat-safe; unrelated data is
never overwritten. A unique demo organization avoids canonical demo reseeding.

Acceptance includes authentication/privilege denial, sensitive HR protection,
organization/project/team/object isolation, assignment dates/history, atomic
workflow/audit/stock changes, old data migration preservation, repeatability and
credential uniqueness, full regression/build/lint, live restart workflow and
Admin/PM/TL browser checks at 1440/1024/768/518. Live cloud deployment is outside
this implementation gate. No Phase 11-15 work is authorized.
