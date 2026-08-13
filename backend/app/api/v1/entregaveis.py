import uuid
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status

from app.api.v1.deps import get_entregavel_repo, get_entregavel_service
from app.core.security import get_current_user
from app.domain.models import TipoEntregavel
from app.domain.schemas import EntregavelGerarRequest, JobGeracaoRead
from app.repositories.entregavel_repo import EntregavelRepository
from app.services.entregavel_service import EntregavelService

router = APIRouter(prefix="/entregaveis", tags=["entregaveis"], dependencies=[Depends(get_current_user)])


@router.post("/gerar/{tipo}", response_model=JobGeracaoRead, status_code=status.HTTP_202_ACCEPTED)
async def gerar_entregavel(
    tipo: TipoEntregavel,
    dados: EntregavelGerarRequest,
    background_tasks: BackgroundTasks,
    service: Annotated[EntregavelService, Depends(get_entregavel_service)],
) -> JobGeracaoRead:
    job = await service.iniciar_geracao(dados.processo_id, tipo)
    background_tasks.add_task(service.executar_geracao, job.id)
    return JobGeracaoRead.model_validate(job)


@router.get("/jobs/{job_id}", response_model=JobGeracaoRead)
async def obter_status_job(
    job_id: uuid.UUID,
    repo: Annotated[EntregavelRepository, Depends(get_entregavel_repo)],
) -> JobGeracaoRead:
    job = await repo.obter_job(job_id)
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job não encontrado")
    return JobGeracaoRead.model_validate(job)
