from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictFloat, StrictInt, StrictStr

Role = Literal["ADMIN", "PROJECT_MANAGER", "TEAM_LEADER", "WORKFORCE", "DEPARTMENT"]
Progress = StrictInt | StrictFloat


class RequestModel(BaseModel):
    # Old clients may send additional form context; scores and actor IDs are ignored.
    model_config = ConfigDict(extra="ignore")


class LoginRequest(RequestModel):
    email: StrictStr = Field(min_length=1, max_length=254)
    password: StrictStr = Field(min_length=1, max_length=128)


class ProvisionUserRequest(RequestModel):
    name: StrictStr = Field(min_length=1, max_length=120)
    email: StrictStr = Field(min_length=1, max_length=254)
    password: StrictStr = Field(max_length=128)
    role: StrictStr


class ManagerAssignmentRequest(RequestModel):
    projectManagerId: StrictStr | None = None


class TeamAssignmentRequest(RequestModel):
    projectId: StrictStr | None = None
    assigned: bool = True


class LeaderAssignmentRequest(RequestModel):
    teamLeaderId: StrictStr | None = None


class FieldUpdateRequest(RequestModel):
    quantity: Progress | None = Field(default=None, ge=0, allow_inf_nan=False)
    unit: StrictStr | None = Field(default=None, max_length=80)
    remarks: StrictStr | None = Field(default=None, max_length=500)
    blocker: StrictStr | None = Field(default=None, max_length=500)
    crew: StrictStr | None = Field(default=None, max_length=120)
    equipment: StrictStr | None = Field(default=None, max_length=120)
    description: StrictStr = Field(min_length=1, max_length=500)
    observation: StrictStr | None = Field(default=None, max_length=500)
    discipline: StrictStr | None = Field(default=None, max_length=500)
    location: StrictStr | None = Field(default=None, max_length=500)
    attachmentName: StrictStr | None = Field(default=None, max_length=255)
    attachmentType: StrictStr | None = Field(default=None, max_length=80)
    activityId: StrictStr | None = None
    progress: Progress | None = Field(default=None, ge=0, le=100)


class FieldUpdateEditRequest(RequestModel):
    quantity: Progress | None = Field(default=None, ge=0, allow_inf_nan=False)
    unit: StrictStr | None = Field(default=None, max_length=80)
    remarks: StrictStr | None = Field(default=None, max_length=500)
    blocker: StrictStr | None = Field(default=None, max_length=500)
    crew: StrictStr | None = Field(default=None, max_length=120)
    equipment: StrictStr | None = Field(default=None, max_length=120)
    description: StrictStr | None = Field(default=None, min_length=1, max_length=500)
    observation: StrictStr | None = Field(default=None, max_length=500)
    discipline: StrictStr | None = Field(default=None, max_length=80)
    location: StrictStr | None = Field(default=None, max_length=120)
    progress: Progress | None = Field(default=None, ge=0, le=100)


class ActivityDetails(RequestModel):
    observation: StrictStr | None = Field(default=None, max_length=500)
    blockedReason: StrictStr | None = Field(default=None, min_length=1, max_length=500)
    progress: Progress | None = Field(default=None, ge=0, le=100)
    actualStart: StrictStr | None = None
    actualEnd: StrictStr | None = None


class ActivityActionRequest(RequestModel):
    action: StrictStr
    details: ActivityDetails | None = None


class ReviewRequest(RequestModel):
    scheduleActivityId: StrictStr | None = None
    reason: StrictStr = Field(default="", max_length=500)
    feedback: StrictStr = Field(default="", max_length=500)


class SafeUser(BaseModel):
    id: str
    email: str
    name: str
    role: Role
    organizationId: str


class Entity(BaseModel):
    # Existing payloads include presentation details; extra fields remain compatible.
    model_config = ConfigDict(extra="allow")
    id: str


class Organization(Entity):
    name: str


class Project(Entity):
    name: str


class Team(Entity):
    projectId: str | None = None


class ScheduleActivity(Entity):
    projectId: str
    teamId: str | None = None
    activityName: str


class Evidence(BaseModel):
    signal: str
    outcome: str
    text: str


class Candidate(BaseModel):
    model_config = ConfigDict(extra="allow")
    scheduleActivityId: str
    activityName: str
    score: int = Field(ge=0, le=100)
    evidence: list[Evidence] = []


class FieldUpdate(Entity):
    projectId: str
    teamId: str | None = None
    rawText: str
    extractedActivity: dict[str, Any]
    reviewHistory: list[dict[str, Any]] = []


class ActivityMatch(BaseModel):
    model_config = ConfigDict(extra="allow")
    fieldUpdateId: str
    scheduleActivityId: str | None = None
    candidates: list[Candidate] = []
    evidence: list[Evidence] = []
    confidence: int = Field(ge=0, le=100)
    matcherVersion: str
    generatedAt: str


class Review(Entity):
    fieldUpdateId: str


class WorkspaceData(BaseModel):
    model_config = ConfigDict(extra="allow")
    organization: Organization
    users: list[Entity]
    projectManagers: list[Entity]
    teamLeaders: list[Entity]
    projects: list[Project]
    teams: list[Team]
    scheduleActivities: list[ScheduleActivity]
    fieldUpdates: list[FieldUpdate]
    activityMatches: list[ActivityMatch]
    reviewItems: list[Review]
    scheduleActivityContributions: list[dict[str, Any]]
    scheduleActivityBaselines: dict[str, dict[str, Any]]
    organizationActivity: list[dict[str, Any]]


class AuthResponse(BaseModel):
    user: SafeUser
    expiresAt: str


class WorkspaceResponse(BaseModel):
    user: SafeUser
    data: WorkspaceData


class DataResponse(BaseModel):
    data: WorkspaceData


class FieldUpdateResponse(DataResponse):
    fieldUpdate: FieldUpdate


class ReviewResponse(DataResponse):
    message: str | None = None
    shouldClose: bool | None = None


class ProvisionedUser(BaseModel):
    id: str
    email: str
    name: str
    role: Role
    active: int


class ProvisionUserResponse(BaseModel):
    user: ProvisionedUser


class OrganizationResponse(BaseModel):
    organization: Organization
    activity: list[dict[str, Any]]


class ProjectsResponse(BaseModel):
    projects: list[Project]


class UsersResponse(BaseModel):
    users: list[Entity]


class TeamsResponse(BaseModel):
    teams: list[Team]


class ProjectResponse(BaseModel):
    project: Project


class ScheduleResponse(BaseModel):
    schedule: list[ScheduleActivity]


class ActivitiesResponse(BaseModel):
    activities: list[ScheduleActivity]


class FieldUpdatesResponse(BaseModel):
    fieldUpdates: list[FieldUpdate]


class ReviewsResponse(BaseModel):
    reviews: list[Review]


class TeamLeaderResponse(BaseModel):
    user: SafeUser
    team: Team | None


class HealthResponse(BaseModel):
    status: Literal["ok"]
    service: Literal["pravaha-api"]


class OkResponse(BaseModel):
    ok: bool


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorDetail
