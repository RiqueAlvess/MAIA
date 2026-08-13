import uuid

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.domain.models import CamadaDocumento, Documento


class DocumentoRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def criar(self, documento: Documento) -> Documento:
        self._session.add(documento)
        await self._session.commit()
        await self._session.refresh(documento)
        return documento

    async def listar_por_processo(self, processo_id: uuid.UUID) -> list[Documento]:
        consulta = select(Documento).where(Documento.processo_id == processo_id).order_by(Documento.nome)
        resultado = await self._session.exec(consulta)
        return list(resultado.all())

    async def listar_por_camada(self, processo_id: uuid.UUID, camada: CamadaDocumento) -> list[Documento]:
        consulta = (
            select(Documento)
            .where(Documento.processo_id == processo_id, Documento.camada == camada)
            .order_by(Documento.nome)
        )
        resultado = await self._session.exec(consulta)
        return list(resultado.all())
