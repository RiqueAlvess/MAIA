from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import Settings, get_settings
from app.core.security import get_bearer_token
from app.db.session import get_session
from app.providers.ai.claude_provider import ClaudeProvider
from app.providers.email.graph_email import GraphEmailProvider
from app.providers.graph_auth import GraphTokenClient
from app.providers.storage.graph_storage import GraphStorageProvider
from app.repositories.cliente_repo import ClienteRepository
from app.repositories.documento_repo import DocumentoRepository
from app.repositories.entregavel_repo import EntregavelRepository
from app.repositories.processo_repo import ProcessoRepository
from app.services.cliente_service import ClienteService
from app.services.entregavel_service import EntregavelService
from app.services.processo_service import ProcessoService
from app.services.relatorio_service import RelatorioService

SessionDep = Annotated[AsyncSession, Depends(get_session)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


def get_cliente_repo(session: SessionDep) -> ClienteRepository:
    return ClienteRepository(session)


def get_processo_repo(session: SessionDep) -> ProcessoRepository:
    return ProcessoRepository(session)


def get_documento_repo(session: SessionDep) -> DocumentoRepository:
    return DocumentoRepository(session)


def get_entregavel_repo(session: SessionDep) -> EntregavelRepository:
    return EntregavelRepository(session)


def get_graph_token_client(
    settings: SettingsDep,
    user_token: Annotated[str | None, Depends(get_bearer_token)],
) -> GraphTokenClient:
    return GraphTokenClient(settings, user_token)


def get_storage_provider(
    settings: SettingsDep,
    token_client: Annotated[GraphTokenClient, Depends(get_graph_token_client)],
) -> GraphStorageProvider:
    return GraphStorageProvider(settings.ms_graph_group_id, token_client)


def get_ai_provider(settings: SettingsDep) -> ClaudeProvider:
    return ClaudeProvider(settings)


def get_email_provider(
    token_client: Annotated[GraphTokenClient, Depends(get_graph_token_client)],
) -> GraphEmailProvider:
    return GraphEmailProvider(token_client)


def get_cliente_service(repo: Annotated[ClienteRepository, Depends(get_cliente_repo)]) -> ClienteService:
    return ClienteService(repo)


def get_processo_service(repo: Annotated[ProcessoRepository, Depends(get_processo_repo)]) -> ProcessoService:
    return ProcessoService(repo)


def get_entregavel_service(
    entregavel_repo: Annotated[EntregavelRepository, Depends(get_entregavel_repo)],
    processo_repo: Annotated[ProcessoRepository, Depends(get_processo_repo)],
    cliente_repo: Annotated[ClienteRepository, Depends(get_cliente_repo)],
    documento_repo: Annotated[DocumentoRepository, Depends(get_documento_repo)],
    storage: Annotated[GraphStorageProvider, Depends(get_storage_provider)],
    ai: Annotated[ClaudeProvider, Depends(get_ai_provider)],
) -> EntregavelService:
    return EntregavelService(entregavel_repo, processo_repo, cliente_repo, documento_repo, storage, ai)


def get_relatorio_service(
    entregavel_repo: Annotated[EntregavelRepository, Depends(get_entregavel_repo)],
    cliente_repo: Annotated[ClienteRepository, Depends(get_cliente_repo)],
    email: Annotated[GraphEmailProvider, Depends(get_email_provider)],
) -> RelatorioService:
    return RelatorioService(entregavel_repo, cliente_repo, email)
