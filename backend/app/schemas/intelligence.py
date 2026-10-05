"""Phase 8 response contracts; evidence retains deterministic rule-specific fields."""
from typing import Any, Literal
from pydantic import BaseModel

class Warning(BaseModel):
    id: str
    projectId: str
    activityId: str | None
    fieldUpdateId: str | None = None
    type: str
    severity: Literal["LOW", "MEDIUM", "HIGH"]
    status: Literal["OPEN", "ACKNOWLEDGED", "RESOLVED"]
    generatedAt: str
    evidence: dict[str, Any]
    reason: str
    attention: str

class HealthDimension(BaseModel):
    status: str
    reason: str

class ActivityIntelligence(BaseModel):
    activityId: str
    name: str
    plannedStart: str | None
    plannedEnd: str | None
    actualStart: str | None
    actualEnd: str | None
    confirmedProgress: float | None
    confirmedUpdateIds: list[str]
    hasConfirmedActual: bool
    actualSource: str | None = None
    status: str
    timing: str
    startVarianceDays: int | None
    finishVarianceDays: int | None
    durationVarianceDays: int | None
    overdueDays: int
    delayDays: int
    stale: bool
    lastUpdateDate: str | None
    potentialDownstream: list[dict[str, Any]]

class IntelligenceResponse(BaseModel):
    projectId: str
    version: str
    evaluatedAt: str
    summary: dict[str, int]
    health: dict[str, HealthDimension]
    dataHealth: dict[str, int | float | str | None]
    activities: list[ActivityIntelligence]
    warnings: list[Warning]
    dependencyRelationships: int
    dependencyImpact: dict[str, Any] | None = None
    warningTotal: int
    activityTotal: int
    limit: int
    offset: int

class MemoryEvent(BaseModel):
    id: str
    kind: str
    occurredAt: str | None
    actor: str | None
    action: str | None
    projectId: str
    details: dict[str, Any]

class MemoryResponse(BaseModel):
    items: list[MemoryEvent]
    total: int
    limit: int
    offset: int
