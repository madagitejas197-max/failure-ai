"""create core tables

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-10 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── users ──
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=True),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("avatar_url", sa.String(length=512), nullable=True),
        sa.Column("bio", sa.Text(), nullable=True),
        sa.Column("role", sa.String(length=50), nullable=False, server_default="user"),
        sa.Column("github_id", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("github_id")
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    # ── projects ──
    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("tech_stack", sa.ARRAY(sa.String()), nullable=False),
        sa.Column("visibility", sa.String(length=50), nullable=False, server_default="public"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index(op.f("ix_projects_id"), "projects", ["id"], unique=False)

    # ── failures ──
    op.create_table(
        "failures",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("author_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("tech_stack", sa.ARRAY(sa.String()), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("problem", sa.Text(), nullable=False),
        sa.Column("root_cause", sa.Text(), nullable=False),
        sa.Column("solution", sa.Text(), nullable=False),
        sa.Column("lesson_learned", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(length=50), nullable=False),
        sa.Column("logs_redacted", sa.Text(), nullable=True),
        sa.Column("github_url", sa.String(length=512), nullable=True),
        sa.Column("time_to_detect_seconds", sa.Integer(), nullable=True),
        sa.Column("time_to_resolve_seconds", sa.Integer(), nullable=True),
        sa.Column("visibility", sa.String(length=50), nullable=False, server_default="public"),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="draft"),
        sa.Column("embedding_id", sa.String(length=255), nullable=True),
        sa.Column("upvote_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index(op.f("ix_failures_id"), "failures", ["id"], unique=False)

    # ── comments ──
    op.create_table(
        "comments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("failure_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("author_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["failure_id"], ["failures.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index(op.f("ix_comments_id"), "comments", ["id"], unique=False)

    # ── tags ──
    op.create_table(
        "tags",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index(op.f("ix_tags_id"), "tags", ["id"], unique=False)
    op.create_index(op.f("ix_tags_name"), "tags", ["name"], unique=True)

    # ── failure_tags ──
    op.create_table(
        "failure_tags",
        sa.Column("failure_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tag_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(["failure_id"], ["failures.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["tags.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("failure_id", "tag_id")
    )

    # ── audit_logs ──
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("actor_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("action", sa.String(length=255), nullable=False),
        sa.Column("resource_type", sa.String(length=100), nullable=False),
        sa.Column("resource_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index(op.f("ix_audit_logs_id"), "audit_logs", ["id"], unique=False)


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("failure_tags")
    op.drop_table("tags")
    op.drop_table("comments")
    op.drop_table("failures")
    op.drop_table("projects")
    op.drop_table("users")
