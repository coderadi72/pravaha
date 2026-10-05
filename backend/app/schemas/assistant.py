"""Strict read-oriented assistant inputs and validated interpretation output."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field


class Ask(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    project_id: str | None = Field(default=None, max_length=160)
    conversation: str | None = Field(default=None, max_length=30000)
    language: str = Field(default="auto", max_length=16)
    question: str = Field(min_length=1, max_length=4000)
    intent: str | None = Field(default=None, max_length=40)
    activity_id: str | None = Field(default=None, max_length=160)


class ToolArgs(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    activity_id: str | None = Field(default=None, max_length=160)
    query: str = Field(default="", max_length=200)
    recent_days: int | None = Field(default=None, ge=1, le=90)
    at_risk: bool = False
    limit: int = Field(default=12, ge=1, le=50)
    offset: int = Field(default=0, ge=0, le=10000)
    guidance_topic: Literal["submit_help", "review_help", "evidence_help"] | None = None
    conversational: bool = False


class Claim(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    text: str = Field(min_length=1, max_length=1200)
    title: str | None = Field(default=None, max_length=100)
    evidence_ids: list[str] = Field(min_length=1, max_length=12)


class Answer(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    status: Literal["ANSWERED", "INSUFFICIENT_EVIDENCE"]
    claims: list[Claim] = Field(min_length=1, max_length=6)
    assumptions: list[str] = Field(max_length=5)
    uncertainty: list[str] = Field(max_length=5)
    next_investigation: list[str] = Field(max_length=5)


TOOL_NAMES = frozenset({"get_project_summary", "get_project_health", "get_delayed_activities", "get_pending_reviews",
    "get_execution_warnings", "get_schedule_variance", "get_activity_timeline", "get_dependency_impact", "search_project_memory"})
