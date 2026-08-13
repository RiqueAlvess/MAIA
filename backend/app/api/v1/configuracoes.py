from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.v1.deps import SettingsDep
from app.core.security import get_current_user
from app.domain.schemas import StatusIntegracoesRead

router = APIRouter(prefix="/configuracoes", tags=["configuracoes"], dependencies=[Depends(get_current_user)])


@router.get("/status", response_model=StatusIntegracoesRead)
async def obter_status(settings: SettingsDep) -> StatusIntegracoesRead:
    return StatusIntegracoesRead(
        ambiente=settings.environment,
        ai_configurado=settings.ai_configurado,
        graph_configurado=settings.graph_configurado,
        auth_configurado=settings.auth_configurado,
        email_configurado=settings.email_configurado,
    )
