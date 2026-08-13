import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.v1.deps import get_processo_service
from app.core.security import get_current_user
from app.domain.schemas import ProcessoCreate, ProcessoRead
from app.services.processo_service import ProcessoService

router = APIRouter(prefix="/processos", tags=["processos"], dependencies=[Depends(get_current_user)])


@router.post("", response_model=ProcessoRead, status_code=status.HTTP_201_CREATED)
async def criar_processo(
    dados: ProcessoCreate,
    service: Annotated[ProcessoService, Depends(get_processo_service)],
) -> ProcessoRead:
    processo = await service.criar(dados)
    return ProcessoRead.model_validate(processo)


@router.get("", response_model=list[ProcessoRead])
async def listar_processos(
    service: Annotated[ProcessoService, Depends(get_processo_service)],
    cliente_id: Annotated[uuid.UUID, Query()],
) -> list[ProcessoRead]:
    processos = await service.listar_por_cliente(cliente_id)
    return [ProcessoRead.model_validate(processo) for processo in processos]


@router.get("/{processo_id}", response_model=ProcessoRead)
async def obter_processo(
    processo_id: uuid.UUID,
    service: Annotated[ProcessoService, Depends(get_processo_service)],
) -> ProcessoRead:
    processo = await service.obter(processo_id)
    if processo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Processo não encontrado")
    return ProcessoRead.model_validate(processo)
