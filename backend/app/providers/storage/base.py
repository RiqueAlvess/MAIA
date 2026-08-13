from dataclasses import dataclass
from typing import Protocol


@dataclass
class ArquivoRemoto:
    item_id: str
    nome: str
    tamanho_kb: int


class StorageProvider(Protocol):
    async def listar_documentos(self, pasta_id: str) -> list[ArquivoRemoto]: ...

    async def ler_arquivo(self, item_id: str) -> bytes: ...

    async def salvar_arquivo(self, pasta_id: str, nome_arquivo: str, conteudo: bytes) -> str: ...
