import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.v1.deps import get_cliente_service
from app.core.security import get_current_user
from app.domain.schemas import ClienteCreate, ClienteRead
from app.services.cliente_service import ClienteService

router = APIRouter(prefix="/clientes", tags=["clientes"], dependencies=[Depends(get_current_user)])


@router.post("", response_model=ClienteRead, status_code=status.HTTP_201_CREATED)
async def criar_cliente(
    dados: ClienteCreate,
    service: Annotated[ClienteService, Depends(get_cliente_service)],
) -> ClienteRead:
    cliente = await service.criar(dados)
    return ClienteRead.model_validate(cliente)


@router.get("", response_model=list[ClienteRead])
async def listar_clientes(
    service: Annotated[ClienteService, Depends(get_cliente_service)],
) -> list[ClienteRead]:
    clientes = await service.listar()
    return [ClienteRead.model_validate(cliente) for cliente in clientes]


@router.get("/{cliente_id}", response_model=ClienteRead)
async def obter_cliente(
    cliente_id: uuid.UUID,
    service: Annotated[ClienteService, Depends(get_cliente_service)],
) -> ClienteRead:
    cliente = await service.obter(cliente_id)
    if cliente is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente não encontrado")
    return ClienteRead.model_validate(cliente)
