import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AuditLog


async def log_audit_action(
    db: AsyncSession,
    action: str,
    resource_type: str,
    actor_id: Optional[uuid.UUID] = None,
    resource_id: Optional[uuid.UUID] = None,
    metadata_json: Optional[dict] = None,
) -> AuditLog:
    """Helper to asynchronously write a mutation event to the audit_logs database table."""
    audit_log = AuditLog(
        actor_id=actor_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        metadata_json=metadata_json,
    )
    db.add(audit_log)
    await db.flush()
    return audit_log
