"""initial_empty

Revision ID: 0001
Revises:
Create Date: 2026-07-10

Initial empty migration — no tables yet.
Tables will be added in Week 2 (CRUD phase).
"""
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Week 1: No tables. Schema added in 0002_create_core_tables.py (Week 2).
    pass


def downgrade() -> None:
    pass
