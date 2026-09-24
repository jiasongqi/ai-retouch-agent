"""brand kit json

Revision ID: c3e91b7a4d12
Revises: fa850313b768
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "c3e91b7a4d12"
down_revision = "fa850313b768"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "brand_kit",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
    )
    op.alter_column("users", "brand_kit", server_default=None)


def downgrade() -> None:
    op.drop_column("users", "brand_kit")
