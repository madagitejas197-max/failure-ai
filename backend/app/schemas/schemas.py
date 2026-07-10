from datetime import datetime
import uuid
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import UserRole, ProjectVisibility, FailureCategory, FailureSeverity, FailureStatus


# ── Token Schemas ─────────────────────────────────────────────────────────────
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    type: str
    exp: int


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


# ── User Schemas ──────────────────────────────────────────────────────────────
class UserBase(BaseModel):
    email: EmailStr
    display_name: str
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    role: UserRole = UserRole.user
    github_id: Optional[str] = None


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    display_name: str


class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    password: Optional[str] = None


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# ── Project Schemas ───────────────────────────────────────────────────────────
class ProjectBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    tech_stack: List[str] = Field(default_factory=list)
    visibility: ProjectVisibility = ProjectVisibility.public


class ProjectCreate(ProjectBase):
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    visibility: Optional[ProjectVisibility] = None


class ProjectResponse(ProjectBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


# ── Comment Schemas ───────────────────────────────────────────────────────────
class CommentBase(BaseModel):
    body: str


class CommentCreate(CommentBase):
    pass


class CommentResponse(CommentBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    failure_id: uuid.UUID
    author_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    author: UserResponse


# ── Tag Schemas ───────────────────────────────────────────────────────────────
class TagBase(BaseModel):
    name: str = Field(..., max_length=100)
    category: Optional[str] = Field(None, max_length=100)


class TagCreate(TagBase):
    pass


class TagResponse(TagBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID


# ── Failure Schemas ───────────────────────────────────────────────────────────
class FailureBase(BaseModel):
    project_id: Optional[uuid.UUID] = None
    category: FailureCategory
    tech_stack: List[str] = Field(default_factory=list)
    title: str = Field(..., max_length=255)
    problem: str
    root_cause: str
    solution: str
    lesson_learned: str
    severity: FailureSeverity
    github_url: Optional[str] = None
    time_to_detect_seconds: Optional[int] = None
    time_to_resolve_seconds: Optional[int] = None
    visibility: ProjectVisibility = ProjectVisibility.public
    status: FailureStatus = FailureStatus.draft


class FailureCreate(FailureBase):
    # Free-text logs field that undergoes secret scanning & redaction
    logs: Optional[str] = None


class FailureUpdate(BaseModel):
    project_id: Optional[uuid.UUID] = None
    category: Optional[FailureCategory] = None
    tech_stack: Optional[List[str]] = None
    title: Optional[str] = Field(None, max_length=255)
    problem: Optional[str] = None
    root_cause: Optional[str] = None
    solution: Optional[str] = None
    lesson_learned: Optional[str] = None
    severity: Optional[FailureSeverity] = None
    logs: Optional[str] = None
    github_url: Optional[str] = None
    time_to_detect_seconds: Optional[int] = None
    time_to_resolve_seconds: Optional[int] = None
    visibility: Optional[ProjectVisibility] = None
    status: Optional[FailureStatus] = None


class FailureResponse(FailureBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    author_id: uuid.UUID
    logs_redacted: Optional[str] = None
    upvote_count: int
    created_at: datetime
    updated_at: datetime
    tags: List[TagResponse] = Field(default_factory=list)


# ── Audit Log Schemas ─────────────────────────────────────────────────────────
class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    actor_id: Optional[uuid.UUID] = None
    action: str
    resource_type: str
    resource_id: Optional[uuid.UUID] = None
    metadata_json: Optional[dict] = None
    created_at: datetime
