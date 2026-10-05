PRAVAHA
Intelligent Project Progress Monitoring & Execution Intelligence

Smart India Hackathon 2026 · SIH26122 · Oil India Limited

Bridging Planning and Field Execution through Intelligent Data Capture, Schedule Linking, Progress Verification, and Project Intelligence.

PRAVAHA is an end-to-end infrastructure project progress monitoring platform designed to connect project planning and scheduling with real-world field execution.

WHAT IS PRAVAHA?

Infrastructure projects generate information across schedules, field reports, spreadsheets, site updates, supervisor observations, and project management systems.

The challenge is connecting real-world execution back to the correct scheduled activity.

PRAVAHA provides a planning-to-execution bridge:

Planning
  ↓
Project Schedule
  ↓
L1 → L2 → L3 → L4 → L5 → L6
  ↓
Field Updates
  ↓
Activity Extraction
  ↓
Schedule Matching
  ↓
Confidence + Evidence
  ↓
Project Manager Review
  ↓
Confirmed Actual Progress
  ↓
Execution Intelligence
  ↓
AI-Assisted Project Insights

PROBLEM STATEMENT

Large infrastructure projects commonly face:

- Field progress recorded across disconnected sources.
- Daily reports and supervisor updates not mapping cleanly to scheduled activities.
- Difficulty identifying the exact L5/L6 activity represented by a field update.
- Manual reconciliation between planning and execution data.
- Delayed visibility into actual project progress.
- Inconsistent progress reporting.
- Difficulty identifying schedule variance and execution risks.
- Limited reuse of historical project information.
- Lack of unified visibility across projects, teams, departments, and workforce.

OUR SOLUTION

PRAVAHA creates a structured bridge between the project schedule and field execution.

The platform enables organizations to:

- Maintain structured project and schedule information.
- Capture field execution updates.
- Extract meaningful activity information from field inputs.
- Match field activities with scheduled L5/L6 activities.
- Provide confidence and supporting evidence for matches.
- Allow Project Managers to review and confirm proposed matches.
- Record confirmed actual progress.
- Analyze execution variance and project health.
- Manage teams, workforce, departments, and assignments.
- Maintain project activity history and auditability.
- Provide AI-assisted project intelligence through authorized application data.

CORE WORKFLOW

Project Planning
  ↓
L1 → L2 → L3 → L4 → L5 → L6 Schedule
  ↓
Field Execution
  ↓
Activity Extraction
  ↓
Schedule Matching
  ↓
Confidence + Evidence
  ↓
PM Review
  ↓
Confirmed Actual Progress
  ↓
Execution Intelligence
  ↓
Management Insights + AI Assistance

KEY FEATURES

1. Project & Schedule Management

- Structured project hierarchy.
- Multi-level schedule representation.
- L1–L6 activity structure.
- Project schedules and baselines.
- Activity dependencies.
- Schedule relationships.
- Project progress monitoring.
- Planned vs actual comparison.
- Schedule-linked execution tracking.

2. Field Execution

Team Leaders / Supervisors can capture real execution information from the field.

- Field progress updates.
- Structured execution records.
- Activity observations.
- Supporting evidence and attachments.
- Discipline-aware execution information.
- Activity extraction from field descriptions.
- Project and activity ownership validation.

Example:

Field Update:
"Spool erected for Line 247-XX"

PRAVAHA can interpret the update as an execution activity and identify the corresponding scheduled activity for review.

3. Schedule Intelligence

- Activity extraction.
- Schedule activity matching.
- Confidence scoring.
- Matching evidence.
- Discipline-aware matching.
- Candidate activity identification.
- PM review workflow.
- Confirmation of actual progress.
- Schedule variance analysis.

Example:

Field Update
  ↓
"Spool erected for Line 247-XX"
  ↓
Extracted Activity: Spool Erection
  ↓
Discipline: Piping
  ↓
Schedule Candidate: Erect Line 247-XX
  ↓
Confidence: 94%
  ↓
PM Review
  ↓
Confirmed Actual

4. Execution Intelligence

PRAVAHA provides project-level execution intelligence based on structured project and actual-progress data.

- Project health analysis.
- Progress variance.
- Schedule variance.
- Execution warnings.
- Delayed activity identification.
- Activity timelines.
- Progress coverage.
- Project-level analytics.
- Execution trend analysis.
- Institutional project memory.

5. AI Intelligence Assistant

PRAVAHA includes an AI-assisted project intelligence layer designed to help authorized users understand project information through natural language.

