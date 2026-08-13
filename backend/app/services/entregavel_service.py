import uuid
from datetime import datetime
from io import BytesIO

from docx import Document as DocxDocument

from app.domain.models import CamadaDocumento, Entregavel, JobGeracao, StatusJob, TipoEntregavel
from app.providers.ai.base import AIProvider
from app.providers.documents.docx_generator import gerar_docx
from app.providers.storage.base import StorageProvider
from app.repositories.cliente_repo import ClienteRepository
from app.repositories.documento_repo import DocumentoRepository
from app.repositories.entregavel_repo import EntregavelRepository
from app.repositories.processo_repo import ProcessoRepository

PROMPT_SISTEMA = """Você atua como consultor de mapeamento de processos de RH, com foco na plataforma Gen.te Nuvem.

Regras:
- Baseie-se apenas nos documentos fornecidos. Não utilize conhecimento externo sem sinalizar isso.
- Cite o documento de origem entre parênteses para cada afirmação relevante.
- Quando uma informação não constar nos documentos, registre "não identificado nos documentos".
- Recomendações de TO BE são sempre de médio e longo prazo.
- Separe claramente fatos, hipóteses e recomendações.
- Utilize linguagem consultiva, objetiva e executiva em português do Brasil."""

TEMPLATES: dict[TipoEntregavel, str] = {
    TipoEntregavel.word_as_is: """Gere o mapeamento AS IS do processo {processo} do cliente {cliente}.
Estruture em 5 partes:

PARTE 1 — VISÃO GERAL DO PROCESSO (até 5 linhas)
PARTE 2 — SUBPROCESSOS AS IS
Para cada subprocesso: Trigger | Etapas | Responsável | Sistema | Tempo | Outputs | Observações
PARTE 3 — GAPS E DORES IDENTIFICADOS
Tabela: # | Gap/Dor | Impacto | Criticidade | Fonte
PARTE 4 — INTEGRAÇÕES E DEPENDÊNCIAS
Sistemas + integrações externas + dependências com outros processos
PARTE 5 — AVALIAÇÃO DE MATURIDADE
Qualidade do Processo (0-100) + justificativa | Profundidade Documental (0-100) + justificativa | Classificação final""",
    TipoEntregavel.excel_gaps: """Identifique e classifique os gaps do processo {processo} do cliente {cliente}.
Para cada gap:
- Descrição | Categoria (operacional/sistêmico/documental/governança/compliance) | Criticidade (baixa/média/alta/crítica) | Impacto | Responsável sugerido | Recomendação inicial | Prioridade
Formato: tabela markdown com todas as colunas.""",
    TipoEntregavel.to_be: """Com base no AS IS validado e nos gaps identificados, proponha o TO BE para {processo} do cliente {cliente}.
Todas as recomendações são de MÉDIO E LONGO PRAZO.
Estruture em:
PARTE 1 — VISÃO DO ESTADO FUTURO (até 5 linhas)
PARTE 2 — RECOMENDAÇÕES por subprocesso: Gap origem | AS IS atual | Proposta TO BE | Ganho esperado | Prazo (3-6 meses ou 6-12 meses)
PARTE 3 — MATRIZ DE PRIORIZAÇÃO: Esforço × Impacto × Classificação (Quick Win / Estrutural / Transformacional)
PARTE 4 — MATURIDADE ESPERADA pós-implementação""",
    TipoEntregavel.raci: """Gere a Matriz RACI para o processo {processo} do cliente {cliente}.
Papéis: Consultor | RH Operacional | Gestor do Processo | TI | Jurídico/Compliance | Liderança Executiva | Suporte.
Para cada atividade: R (responsável) | A (aprovador) | C (consultado) | I (informado).
Formato: tabela markdown com todas as colunas + coluna de observações de governança.""",
    TipoEntregavel.dashboard: """Avalie a maturidade do processo {processo} do cliente {cliente} nos dois eixos:
1. Qualidade do Processo Atual (0-100): 0-25=Crítico | 26-50=Regular | 51-75=Bom | 76-100=Excelente
2. Profundidade da Documentação (0-100): mesma escala.
Calcule a média final.
Entregue tabela: processo | nota qualidade | justificativa | nota documental | justificativa | nota final | classificação | principal recomendação.
Ao final, gere resumo executivo em até 10 linhas.""",
    TipoEntregavel.status_semanal: """Gere um status report semanal do projeto {cliente}.
Processo analisado nesta semana: {processo}.
Estruture em: 1. Resumo executivo | 2. Avanços | 3. Pendências do cliente | 4. Riscos e bloqueios | 5. Entregáveis atualizados | 6. Decisões necessárias | 7. Próximas ações.
Linguagem objetiva e executiva para apresentação à liderança.""",
    TipoEntregavel.pauta: """Prepare uma pauta de reunião para validação do AS IS de {processo} com o cliente {cliente}.
Inclua: objetivo | contexto | pontos identificados | gaps preliminares | perguntas de validação por tema (operação, sistema, responsáveis, controles, riscos, melhorias) | documentos pendentes | decisões esperadas | próximos passos.""",
}

