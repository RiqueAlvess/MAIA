import httpx

from app.core.config import Settings

ANTHROPIC_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"


class ClaudeProvider:
    def __init__(self, settings: Settings):
        self._api_key = settings.anthropic_api_key
        self._model = settings.anthropic_model
        self._max_tokens = settings.anthropic_max_tokens

    async def gerar_texto(self, prompt_sistema: str, prompt_usuario: str) -> str:
        if not self._api_key:
            raise RuntimeError("ANTHROPIC_API_KEY não configurada")

        payload = {
            "model": self._model,
            "max_tokens": self._max_tokens,
            "system": prompt_sistema,
            "messages": [{"role": "user", "content": prompt_usuario}],
        }
        headers = {
            "x-api-key": self._api_key,
            "anthropic-version": ANTHROPIC_VERSION,
            "content-type": "application/json",
        }
        async with httpx.AsyncClient(timeout=120) as client:
            resposta = await client.post(ANTHROPIC_URL, json=payload, headers=headers)
            resposta.raise_for_status()
            dados = resposta.json()

        return "".join(bloco["text"] for bloco in dados["content"] if bloco["type"] == "text")
