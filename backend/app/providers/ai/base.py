from typing import Protocol


class AIProvider(Protocol):
    async def gerar_texto(self, prompt_sistema: str, prompt_usuario: str) -> str: ...
