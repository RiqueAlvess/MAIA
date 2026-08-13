import uuid
from datetime import datetime

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.domain.models import Entregavel, JobGeracao, StatusJob


class EntregavelRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def criar_entregavel(self, entregavel: Entregavel) -> Entregavel:
        self._session.add(entregavel)
        await self._session.commit()
        await self._session.refresh(entregavel)
        return entregavel

    async def obter_entregavel(self, entregavel_id: uuid.UUID) -> Entregavel | None:
        return await self._session.get(Entregavel, entregavel_id)

    async def atualizar_entregavel(self, entregavel: Entregavel) -> Entregavel:
        self._session.add(entregavel)
        await self._session.commit()
        await self._session.refresh(entregavel)
        return entregavel

    async def listar_por_processo(self, processo_id: uuid.UUID) -> list[Entregavel]:
        consulta = select(Entregavel).where(Entregavel.processo_id == processo_id).order_by(Entregavel.gerado_em)
        resultado = await self._session.exec(consulta)
        return list(resultado.all())

    async def criar_job(self, job: JobGeracao) -> JobGeracao:
        self._session.add(job)
        await self._session.commit()
        await self._session.refresh(job)
        return job

    async def obter_job(self, job_id: uuid.UUID) -> JobGeracao | None:
        return await self._session.get(JobGeracao, job_id)

    async def atualizar_job(self, job: JobGeracao, status: StatusJob, log: str) -> JobGeracao:
        job.status = status
        job.log = log
        job.atualizado_em = datetime.utcnow()
        self._session.add(job)
        await self._session.commit()
        await self._session.refresh(job)
        return job
