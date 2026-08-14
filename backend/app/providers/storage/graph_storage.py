import urllib.parse

import httpx

from app.providers.graph_auth import GraphTokenClient
from app.providers.storage.base import ArquivoRemoto

GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"

# Delegado: o app age em nome do usuário logado sobre a biblioteca de
# documentos do grupo do setor (Microsoft 365 Group), não um site fixo.
STORAGE_SCOPES = ["Files.ReadWrite.All"]


class GraphStorageProvider:
    """Storage provider baseado na biblioteca de documentos de um grupo do
    Microsoft 365 (/groups/{group_id}/drive), acessada com o token do usuário
    logado via On-Behalf-Of — o usuário só lê/escreve porque é membro do grupo."""

    def __init__(self, group_id: str, token_client: GraphTokenClient):
        self._group_id = group_id
        self._token_client = token_client

    async def _headers(self) -> dict[str, str]:
        return await self._token_client.headers(STORAGE_SCOPES)

    async def listar_documentos(self, pasta_id: str) -> list[ArquivoRemoto]:
        url = f"{GRAPH_BASE_URL}/groups/{self._group_id}/drive/items/{pasta_id}/children"
        async with httpx.AsyncClient(timeout=30) as client:
            resposta = await client.get(url, headers=await self._headers())
            resposta.raise_for_status()
            itens = resposta.json().get("value", [])
        return [
            ArquivoRemoto(item_id=item["id"], nome=item["name"], tamanho_kb=item.get("size", 0) // 1024)
            for item in itens
            if "file" in item
        ]

    async def ler_arquivo(self, item_id: str) -> bytes:
        url = f"{GRAPH_BASE_URL}/groups/{self._group_id}/drive/items/{item_id}/content"
        async with httpx.AsyncClient(timeout=60) as client:
            resposta = await client.get(url, headers=await self._headers())
            resposta.raise_for_status()
            return resposta.content

    async def salvar_arquivo(self, pasta_id: str, nome_arquivo: str, conteudo: bytes) -> str:
        nome_codificado = urllib.parse.quote(nome_arquivo)
        url = f"{GRAPH_BASE_URL}/groups/{self._group_id}/drive/items/{pasta_id}:/{nome_codificado}:/content"
        async with httpx.AsyncClient(timeout=60) as client:
            headers = await self._headers()
            headers["Content-Type"] = "application/octet-stream"
            resposta = await client.put(url, headers=headers, content=conteudo)
            resposta.raise_for_status()
            return resposta.json()["id"]
