"""Bounded, strict organization mutation contracts."""
from datetime import date
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, StrictStr


class ValuesRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    values: dict[str, str | int | float | bool | None] = Field(max_length=20)


class TransitionRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    status: StrictStr = Field(max_length=30)


class AllocationRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    employee_id: StrictStr
    project_id: StrictStr
    team_id: StrictStr
    effective_start: date
    transfer: bool = False


class GrantRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    user_id: StrictStr
    capability: Literal['business','materials','people','quality','hse','hr-confidential']
    granted: bool = True


class EndAllocationRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    effective_end: date


class TeamCreateRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    name: StrictStr = Field(min_length=1, max_length=120)
    project_id: StrictStr
    site: StrictStr = Field(default='', max_length=120)


class LinkRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    project_id: StrictStr
    employee_id: StrictStr | None = None
    department_id: StrictStr | None = None
    responsibility: StrictStr = Field(default='Project member', max_length=120)


class SkillRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    employee_id: StrictStr
    skill_id: StrictStr
