import urllib.parse

import httpx

from app.core.config import Settings
from app.providers.graph_auth import GraphTokenClient
from app.providers.storage.base import ArquivoRemoto

GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"


class GraphStorageProvider:
    """Storage provider baseado no Microsoft Graph API (SharePoint/OneDrive), autenticação app-only."""

    def __init__(self, settings: Settings, token_client: GraphTokenClient | None = None):
        self._site_id = settings.ms_graph_site_id
        self._token_client = token_client or GraphTokenClient(settings)

    async def listar_documentos(self, pasta_id: str) -> list[ArquivoRemoto]:
        url = f"{GRAPH_BASE_URL}/sites/{self._site_id}/drive/items/{pasta_id}/children"
        async with httpx.AsyncClient(timeout=30) as client:
            resposta = await client.get(url, headers=await self._token_client.headers())
            resposta.raise_for_status()
            itens = resposta.json().get("value", [])
        return [
            ArquivoRemoto(item_id=item["id"], nome=item["name"], tamanho_kb=item.get("size", 0) // 1024)
            for item in itens
            if "file" in item
        ]

    async def ler_arquivo(self, item_id: str) -> bytes:
        url = f"{GRAPH_BASE_URL}/sites/{self._site_id}/drive/items/{item_id}/content"
        async with httpx.AsyncClient(timeout=60) as client:
            resposta = await client.get(url, headers=await self._token_client.headers())
            resposta.raise_for_status()
            return resposta.content

    async def salvar_arquivo(self, pasta_id: str, nome_arquivo: str, conteudo: bytes) -> str:
        nome_codificado = urllib.parse.quote(nome_arquivo)
        url = f"{GRAPH_BASE_URL}/sites/{self._site_id}/drive/items/{pasta_id}:/{nome_codificado}:/content"
        async with httpx.AsyncClient(timeout=60) as client:
            headers = await self._token_client.headers()
            headers["Content-Type"] = "application/octet-stream"
            resposta = await client.put(url, headers=headers, content=conteudo)
            resposta.raise_for_status()
            return resposta.json()["id"]
