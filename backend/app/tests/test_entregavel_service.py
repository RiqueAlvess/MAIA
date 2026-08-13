import uuid
from datetime import datetime

import pytest

from app.domain.models import (
    CamadaDocumento,
    Cliente,
    Documento,
    Entregavel,
    JobGeracao,
    Processo,
    StatusJob,
    TipoEntregavel,
)
from app.services.entregavel_service import EntregavelService


class FakeClienteRepo:
    def __init__(self, cliente: Cliente):
        self._cliente = cliente

    async def obter(self, cliente_id: uuid.UUID) -> Cliente | None:
        return self._cliente if cliente_id == self._cliente.id else None


class FakeProcessoRepo:
    def __init__(self, processo: Processo):
        self._processo = processo

    async def obter(self, processo_id: uuid.UUID) -> Processo | None:
        return self._processo if processo_id == self._processo.id else None


class FakeDocumentoRepo:
    def __init__(self, documentos: list[Documento]):
        self._documentos = documentos

    async def listar_por_camada(self, processo_id: uuid.UUID, camada: CamadaDocumento) -> list[Documento]:
        return [d for d in self._documentos if d.processo_id == processo_id and d.camada == camada]


class FakeEntregavelRepo:
    def __init__(self):
        self.entregaveis: dict[uuid.UUID, Entregavel] = {}
        self.jobs: dict[uuid.UUID, JobGeracao] = {}

    async def criar_entregavel(self, entregavel: Entregavel) -> Entregavel:
        entregavel.id = entregavel.id or uuid.uuid4()
        self.entregaveis[entregavel.id] = entregavel
        return entregavel

    async def obter_entregavel(self, entregavel_id: uuid.UUID) -> Entregavel | None:
        return self.entregaveis.get(entregavel_id)

    async def atualizar_entregavel(self, entregavel: Entregavel) -> Entregavel:
        self.entregaveis[entregavel.id] = entregavel
        return entregavel

    async def criar_job(self, job: JobGeracao) -> JobGeracao:
        job.id = job.id or uuid.uuid4()
        self.jobs[job.id] = job
        return job

    async def obter_job(self, job_id: uuid.UUID) -> JobGeracao | None:
        return self.jobs.get(job_id)

    async def atualizar_job(self, job: JobGeracao, status: StatusJob, log: str) -> JobGeracao:
        job.status = status
        job.log = log
        job.atualizado_em = datetime.utcnow()
        self.jobs[job.id] = job
        return job


class FakeStorageProvider:
    def __init__(self):
        self.arquivos_salvos: list[tuple[str, str, bytes]] = []

    async def listar_documentos(self, pasta_id: str):
        return []

    async def ler_arquivo(self, item_id: str) -> bytes:
        return f"Conteúdo do documento {item_id}".encode()

    async def salvar_arquivo(self, pasta_id: str, nome_arquivo: str, conteudo: bytes) -> str:
        self.arquivos_salvos.append((pasta_id, nome_arquivo, conteudo))
        return "item-gerado-123"


class FakeAIProvider:
    def __init__(self, resposta: str = "Conteúdo gerado de teste"):
        self._resposta = resposta
        self.ultimo_prompt_usuario: str | None = None

    async def gerar_texto(self, prompt_sistema: str, prompt_usuario: str) -> str:
        self.ultimo_prompt_usuario = prompt_usuario
        return self._resposta


@pytest.fixture
def cenario():
    cliente = Cliente(id=uuid.uuid4(), nome="Cliente Teste", pasta_sharepoint_id="pasta-cliente-1")
    processo = Processo(id=uuid.uuid4(), cliente_id=cliente.id, nome="Admissão")
    documento = Documento(
        id=uuid.uuid4(),
        processo_id=processo.id,
        nome="entrevista.txt",
        graph_item_id="doc-bronze-1",
        camada=CamadaDocumento.bronze,
        tamanho_kb=10,
    )

    entregavel_repo = FakeEntregavelRepo()
    storage = FakeStorageProvider()
    ai = FakeAIProvider()

    service = EntregavelService(
        entregavel_repo=entregavel_repo,
        processo_repo=FakeProcessoRepo(processo),
        cliente_repo=FakeClienteRepo(cliente),
        documento_repo=FakeDocumentoRepo([documento]),
        storage=storage,
        ai=ai,
    )
    return service, entregavel_repo, storage, ai, cliente, processo


async def test_executar_geracao_conclui_job_e_salva_arquivo(cenario):
    service, entregavel_repo, storage, ai, cliente, processo = cenario

    job = await service.iniciar_geracao(processo.id, TipoEntregavel.word_as_is)
    await service.executar_geracao(job.id)

    job_atualizado = entregavel_repo.jobs[job.id]
    assert job_atualizado.status == StatusJob.concluido

    entregavel_atualizado = entregavel_repo.entregaveis[job.entregavel_id]
    assert entregavel_atualizado.graph_item_id == "item-gerado-123"
    assert entregavel_atualizado.gerado_em is not None

    assert len(storage.arquivos_salvos) == 1
    pasta_id, nome_arquivo, _ = storage.arquivos_salvos[0]
    assert pasta_id == cliente.pasta_sharepoint_id
    assert nome_arquivo.endswith("_Admissão_ASIS.docx")

    assert "Admissão" in ai.ultimo_prompt_usuario
    assert "Cliente Teste" in ai.ultimo_prompt_usuario
    assert "entrevista.txt" in ai.ultimo_prompt_usuario


async def test_executar_geracao_registra_erro_quando_ai_falha(cenario):
    service, entregavel_repo, storage, ai, cliente, processo = cenario

    async def gerar_texto_com_falha(prompt_sistema, prompt_usuario):
        raise RuntimeError("ANTHROPIC_API_KEY não configurada")

    ai.gerar_texto = gerar_texto_com_falha

    job = await service.iniciar_geracao(processo.id, TipoEntregavel.raci)
    await service.executar_geracao(job.id)

    job_atualizado = entregavel_repo.jobs[job.id]
    assert job_atualizado.status == StatusJob.erro
    assert "ANTHROPIC_API_KEY" in job_atualizado.log
    assert storage.arquivos_salvos == []
