import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.domain.models import Processo


class ProcessoRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def criar(self, processo: Processo) -> Processo:
        self._session.add(processo)
        await self._session.commit()
        await self._session.refresh(processo)
        return processo

    async def obter(self, processo_id: uuid.UUID) -> Processo | None:
        return await self._session.get(Processo, processo_id)

    async def listar_por_cliente(self, cliente_id: uuid.UUID) -> list[Processo]:
        consulta = select(Processo).where(Processo.cliente_id == cliente_id).order_by(Processo.nome)
        resultado = await self._session.exec(consulta)
        return list(resultado.all())

    async def atualizar(self, processo: Processo) -> Processo:
        self._session.add(processo)
        await self._session.commit()
        await self._session.refresh(processo)
        return processo
