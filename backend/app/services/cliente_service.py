import uuid

from app.domain.models import Cliente
from app.domain.schemas import ClienteCreate
from app.repositories.cliente_repo import ClienteRepository


class ClienteService:
    def __init__(self, repo: ClienteRepository):
        self._repo = repo

    async def criar(self, dados: ClienteCreate) -> Cliente:
        cliente = Cliente(nome=dados.nome, pasta_sharepoint_id=dados.pasta_sharepoint_id)
        return await self._repo.criar(cliente)

    async def obter(self, cliente_id: uuid.UUID) -> Cliente | None:
        return await self._repo.obter(cliente_id)

    async def listar(self) -> list[Cliente]:
        return await self._repo.listar()
