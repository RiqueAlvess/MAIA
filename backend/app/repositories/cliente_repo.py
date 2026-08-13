import uuid

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.domain.models import Cliente


class ClienteRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def criar(self, cliente: Cliente) -> Cliente:
        self._session.add(cliente)
        await self._session.commit()
        await self._session.refresh(cliente)
        return cliente

    async def obter(self, cliente_id: uuid.UUID) -> Cliente | None:
        return await self._session.get(Cliente, cliente_id)

    async def listar(self) -> list[Cliente]:
        resultado = await self._session.exec(select(Cliente).order_by(Cliente.nome))
        return list(resultado.all())

    async def atualizar(self, cliente: Cliente) -> Cliente:
        self._session.add(cliente)
        await self._session.commit()
        await self._session.refresh(cliente)
        return cliente
