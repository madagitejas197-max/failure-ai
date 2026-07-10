from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
import uuid

from app.database import get_db
from app.models import Project, User, ProjectVisibility, UserRole
from app.schemas import ProjectResponse, ProjectCreate, ProjectUpdate
from app.core.dependencies import get_current_user
from app.core.audit import log_audit_action

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.get(
    "",
    response_model=List[ProjectResponse],
    summary="List all accessible projects",
)
async def list_projects(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> List[Project]:
    """
    List all projects.
    Returns public projects, and private/org projects if owned by the current user.
    """
    stmt = select(Project).filter(
        or_(
            Project.visibility == ProjectVisibility.public,
            Project.owner_id == current_user.id,
        )
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project",
)
async def create_project(
    project_in: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Project:
    """Create a new project owned by the current user."""
    project = Project(
        owner_id=current_user.id,
        name=project_in.name,
        description=project_in.description,
        tech_stack=project_in.tech_stack,
        visibility=project_in.visibility,
    )
    db.add(project)
    await db.flush()

    await log_audit_action(
        db,
        action="project.create",
        resource_type="project",
        actor_id=current_user.id,
        resource_id=project.id,
        metadata_json={"name": project.name},
    )

    return project


@router.get(
    "/{id}",
    response_model=ProjectResponse,
    summary="Get a project by ID",
)
async def get_project(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Project:
    """Get project details if accessible (public or owned by user)."""
    result = await db.execute(select(Project).filter(Project.id == id))
    project = result.scalars().first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Check access
    if (
        project.visibility != ProjectVisibility.public
        and project.owner_id != current_user.id
        and current_user.role != UserRole.admin
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this project",
        )

    return project


@router.put(
    "/{id}",
    response_model=ProjectResponse,
    summary="Update a project",
)
async def update_project(
    id: uuid.UUID,
    project_in: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Project:
    """Update project details (owner only)."""
    result = await db.execute(select(Project).filter(Project.id == id))
    project = result.scalars().first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if project.owner_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this project",
        )

    # Update fields
    if project_in.name is not None:
        project.name = project_in.name
    if project_in.description is not None:
        project.description = project_in.description
    if project_in.tech_stack is not None:
        project.tech_stack = project_in.tech_stack
    if project_in.visibility is not None:
        project.visibility = project_in.visibility

    db.add(project)
    await db.flush()

    await log_audit_action(
        db,
        action="project.update",
        resource_type="project",
        actor_id=current_user.id,
        resource_id=project.id,
    )

    return project


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a project",
)
async def delete_project(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a project (owner or admin only)."""
    result = await db.execute(select(Project).filter(Project.id == id))
    project = result.scalars().first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if project.owner_id != current_user.id and current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this project",
        )

    await db.delete(project)
    await db.flush()

    await log_audit_action(
        db,
        action="project.delete",
        resource_type="project",
        actor_id=current_user.id,
        resource_id=id,
    )
