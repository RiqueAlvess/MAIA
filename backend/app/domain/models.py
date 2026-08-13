import uuid
from datetime import datetime
from enum import Enum

from sqlmodel import Field, Relationship, SQLModel


class CamadaDocumento(str, Enum):
    bronze = "bronze"
    as_is = "as_is"
    to_be = "to_be"


class TipoEntregavel(str, Enum):
    word_as_is = "word_as_is"
    excel_gaps = "excel_gaps"
    to_be = "to_be"
    raci = "raci"
    dashboard = "dashboard"
    status_semanal = "status_semanal"
    pauta = "pauta"


class StatusJob(str, Enum):
    pendente = "pendente"
    processando = "processando"
    concluido = "concluido"
    erro = "erro"


class Cliente(SQLModel, table=True):
    __tablename__ = "clientes"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    nome: str = Field(index=True, max_length=200)
    pasta_sharepoint_id: str = Field(max_length=500)
    criado_em: datetime = Field(default_factory=datetime.utcnow)

    processos: list["Processo"] = Relationship(back_populates="cliente")


class Processo(SQLModel, table=True):
    __tablename__ = "processos"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    cliente_id: uuid.UUID = Field(foreign_key="clientes.id", index=True)
    nome: str = Field(max_length=200)
    status_as_is: str = Field(default="nao_iniciado", max_length=50)
    status_to_be: str = Field(default="nao_iniciado", max_length=50)
    criado_em: datetime = Field(default_factory=datetime.utcnow)

    cliente: Cliente | None = Relationship(back_populates="processos")
    documentos: list["Documento"] = Relationship(back_populates="processo")
    entregaveis: list["Entregavel"] = Relationship(back_populates="processo")


class Documento(SQLModel, table=True):
    __tablename__ = "documentos"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    processo_id: uuid.UUID = Field(foreign_key="processos.id", index=True)
    nome: str = Field(max_length=300)
    graph_item_id: str = Field(max_length=500)
    camada: CamadaDocumento
    tamanho_kb: int = Field(default=0)
    criado_em: datetime = Field(default_factory=datetime.utcnow)

    processo: Processo | None = Relationship(back_populates="documentos")


class Entregavel(SQLModel, table=True):
    __tablename__ = "entregaveis"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    processo_id: uuid.UUID = Field(foreign_key="processos.id", index=True)
    tipo: TipoEntregavel
    graph_item_id: str | None = Field(default=None, max_length=500)
    gerado_em: datetime | None = Field(default=None)

    processo: Processo | None = Relationship(back_populates="entregaveis")
    jobs: list["JobGeracao"] = Relationship(back_populates="entregavel")


class JobGeracao(SQLModel, table=True):
    __tablename__ = "jobs_geracao"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    entregavel_id: uuid.UUID = Field(foreign_key="entregaveis.id", index=True)
    status: StatusJob = Field(default=StatusJob.pendente)
    log: str = Field(default="")
    criado_em: datetime = Field(default_factory=datetime.utcnow)
    atualizado_em: datetime = Field(default_factory=datetime.utcnow)

    entregavel: Entregavel | None = Relationship(back_populates="jobs")
