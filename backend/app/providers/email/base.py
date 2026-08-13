from typing import Protocol


class EmailProvider(Protocol):
    async def enviar(self, destinatarios: list[str], assunto: str, corpo_html: str) -> None: ...
