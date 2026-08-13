from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.session import get_session
from app.providers.ai.claude_provider import ClaudeProvider
from app.providers.storage.graph_storage import GraphStorageProvider
from app.repositories.cliente_repo import ClienteRepository
from app.repositories.documento_repo import DocumentoRepository
from app.repositories.entregavel_repo import EntregavelRepository
from app.repositories.processo_repo import ProcessoRepository
from app.services.cliente_service import ClienteService
from app.services.entregavel_service import EntregavelService
from app.services.processo_service import ProcessoService

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


def get_storage_provider(settings: SettingsDep) -> GraphStorageProvider:
    return GraphStorageProvider(settings)


def get_ai_provider(settings: SettingsDep) -> ClaudeProvider:
    return ClaudeProvider(settings)


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
