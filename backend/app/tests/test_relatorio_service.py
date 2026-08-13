import uuid
from datetime import datetime

import pytest

from app.domain.models import Cliente, Entregavel, JobGeracao, Processo, StatusJob, TipoEntregavel
from app.services.relatorio_service import RelatorioService


class FakeClienteRepo:
    def __init__(self, cliente: Cliente):
        self._cliente = cliente

    async def obter(self, cliente_id: uuid.UUID) -> Cliente | None:
        return self._cliente if cliente_id == self._cliente.id else None


class FakeEntregavelRepo:
    def __init__(self, linhas: list[tuple[Entregavel, Processo, Cliente, JobGeracao | None]]):
        self._linhas = linhas

    async def listar_historico(self, cliente_id=None, tipo=None):
        resultado = self._linhas
        if cliente_id is not None:
            resultado = [linha for linha in resultado if linha[2].id == cliente_id]
        if tipo is not None:
            resultado = [linha for linha in resultado if linha[0].tipo == tipo]
        return resultado


class FakeEmailProvider:
    def __init__(self):
        self.chamadas: list[tuple[list[str], str, str]] = []

    async def enviar(self, destinatarios: list[str], assunto: str, corpo_html: str) -> None:
        self.chamadas.append((destinatarios, assunto, corpo_html))


@pytest.fixture
def cenario():
    cliente = Cliente(
        id=uuid.uuid4(),
        nome="Cliente Teste",
        pasta_sharepoint_id="pasta-1",
        destinatarios_relatorio="padrao@example.com, outro@example.com",
    )
    processo = Processo(id=uuid.uuid4(), cliente_id=cliente.id, nome="Admissão")
    entregavel = Entregavel(id=uuid.uuid4(), processo_id=processo.id, tipo=TipoEntregavel.word_as_is)
    job = JobGeracao(
        id=uuid.uuid4(), entregavel_id=entregavel.id, status=StatusJob.concluido, atualizado_em=datetime.utcnow()
    )

    entregavel_repo = FakeEntregavelRepo([(entregavel, processo, cliente, job)])
    cliente_repo = FakeClienteRepo(cliente)
    email = FakeEmailProvider()

    service = RelatorioService(entregavel_repo, cliente_repo, email)
    return service, cliente, processo, email


async def test_listar_historico_retorna_dados_enriquecidos(cenario):
    service, cliente, processo, _ = cenario

    historico = await service.listar_historico()

    assert len(historico) == 1
    item = historico[0]
    assert item.cliente_nome == cliente.nome
    assert item.processo_nome == processo.nome
    assert item.status == StatusJob.concluido


async def test_enviar_email_usa_destinatarios_padrao_do_cliente_quando_nao_informado(cenario):
    service, cliente, _, email = cenario

    await service.enviar_email(cliente.id, processo_id=None, destinatarios_override=None)

    assert len(email.chamadas) == 1
    destinatarios, assunto, corpo = email.chamadas[0]
    assert destinatarios == ["padrao@example.com", "outro@example.com"]
    assert cliente.nome in assunto
    assert "Admissão" in corpo


async def test_enviar_email_com_override_ignora_destinatarios_padrao(cenario):
    service, cliente, _, email = cenario

    await service.enviar_email(cliente.id, processo_id=None, destinatarios_override=["custom@example.com"])

    destinatarios, _, _ = email.chamadas[0]
    assert destinatarios == ["custom@example.com"]


async def test_enviar_email_sem_destinatarios_disponiveis_levanta_value_error():
    cliente = Cliente(id=uuid.uuid4(), nome="Sem Destinatarios", pasta_sharepoint_id="pasta-2")
    service = RelatorioService(FakeEntregavelRepo([]), FakeClienteRepo(cliente), FakeEmailProvider())

    with pytest.raises(ValueError, match="destinatário"):
        await service.enviar_email(cliente.id, processo_id=None, destinatarios_override=None)


async def test_enviar_email_cliente_inexistente_levanta_value_error(cenario):
    service, _, _, _ = cenario

    with pytest.raises(ValueError, match="Cliente não encontrado"):
        await service.enviar_email(uuid.uuid4(), processo_id=None, destinatarios_override=["x@example.com"])
