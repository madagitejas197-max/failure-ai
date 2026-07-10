from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy import or_, and_, desc
import uuid

from app.database import get_db
from app.models import Failure, Project, User, ProjectVisibility, FailureCategory, FailureSeverity, FailureStatus, Comment, Tag, failure_tags, UserRole
from app.schemas import FailureResponse, FailureCreate, FailureUpdate, CommentResponse, CommentCreate
from app.core.dependencies import get_current_user
from app.core.secret_scanner import scan_and_redact
from app.core.audit import log_audit_action

router = APIRouter(prefix="/failures", tags=["Failures"])


async def get_or_create_tags(db: AsyncSession, tag_names: List[str]) -> List[Tag]:
    """Helper to retrieve existing tags or create them if they do not exist."""
    if not tag_names:
        return []

    # Clean tag names
    cleaned_names = [name.strip().lower() for name in tag_names if name.strip()]
    if not cleaned_names:
        return []

    # Query existing
    stmt = select(Tag).filter(Tag.name.in_(cleaned_names))
    result = await db.execute(stmt)
    existing_tags = {tag.name: tag for tag in result.scalars().all()}

    tags = []
    for name in cleaned_names:
        if name in existing_tags:
            tags.append(existing_tags[name])
        else:
            new_tag = Tag(name=name)
            db.add(new_tag)
            tags.append(new_tag)

    await db.flush()
    return tags


