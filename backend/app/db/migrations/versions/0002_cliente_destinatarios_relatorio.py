"""adiciona destinatarios_relatorio em clientes

Revision ID: 0002
Revises: 0001
Create Date: 2026-08-13

"""
from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "clientes",
        sa.Column(
            "destinatarios_relatorio",
            sqlmodel.sql.sqltypes.AutoString(length=1000),
            nullable=False,
            server_default="",
        ),
    )


def downgrade() -> None:
    op.drop_column("clientes", "destinatarios_relatorio")
