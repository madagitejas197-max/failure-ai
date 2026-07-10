import enum
import uuid
from typing import List, Optional
from sqlalchemy import String, Text, ForeignKey, Table, Column, DateTime, Integer, Numeric, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.models.base import ModelBase

# Association Table for Failure <-> Tag (M:N)
failure_tags = Table(
    "failure_tags",
    ModelBase.metadata,
    Column("failure_id", UUID(as_uuid=True), ForeignKey("failures.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)

class UserRole(str, enum.Enum):
    user = "user"
    moderator = "moderator"
    admin = "admin"

class ProjectVisibility(str, enum.Enum):
    public = "public"
    org = "org"
    private = "private"

class FailureCategory(str, enum.Enum):
    architecture = "architecture"
    security = "security"
    performance = "performance"
    deployment = "deployment"
    scaling = "scaling"
    data = "data"
    other = "other"

class FailureSeverity(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class FailureStatus(str, enum.Enum):
    draft = "draft"
    published = "published"
    flagged = "flagged"
    archived = "archived"

class User(ModelBase):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    role: Mapped[UserRole] = mapped_column(String(50), default=UserRole.user, nullable=False)
    github_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, unique=True)

    # Relationships
    projects: Mapped[List["Project"]] = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    failures: Mapped[List["Failure"]] = relationship("Failure", back_populates="author", cascade="all, delete-orphan")
    comments: Mapped[List["Comment"]] = relationship("Comment", back_populates="author", cascade="all, delete-orphan")
    audit_logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="actor")

class Project(ModelBase):
    __tablename__ = "projects"

    owner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    tech_stack: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    visibility: Mapped[ProjectVisibility] = mapped_column(String(50), default=ProjectVisibility.public, nullable=False)

    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="projects")
    failures: Mapped[List["Failure"]] = relationship("Failure", back_populates="project", cascade="all, delete-orphan")

class Failure(ModelBase):
    __tablename__ = "failures"

    project_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    author_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    category: Mapped[FailureCategory] = mapped_column(String(50), nullable=False)
    tech_stack: Mapped[List[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    problem: Mapped[str] = mapped_column(Text, nullable=False)
    root_cause: Mapped[str] = mapped_column(Text, nullable=False)
    solution: Mapped[str] = mapped_column(Text, nullable=False)
    lesson_learned: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[FailureSeverity] = mapped_column(String(50), nullable=False)
    logs_redacted: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    github_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True)
    time_to_detect_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    time_to_resolve_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    visibility: Mapped[ProjectVisibility] = mapped_column(String(50), default=ProjectVisibility.public, nullable=False)
    status: Mapped[FailureStatus] = mapped_column(String(50), default=FailureStatus.draft, nullable=False)
    embedding_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    upvote_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Relationships
    project: Mapped[Optional["Project"]] = relationship("Project", back_populates="failures")
    author: Mapped["User"] = relationship("User", back_populates="failures")
    comments: Mapped[List["Comment"]] = relationship("Comment", back_populates="failure", cascade="all, delete-orphan")
    tags: Mapped[List["Tag"]] = relationship("Tag", secondary=failure_tags, back_populates="failures")

class Comment(ModelBase):
    __tablename__ = "comments"

    failure_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("failures.id", ondelete="CASCADE"), nullable=False)
    author_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)

    # Relationships
    failure: Mapped["Failure"] = relationship("Failure", back_populates="comments")
    author: Mapped["User"] = relationship("User", back_populates="comments")

class Tag(ModelBase):
    __tablename__ = "tags"

    name: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Relationships
    failures: Mapped[List["Failure"]] = relationship("Failure", secondary=failure_tags, back_populates="tags")

class AuditLog(ModelBase):
    __tablename__ = "audit_logs"

    actor_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), nullable=True)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Relationships
    actor: Mapped[Optional["User"]] = relationship("User", back_populates="audit_logs")