@router.get(
    "",
    response_model=List[FailureResponse],
    summary="List and filter failure reports",
)
async def list_failures(
    category: Optional[FailureCategory] = None,
    severity: Optional[FailureSeverity] = None,
    tech_stack: Optional[str] = None,  # comma-separated
    project_id: Optional[uuid.UUID] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[Failure]:
    """
    List failures with optional filtering.
    Enforces visibility: public failures, and private/org failures if owned/authored by user or user is admin.
    """
    # Base visibility query
    visibility_filter = or_(
        Failure.visibility == ProjectVisibility.public,
        Failure.author_id == current_user.id,
        current_user.role == UserRole.admin,
    )

    filters = [visibility_filter]

    if category:
        filters.append(Failure.category == category)
    if severity:
        filters.append(Failure.severity == severity)
    if project_id:
        filters.append(Failure.project_id == project_id)
    if tech_stack:
        # Search for any of the tech stack tags
        techs = [t.strip().lower() for t in tech_stack.split(",") if t.strip()]
        for tech in techs:
            filters.append(Failure.tech_stack.any(tech))

    stmt = (
        select(Failure)
        .filter(and_(*filters))
        .options(selectinload(Failure.tags))
        .order_by(desc(Failure.created_at))
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.post(
    "",
    response_model=FailureResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a new failure report",
)
async def create_failure(
    failure_in: FailureCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Failure:
    """Submit a failure report, redact secrets, and link tags."""
    # Perform secret scanning
    logs_redacted = None
    status_val = failure_in.status

    if failure_in.logs:
        redacted, secrets_found = scan_and_redact(failure_in.logs)
        logs_redacted = redacted
        if secrets_found:
            status_val = FailureStatus.flagged

    # If project is linked, verify ownership
    if failure_in.project_id:
        proj_result = await db.execute(select(Project).filter(Project.id == failure_in.project_id))
        project = proj_result.scalars().first()
        if not project:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Linked project not found",
            )
        if project.owner_id != current_user.id and current_user.role != UserRole.admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not own the linked project",
            )

    failure = Failure(
        project_id=failure_in.project_id,
        author_id=current_user.id,
        category=failure_in.category,
        tech_stack=[t.strip().lower() for t in failure_in.tech_stack],
        title=failure_in.title,
        problem=failure_in.problem,
        root_cause=failure_in.root_cause,
        solution=failure_in.solution,
        lesson_learned=failure_in.lesson_learned,
        severity=failure_in.severity,
        logs_redacted=logs_redacted,
        github_url=failure_in.github_url,
        time_to_detect_seconds=failure_in.time_to_detect_seconds,
        time_to_resolve_seconds=failure_in.time_to_resolve_seconds,
        visibility=failure_in.visibility,
        status=status_val,
    )

    # Process and link tech stack tags automatically as Failure Tags
    tags = await get_or_create_tags(db, failure_in.tech_stack)
    failure.tags = tags

    db.add(failure)
    await db.flush()

    # Placeholder for Week 3 Embedding Job
    # background_tasks.add_task(embed_failure_job, failure.id)

    await log_audit_action(
        db,
        action="failure.create",
        resource_type="failure",
        actor_id=current_user.id,
        resource_id=failure.id,
        metadata_json={"title": failure.title, "secrets_redacted": logs_redacted is not None},
    )

    # Load tags for response
    stmt = select(Failure).filter(Failure.id == failure.id).options(selectinload(Failure.tags))
    res = await db.execute(stmt)
    return res.scalars().first()


@router.get(
    "/{id}",
    response_model=FailureResponse,
    summary="Get a failure by ID",
)
async def get_failure(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Failure:
    """Get failure details (visibility checks apply)."""
    stmt = select(Failure).filter(Failure.id == id).options(selectinload(Failure.tags))
    result = await db.execute(stmt)
    failure = result.scalars().first()

    if not failure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Failure report not found",
        )

    # Check access
    if (
        failure.visibility != ProjectVisibility.public
        and failure.author_id != current_user.id
        and current_user.role != UserRole.admin
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this failure report",
        )

    return failure


@router.put(
    "/{id}",
    response_model=FailureResponse,
    summary="Update a failure",
)
async def update_failure(
    id: uuid.UUID,
    failure_in: FailureUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Failure:
    """Update a failure report (author or admin only)."""
    stmt = select(Failure).filter(Failure.id == id).options(selectinload(Failure.tags))
    result = await db.execute(stmt)
    failure = result.scalars().first()

    if not failure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Failure report not found",
        )

    if failure.author_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this failure report",
        )

    # Update fields
    if failure_in.project_id is not None:
        failure.project_id = failure_in.project_id
    if failure_in.category is not None:
        failure.category = failure_in.category
    if failure_in.title is not None:
        failure.title = failure_in.title
    if failure_in.problem is not None:
        failure.problem = failure_in.problem
    if failure_in.root_cause is not None:
        failure.root_cause = failure_in.root_cause
    if failure_in.solution is not None:
        failure.solution = failure_in.solution
    if failure_in.lesson_learned is not None:
        failure.lesson_learned = failure_in.lesson_learned
    if failure_in.severity is not None:
        failure.severity = failure_in.severity
    if failure_in.github_url is not None:
        failure.github_url = failure_in.github_url
    if failure_in.time_to_detect_seconds is not None:
        failure.time_to_detect_seconds = failure_in.time_to_detect_seconds
    if failure_in.time_to_resolve_seconds is not None:
        failure.time_to_resolve_seconds = failure_in.time_to_resolve_seconds
    if failure_in.visibility is not None:
        failure.visibility = failure_in.visibility
    if failure_in.status is not None:
        failure.status = failure_in.status

    if failure_in.tech_stack is not None:
        failure.tech_stack = [t.strip().lower() for t in failure_in.tech_stack]
        tags = await get_or_create_tags(db, failure_in.tech_stack)
        failure.tags = tags

    if failure_in.logs is not None:
        redacted, secrets_found = scan_and_redact(failure_in.logs)
        failure.logs_redacted = redacted
        if secrets_found:
            failure.status = FailureStatus.flagged

    db.add(failure)
    await db.flush()

    await log_audit_action(
        db,
        action="failure.update",
        resource_type="failure",
        actor_id=current_user.id,
        resource_id=failure.id,
    )

    return failure


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete/Archive a failure",
)
async def delete_failure(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Soft-delete/archive a failure report."""
    stmt = select(Failure).filter(Failure.id == id)
    result = await db.execute(stmt)
    failure = result.scalars().first()

    if not failure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Failure report not found",
        )

    if failure.author_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this failure report",
        )

    # Soft delete / archive
    failure.status = FailureStatus.archived
    db.add(failure)
    await db.flush()

    await log_audit_action(
        db,
        action="failure.archive",
        resource_type="failure",
        actor_id=current_user.id,
        resource_id=id,
    )


@router.post(
    "/{id}/upvote",
    response_model=FailureResponse,
    summary="Upvote a failure report",
)
async def upvote_failure(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Failure:
    """Increment upvote count on a failure."""
    stmt = select(Failure).filter(Failure.id == id).options(selectinload(Failure.tags))
    result = await db.execute(stmt)
    failure = result.scalars().first()

    if not failure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Failure report not found",
        )

    failure.upvote_count += 1
    db.add(failure)
    await db.flush()

    return failure


# ── Comments Sub-router ───────────────────────────────────────────────────────
@router.get(
    "/{id}/comments",
    response_model=List[CommentResponse],
    summary="Get comments for a failure report",
)
async def get_comments(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[Comment]:
    """List comments on a failure (visibility checks apply)."""
    # First verify failure is accessible
    stmt = select(Failure).filter(Failure.id == id)
    res = await db.execute(stmt)
    failure = res.scalars().first()

    if not failure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Failure report not found",
        )

    if (
        failure.visibility != ProjectVisibility.public
        and failure.author_id != current_user.id
        and current_user.role != UserRole.admin
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this failure report's comments",
        )

    comment_stmt = (
        select(Comment)
        .filter(Comment.failure_id == id)
        .options(selectinload(Comment.author))
        .order_by(Comment.created_at)
    )
    comment_res = await db.execute(comment_stmt)
    return list(comment_res.scalars().all())


@router.post(
    "/{id}/comments",
    response_model=CommentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a comment to a failure report",
)
async def create_comment(
    id: uuid.UUID,
    comment_in: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Comment:
    """Add a new comment on a failure report."""
    # First verify failure is accessible
    stmt = select(Failure).filter(Failure.id == id)
    res = await db.execute(stmt)
    failure = res.scalars().first()

    if not failure:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Failure report not found",
        )

    if (
        failure.visibility != ProjectVisibility.public
        and failure.author_id != current_user.id
        and current_user.role != UserRole.admin
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this failure report",
        )

    comment = Comment(
        failure_id=id,
        author_id=current_user.id,
        body=comment_in.body,
    )
    db.add(comment)
    await db.flush()

    await log_audit_action(
        db,
        action="comment.create",
        resource_type="comment",
        actor_id=current_user.id,
        resource_id=comment.id,
    )

    # Return with author loaded
    stmt = select(Comment).filter(Comment.id == comment.id).options(selectinload(Comment.author))
    final_res = await db.execute(stmt)
    return final_res.scalars().first()