Capabilities include:

- Understanding project status.
- Finding delayed activities.
- Reviewing pending items.
- Understanding project timelines.
- Checking execution variance.
- Reviewing execution warnings.
- Searching project-related knowledge.
- Generating project-oriented insights.

AI ARCHITECTURE

AI Model
  ↓
PRAVAHA APIs & Services
  ↓
Authorized Project Context
  ↓
PostgreSQL Source of Truth

The AI layer is separated from the underlying database and works through authorized application interfaces and project context.

ROLE-BASED ACCESS

ADMIN
  ↓
PROJECT MANAGER
  ↓
TEAM LEADER / SUPERVISOR
  ↓
FIELD EXECUTION

Administrator:
- Organization management.
- User management.
- Project management.
- Department management.
- Team management.
- Workforce management.
- Assignments.
- Data and imports.
- Reports.
- Activity and audit visibility.
- System configuration.

Project Manager:
- Project monitoring.
- Schedule visibility.
- Activity review.
- Schedule matching review.
- Actual progress confirmation.
- Execution intelligence.
- Variance analysis.
- Project health monitoring.

Team Leader / Supervisor:
- Field updates.
- Execution observations.
- Evidence submission.
- Activity-related reporting.
- Team/workforce coordination.
- Monitoring assigned execution work.

PRAVAHA does not require a separate application role for Field Workers. Workforce members can be represented through workforce records and assignments while field execution is managed through the Team Leader / Supervisor workflow.

ORGANIZATION MANAGEMENT

PRAVAHA is designed to support organization-wide project operations.

Project & Operations:
- Project Management
- Planning / Project Controls
- Civil
- Mechanical
- Piping
- Electrical
- Instrumentation & Controls
- Structural
- Survey
- Commissioning
- Maintenance
- QA/QC
- HSE

Supply Chain:
- Procurement
- Materials
- Warehouse / Stores
- Logistics

Business & Corporate:
- Marketing & Business Development
- Finance & Accounts
- Contracts & Commercial
- Legal & Compliance

People & Technology:
- Human Resources
- Training & Development
- IT / Digital

SYSTEM ARCHITECTURE

React + Vite Frontend
  ↓
Centralized API Client
  ↓
FastAPI + Pydantic
  ↓
Authentication + Authorization + Workflow
  ↓
Extraction / Matching / Confidence / Audit
  ↓
SQLAlchemy 2.x
  ↓
PostgreSQL
  ↓
Alembic Migrations

DEPLOYMENT ARCHITECTURE

PRAVAHA uses a separated frontend, backend, and database architecture.

Vercel
  ↓
React + Vite Frontend

Render
  ↓
FastAPI Backend

Neon
  ↓
PostgreSQL Database

TECHNOLOGY STACK

Frontend: React + Vite
Backend: FastAPI
API Validation: Pydantic
ORM: SQLAlchemy 2.x
Database: PostgreSQL
Migrations: Alembic
Authentication: Session-based authentication
Password Security: Argon2id
AI: Configured AI provider APIs
API Communication: REST
Version Control: Git / GitHub

PROJECT STRUCTURE

PRAVAHA/
├── backend/
│   └── app/
│       ├── api/
│       ├── core/
│       ├── db/
│       ├── models/
│       ├── schemas/
│       └── services/
│
├── frontend/
│   ├── public/
│   └── src/
│       ├── components/
│       ├── pages/
│       ├── services/
│       └── ...
│
├── database/
├── docs/
├── scripts/
├── tests/
├── .env.example
├── .gitignore
└── README.md

GETTING STARTED

Prerequisites:

- Node.js
- npm
- Python
- PostgreSQL
- Git

Use the versions specified by the project configuration.

INSTALLATION

Clone the repository:

git clone <YOUR-GITHUB-REPOSITORY-URL>
cd <PROJECT-DIRECTORY>

FRONTEND SETUP

cd frontend
npm install

Create the frontend environment file from .env.example and configure the required values.

Start the frontend:

npm run dev

BACKEND SETUP

cd backend

Windows:

python -m venv .venv
.venv\Scripts\Activate.ps1

Linux / macOS:

python3 -m venv .venv
source .venv/bin/activate

Install dependencies:

pip install -r requirements.txt

Create the backend environment file from .env.example and configure the required values.

DATABASE SETUP

PRAVAHA uses PostgreSQL with Alembic migrations.

After configuring the database:

