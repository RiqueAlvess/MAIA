import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.v1.deps import get_relatorio_service
from app.core.security import get_current_user
from app.domain.models import TipoEntregavel
from app.domain.schemas import EntregavelHistoricoRead, RelatorioEmailRequest
from app.services.relatorio_service import RelatorioService

router = APIRouter(prefix="/relatorios", tags=["relatorios"], dependencies=[Depends(get_current_user)])


@router.get("/entregaveis", response_model=list[EntregavelHistoricoRead])
async def listar_historico(
    service: Annotated[RelatorioService, Depends(get_relatorio_service)],
    cliente_id: Annotated[uuid.UUID | None, Query()] = None,
    tipo: Annotated[TipoEntregavel | None, Query()] = None,
) -> list[EntregavelHistoricoRead]:
    return await service.listar_historico(cliente_id=cliente_id, tipo=tipo)


@router.post("/enviar-email", status_code=status.HTTP_204_NO_CONTENT)
async def enviar_email(
    dados: RelatorioEmailRequest,
    service: Annotated[RelatorioService, Depends(get_relatorio_service)],
) -> None:
    try:
        await service.enviar_email(dados.cliente_id, dados.processo_id, dados.destinatarios)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
