import time
import urllib.parse

import httpx
import msal

from app.core.config import Settings
from app.providers.storage.base import ArquivoRemoto

GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"


class GraphStorageProvider:
    """Storage provider baseado no Microsoft Graph API (SharePoint/OneDrive), autenticação app-only."""

    def __init__(self, settings: Settings):
        self._settings = settings
        self._site_id = settings.ms_graph_site_id
        self._app: msal.ConfidentialClientApplication | None = None
        self._token: str | None = None
        self._token_expira_em: float = 0.0

    def _obter_app(self) -> msal.ConfidentialClientApplication:
        if not self._settings.graph_configurado:
            raise RuntimeError("Microsoft Graph não configurado (MS_GRAPH_TENANT_ID/CLIENT_ID/CLIENT_SECRET)")
        if self._app is None:
            self._app = msal.ConfidentialClientApplication(
                client_id=self._settings.ms_graph_client_id,
                client_credential=self._settings.ms_graph_client_secret,
                authority=f"https://login.microsoftonline.com/{self._settings.ms_graph_tenant_id}",
            )
        return self._app

    async def _obter_token(self) -> str:
        if self._token and time.time() < self._token_expira_em - 60:
            return self._token
        resultado = self._obter_app().acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
        if "access_token" not in resultado:
            detalhe = resultado.get("error_description", resultado)
            raise RuntimeError(f"Falha ao autenticar no Microsoft Graph: {detalhe}")
        self._token = resultado["access_token"]
        self._token_expira_em = time.time() + resultado.get("expires_in", 3600)
        return self._token

    async def _headers(self) -> dict[str, str]:
        token = await self._obter_token()
        return {"Authorization": f"Bearer {token}"}

    async def listar_documentos(self, pasta_id: str) -> list[ArquivoRemoto]:
        url = f"{GRAPH_BASE_URL}/sites/{self._site_id}/drive/items/{pasta_id}/children"
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
        url = f"{GRAPH_BASE_URL}/sites/{self._site_id}/drive/items/{item_id}/content"
        async with httpx.AsyncClient(timeout=60) as client:
            resposta = await client.get(url, headers=await self._headers())
            resposta.raise_for_status()
            return resposta.content

    async def salvar_arquivo(self, pasta_id: str, nome_arquivo: str, conteudo: bytes) -> str:
        nome_codificado = urllib.parse.quote(nome_arquivo)
        url = f"{GRAPH_BASE_URL}/sites/{self._site_id}/drive/items/{pasta_id}:/{nome_codificado}:/content"
        async with httpx.AsyncClient(timeout=60) as client:
            headers = await self._headers()
            headers["Content-Type"] = "application/octet-stream"
            resposta = await client.put(url, headers=headers, content=conteudo)
            resposta.raise_for_status()
            return resposta.json()["id"]
