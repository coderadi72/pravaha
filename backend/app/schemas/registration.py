from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, StrictStr


class SignupRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: StrictStr = Field(min_length=1, max_length=120)
    email: StrictStr = Field(min_length=1, max_length=254)
    password: StrictStr = Field(min_length=1, max_length=128, repr=False)
    confirmPassword: StrictStr = Field(min_length=1, max_length=128, repr=False)
    roleCategory: Literal["MANAGEMENT", "SUPERVISOR"]


class SignupResponse(BaseModel):
    status: Literal["SUBMITTED"]
    message: str


class ApproveRegistrationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    approvedRole: Literal["PROJECT_MANAGER", "DEPARTMENT", "TEAM_LEADER"] | None = None


class RejectRegistrationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    rejectionReason: StrictStr = Field(min_length=1, max_length=500)


class SafeRegistration(BaseModel):
    id: str
    name: str
    email: str
    emailDomain: str
    requestedRoleCategory: Literal["MANAGEMENT", "SUPERVISOR"]
    status: Literal["PENDING", "APPROVED", "REJECTED"]
    reviewOrganizationId: str
    approvedRole: str | None
    organizationId: str | None
    createdAt: str
    updatedAt: str
    reviewedAt: str | None
    rejectionReason: str | None


class RegistrationsResponse(BaseModel):
    registrations: list[SafeRegistration]
    total: int
    offset: int
    limit: int


class RegistrationReviewResponse(BaseModel):
    registration: SafeRegistration
    message: str
