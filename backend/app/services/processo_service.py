import uuid

from app.domain.models import Processo
from app.domain.schemas import ProcessoCreate
from app.repositories.processo_repo import ProcessoRepository


class ProcessoService:
    def __init__(self, repo: ProcessoRepository):
        self._repo = repo

    async def criar(self, dados: ProcessoCreate) -> Processo:
        processo = Processo(cliente_id=dados.cliente_id, nome=dados.nome)
        return await self._repo.criar(processo)

    async def obter(self, processo_id: uuid.UUID) -> Processo | None:
        return await self._repo.obter(processo_id)

    async def listar_por_cliente(self, cliente_id: uuid.UUID) -> list[Processo]:
        return await self._repo.listar_por_cliente(cliente_id)

    async def listar_todos(self) -> list[Processo]:
        return await self._repo.listar_todos()
