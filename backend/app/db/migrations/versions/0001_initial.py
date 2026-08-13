"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-08-13

"""
from typing import Sequence, Union

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "clientes",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("nome", sqlmodel.sql.sqltypes.AutoString(length=200), nullable=False),
        sa.Column("pasta_sharepoint_id", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=False),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_clientes_nome"), "clientes", ["nome"], unique=False)

    op.create_table(
        "processos",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("cliente_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("nome", sqlmodel.sql.sqltypes.AutoString(length=200), nullable=False),
        sa.Column("status_as_is", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column("status_to_be", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["cliente_id"], ["clientes.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_processos_cliente_id"), "processos", ["cliente_id"], unique=False)

    op.create_table(
        "documentos",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("processo_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("nome", sqlmodel.sql.sqltypes.AutoString(length=300), nullable=False),
        sa.Column("graph_item_id", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=False),
        sa.Column("camada", sa.Enum("bronze", "as_is", "to_be", name="camadadocumento"), nullable=False),
        sa.Column("tamanho_kb", sa.Integer(), nullable=False),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["processo_id"], ["processos.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_documentos_processo_id"), "documentos", ["processo_id"], unique=False)

    op.create_table(
        "entregaveis",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("processo_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column(
            "tipo",
            sa.Enum(
                "word_as_is",
                "excel_gaps",
                "to_be",
                "raci",
                "dashboard",
                "status_semanal",
                "pauta",
                name="tipoentregavel",
            ),
            nullable=False,
        ),
        sa.Column("graph_item_id", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
        sa.Column("gerado_em", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["processo_id"], ["processos.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_entregaveis_processo_id"), "entregaveis", ["processo_id"], unique=False)

    op.create_table(
        "jobs_geracao",
        sa.Column("id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column("entregavel_id", sqlmodel.sql.sqltypes.GUID(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pendente", "processando", "concluido", "erro", name="statusjob"),
            nullable=False,
        ),
        sa.Column("log", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["entregavel_id"], ["entregaveis.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_jobs_geracao_entregavel_id"), "jobs_geracao", ["entregavel_id"], unique=False)


def downgrade() -> None:
    op.drop_table("jobs_geracao")
    op.drop_table("entregaveis")
    op.drop_table("documentos")
    op.drop_table("processos")
    op.drop_table("clientes")
    sa.Enum(name="statusjob").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="tipoentregavel").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="camadadocumento").drop(op.get_bind(), checkfirst=True)