SUFIXOS_ARQUIVO: dict[TipoEntregavel, str] = {
    TipoEntregavel.word_as_is: "ASIS",
    TipoEntregavel.excel_gaps: "Gaps",
    TipoEntregavel.to_be: "TOBE",
    TipoEntregavel.raci: "RACI",
    TipoEntregavel.dashboard: "Maturidade",
    TipoEntregavel.status_semanal: "Status_Semanal",
    TipoEntregavel.pauta: "Pauta",
}

MAX_DOCUMENTOS_CONTEXTO = 8
MAX_CARACTERES_POR_DOCUMENTO = 3000


class EntregavelService:
    def __init__(
        self,
        entregavel_repo: EntregavelRepository,
        processo_repo: ProcessoRepository,
        cliente_repo: ClienteRepository,
        documento_repo: DocumentoRepository,
        storage: StorageProvider,
        ai: AIProvider,
    ):
        self._entregaveis = entregavel_repo
        self._processos = processo_repo
        self._clientes = cliente_repo
        self._documentos = documento_repo
        self._storage = storage
        self._ai = ai

    async def iniciar_geracao(self, processo_id: uuid.UUID, tipo: TipoEntregavel) -> JobGeracao:
        entregavel = await self._entregaveis.criar_entregavel(Entregavel(processo_id=processo_id, tipo=tipo))
        return await self._entregaveis.criar_job(JobGeracao(entregavel_id=entregavel.id))

    async def executar_geracao(self, job_id: uuid.UUID) -> None:
        job = await self._entregaveis.obter_job(job_id)
        if job is None:
            return

        await self._entregaveis.atualizar_job(job, status=StatusJob.processando, log="Geração iniciada")
        try:
            entregavel = await self._entregaveis.obter_entregavel(job.entregavel_id)
            processo = await self._processos.obter(entregavel.processo_id)
            cliente = await self._clientes.obter(processo.cliente_id)

            contexto = await self._montar_contexto(processo.id)
            template = TEMPLATES[entregavel.tipo]
            prompt_usuario = template.format(cliente=cliente.nome, processo=processo.nome) + f"\n\n{contexto}"

            conteudo = await self._ai.gerar_texto(PROMPT_SISTEMA, prompt_usuario)
            arquivo = gerar_docx(conteudo)

            nome_arquivo = self._nome_arquivo(entregavel.tipo, processo.nome)
            item_id = await self._storage.salvar_arquivo(cliente.pasta_sharepoint_id, nome_arquivo, arquivo)

            entregavel.graph_item_id = item_id
            entregavel.gerado_em = datetime.utcnow()
            await self._entregaveis.atualizar_entregavel(entregavel)

            await self._entregaveis.atualizar_job(job, status=StatusJob.concluido, log="Geração concluída")
        except Exception as exc:  # noqa: BLE001 - job de background precisa registrar qualquer falha
            await self._entregaveis.atualizar_job(job, status=StatusJob.erro, log=str(exc))

    async def _montar_contexto(self, processo_id: uuid.UUID) -> str:
        documentos = await self._documentos.listar_por_camada(processo_id, CamadaDocumento.bronze)
        if not documentos:
            return "Nenhum documento disponível na camada Bronze."

        blocos = []
        for documento in documentos[:MAX_DOCUMENTOS_CONTEXTO]:
            conteudo_bruto = await self._storage.ler_arquivo(documento.graph_item_id)
            texto = self._extrair_texto(documento.nome, conteudo_bruto)
            blocos.append(f"Documento: {documento.nome}\n{texto}")
        return "\n\n".join(blocos)

    @staticmethod
    def _extrair_texto(nome: str, conteudo: bytes) -> str:
        if nome.lower().endswith(".docx"):
            documento = DocxDocument(BytesIO(conteudo))
            texto = "\n".join(par.text for par in documento.paragraphs if par.text.strip())
        else:
            texto = conteudo.decode("utf-8", errors="ignore")
        return texto[:MAX_CARACTERES_POR_DOCUMENTO]

    @staticmethod
    def _nome_arquivo(tipo: TipoEntregavel, processo: str) -> str:
        data = datetime.utcnow().strftime("%Y-%m-%d")
        return f"{data}_{processo.replace(' ', '_')}_{SUFIXOS_ARQUIVO[tipo]}.docx"
