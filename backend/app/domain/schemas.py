import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.domain.models import CamadaDocumento, StatusJob, TipoEntregavel


class ClienteCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=200)
    pasta_sharepoint_id: str = Field(min_length=1, max_length=500)


class ClienteRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    nome: str
    pasta_sharepoint_id: str
    destinatarios_relatorio: str
    criado_em: datetime


class ClienteAtualizarDestinatarios(BaseModel):
    destinatarios_relatorio: str = Field(default="", max_length=1000)


class ProcessoCreate(BaseModel):
    cliente_id: uuid.UUID
    nome: str = Field(min_length=1, max_length=200)


class ProcessoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    cliente_id: uuid.UUID
    nome: str
    status_as_is: str
    status_to_be: str
    criado_em: datetime
    cliente_nome: str | None = None


class DocumentoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    processo_id: uuid.UUID
    nome: str
    camada: CamadaDocumento
    tamanho_kb: int
    criado_em: datetime


class EntregavelGerarRequest(BaseModel):
    processo_id: uuid.UUID


class EntregavelRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    processo_id: uuid.UUID
    tipo: TipoEntregavel
    gerado_em: datetime | None


class JobGeracaoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    entregavel_id: uuid.UUID
    status: StatusJob
    log: str
    criado_em: datetime
    atualizado_em: datetime


class EntregavelHistoricoRead(BaseModel):
    id: uuid.UUID
    tipo: TipoEntregavel
    processo_id: uuid.UUID
    processo_nome: str
    cliente_id: uuid.UUID
    cliente_nome: str
    gerado_em: datetime | None
    status: StatusJob | None
    status_log: str


class RelatorioEmailRequest(BaseModel):
    cliente_id: uuid.UUID
    processo_id: uuid.UUID | None = None
    destinatarios: list[str] | None = None


class StatusIntegracoesRead(BaseModel):
    ambiente: str
    ai_configurado: bool
    graph_configurado: bool
    auth_configurado: bool
    email_configurado: bool
