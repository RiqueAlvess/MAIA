import html
import uuid

from app.domain.models import TipoEntregavel
from app.domain.schemas import EntregavelHistoricoRead
from app.providers.email.base import EmailProvider
from app.repositories.cliente_repo import ClienteRepository
from app.repositories.entregavel_repo import EntregavelRepository
from app.services.entregavel_service import ROTULOS_ENTREGAVEL


class RelatorioService:
    def __init__(
        self,
        entregavel_repo: EntregavelRepository,
        cliente_repo: ClienteRepository,
        email: EmailProvider,
    ):
        self._entregaveis = entregavel_repo
        self._clientes = cliente_repo
        self._email = email

    async def listar_historico(
        self, cliente_id: uuid.UUID | None = None, tipo: TipoEntregavel | None = None
    ) -> list[EntregavelHistoricoRead]:
        linhas = await self._entregaveis.listar_historico(cliente_id=cliente_id, tipo=tipo)
        return [
            EntregavelHistoricoRead(
                id=entregavel.id,
                tipo=entregavel.tipo,
                processo_id=processo.id,
                processo_nome=processo.nome,
                cliente_id=cliente.id,
                cliente_nome=cliente.nome,
                gerado_em=entregavel.gerado_em,
                status=job.status if job else None,
                status_log=job.log if job else "",
            )
            for entregavel, processo, cliente, job in linhas
        ]

    async def enviar_email(
        self,
        cliente_id: uuid.UUID,
        processo_id: uuid.UUID | None,
        destinatarios_override: list[str] | None,
    ) -> None:
        cliente = await self._clientes.obter(cliente_id)
        if cliente is None:
            raise ValueError("Cliente não encontrado")

        destinatarios = destinatarios_override or self._parse_destinatarios(cliente.destinatarios_relatorio)
        if not destinatarios:
            raise ValueError("Nenhum destinatário informado nem cadastrado para este cliente")

        historico = await self.listar_historico(cliente_id=cliente_id)
        if processo_id is not None:
            historico = [item for item in historico if item.processo_id == processo_id]

        assunto = f"MAIA — Relatório de entregáveis · {cliente.nome}"
        corpo_html = self._montar_corpo_html(cliente.nome, historico)
        await self._email.enviar(destinatarios, assunto, corpo_html)

    @staticmethod
    def _parse_destinatarios(valor: str) -> list[str]:
        return [item.strip() for item in valor.split(",") if item.strip()]

    @staticmethod
    def _montar_corpo_html(cliente_nome: str, historico: list[EntregavelHistoricoRead]) -> str:
        cliente_nome_seguro = html.escape(cliente_nome)

        if not historico:
            corpo_tabela = "<p>Nenhum entregável gerado ainda.</p>"
        else:
            linhas = "".join(
                "<tr>"
                f"<td>{html.escape(item.processo_nome)}</td>"
                f"<td>{html.escape(ROTULOS_ENTREGAVEL.get(item.tipo, item.tipo.value))}</td>"
                f"<td>{html.escape(item.status.value if item.status else '—')}</td>"
                f"<td>{item.gerado_em.strftime('%d/%m/%Y %H:%M') if item.gerado_em else '—'}</td>"
                "</tr>"
                for item in historico
            )
            corpo_tabela = (
                "<table cellpadding='6' cellspacing='0' style='border-collapse:collapse;width:100%'>"
                "<thead><tr>"
                "<th align='left'>Processo</th><th align='left'>Entregável</th>"
                "<th align='left'>Status</th><th align='left'>Gerado em</th>"
                "</tr></thead><tbody>" + linhas + "</tbody></table>"
            )

        return (
            f"<h2>Relatório de entregáveis — {cliente_nome_seguro}</h2>"
            "<p>Resumo gerado automaticamente pelo MAIA.</p>"
            f"{corpo_tabela}"
        )