alembic upgrade head

Always use the migration system for schema changes.

ENVIRONMENT VARIABLES

PRAVAHA uses environment variables for configuration and secrets.

Typical configuration areas:

- Database connection
- Authentication/session configuration
- CORS configuration
- Frontend API URL
- AI provider configuration
- Application configuration

Never commit:

- .env
- API keys
- Database passwords
- JWT/session secrets
- Private credentials
- Production tokens

Use .env.example as the configuration reference.

RUNNING PRAVAHA

Backend:

uvicorn app.main:app --reload

Frontend:

npm run dev

The frontend communicates with the FastAPI backend through the configured API endpoint.

TESTING & VERIFICATION

Verification covers major application areas including:

- Backend functionality.
- Frontend build.
- Linting.
- Database migrations.
- Authentication.
- Authorization.
- Project ownership.
- Schedule workflows.
- Activity matching.
- PM review.
- Actual progress confirmation.
- Execution intelligence.
- Organization workflows.
- Responsive UI behavior.
- Application restart persistence.
- API workflows.

Run the test commands defined by the repository configuration.

SECURITY

Implemented security areas include:

- Secure password hashing.
- Session-based authentication.
- HttpOnly authentication cookies.
- Role-based authorization.
- Project ownership checks.
- Request validation.
- Rate limiting.
- CORS controls.
- Request/body-size protection.
- Protected administrative operations.
- Environment-based secret management.
- Auditability of important workflow actions.

PRAVAHA follows a least-privilege approach where operations are performed according to the authenticated user's role and project permissions.

WHY PRAVAHA?

Traditional project monitoring often treats planning and execution as separate information streams.

PRAVAHA connects them.

Traditional Approach:

Schedule
  +
Field Reports
  +
Spreadsheets
  ↓
Manual Reconciliation

PRAVAHA:

Schedule
  ↓
Field Update
  ↓
Extraction
  ↓
Matching
  ↓
Confidence
  ↓
PM Review
  ↓
Confirmed Actual
  ↓
Execution Intelligence
  ↓
Decision Support

PLAN → EXECUTE → VERIFY → UNDERSTAND → ACT

DATA & INTELLIGENCE PIPELINE

Raw Field Information
  ↓
Structured Extraction
  ↓
Activity Identification
  ↓
Schedule Matching
  ↓
Confidence + Evidence
  ↓
Human Review
  ↓
Confirmed Actual
  ↓
Variance Analysis
  ↓
Execution Warnings
  ↓
Project Intelligence
  ↓
AI-Assisted Understanding

FINAL IMPLEMENTATION STATUS

PRAVAHA's planned implementation phases have been completed.

The final platform brings together:

- Authentication & authorization
- Registration and administrative approval
- Project management
- Schedule management
- Field execution
- Activity extraction
- Schedule matching
- Confidence and evidence
- PM review
- Actual progress tracking
- Execution intelligence
- Organization management
- Workforce management
- Team and assignment workflows
- Analytics
- Auditability
- AI-assisted project intelligence
- Responsive enterprise UI
- Security controls
- End-to-end project workflow

PRAVAHA demonstrates a complete planning-to-execution bridge for infrastructure project management.

DOCUMENTATION

Detailed technical documentation is available inside the docs/ directory.

Documentation covers areas such as:

- Architecture
- Authentication
- Schedule ingestion
- Activity matching
- Execution intelligence
- Organization management
- AI assistant
- Verification
- Deployment
- Project workflows

FUTURE ENHANCEMENTS

The core PRAVAHA implementation is complete. Optional future enhancements may include:

- Advanced OCR pipelines.
- Production-grade speech/voice ingestion.
- Additional enterprise scheduling integrations.
- Advanced predictive forecasting.
- Critical-path optimization.
- Resource optimization.
- Advanced anomaly detection.
- Enterprise observability.
- Additional external system integrations.

SMART INDIA HACKATHON

Problem Statement: SIH26122
Organization: Oil India Limited
Theme: Smart Automation
Solution: PRAVAHA — Intelligent Project Progress Monitoring & Execution Intelligence

PRAVAHA addresses the gap between project planning and real-world field execution by creating a structured, reviewable, and intelligent bridge between schedules and actual project progress.

PRAVAHA

From Field Updates to Smarter Schedules.

PLAN → CAPTURE → MATCH → REVIEW → CONFIRM → ANALYZE → INTELLIGENCE

LICENSE

Refer to the repository license file if present.
