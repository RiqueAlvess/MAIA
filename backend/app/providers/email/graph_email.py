import httpx

from app.core.config import Settings
from app.providers.graph_auth import GraphTokenClient

GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"


class GraphEmailProvider:
    """Envia e-mail via Microsoft Graph (POST /users/{upn}/sendMail), autenticação app-only.

    Requer a permissão de aplicativo Mail.Send (com consentimento de admin) no
    mesmo app registration usado para o Graph Storage, e uma caixa de correio
    remetente configurada em MS_GRAPH_SENDER_UPN.
    """

    def __init__(self, settings: Settings, token_client: GraphTokenClient | None = None):
        self._settings = settings
        self._token_client = token_client or GraphTokenClient(settings)

    async def enviar(self, destinatarios: list[str], assunto: str, corpo_html: str) -> None:
        if not self._settings.email_configurado:
            raise RuntimeError(
                "Envio de e-mail não configurado (defina MS_GRAPH_SENDER_UPN além das credenciais do Graph)"
            )
        if not destinatarios:
            raise ValueError("Informe ao menos um destinatário")

        url = f"{GRAPH_BASE_URL}/users/{self._settings.ms_graph_sender_upn}/sendMail"
        payload = {
            "message": {
                "subject": assunto,
                "body": {"contentType": "HTML", "content": corpo_html},
                "toRecipients": [{"emailAddress": {"address": destinatario}} for destinatario in destinatarios],
            },
            "saveToSentItems": "true",
        }
        headers = await self._token_client.headers()
        async with httpx.AsyncClient(timeout=30) as client:
            resposta = await client.post(url, headers=headers, json=payload)
            resposta.raise_for_status()
