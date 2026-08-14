import httpx

from app.providers.graph_auth import GraphTokenClient

GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"

# Delegado: o e-mail sai da caixa do próprio usuário logado (/me/sendMail),
# não de uma caixa remetente fixa de aplicativo.
EMAIL_SCOPES = ["Mail.Send"]


class GraphEmailProvider:
    """Envia e-mail via Microsoft Graph (POST /me/sendMail) em nome do
    usuário logado, usando o token obtido via On-Behalf-Of. Requer a
    permissão delegada Mail.Send (com consentimento de admin) no app
    registration usado para o Graph."""

    def __init__(self, token_client: GraphTokenClient):
        self._token_client = token_client

    async def enviar(self, destinatarios: list[str], assunto: str, corpo_html: str) -> None:
        if not destinatarios:
            raise ValueError("Informe ao menos um destinatário")

        url = f"{GRAPH_BASE_URL}/me/sendMail"
        payload = {
            "message": {
                "subject": assunto,
                "body": {"contentType": "HTML", "content": corpo_html},
                "toRecipients": [{"emailAddress": {"address": destinatario}} for destinatario in destinatarios],
            },
            "saveToSentItems": "true",
        }
        headers = await self._token_client.headers(EMAIL_SCOPES)
        async with httpx.AsyncClient(timeout=30) as client:
            resposta = await client.post(url, headers=headers, json=payload)
            resposta.raise_for_status()
