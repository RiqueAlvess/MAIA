# MAIA — Mapeamento Assistido por IA

Plataforma para condução de mapeamento de processos: cadastro de clientes e processos, armazenamento de documentação em SharePoint/OneDrive via Microsoft Graph e geração de entregáveis (AS IS, TO BE, RACI, gaps, dashboards de maturidade, status semanal e pauta de reunião) em `.docx`.

## Arquitetura

```
Angular (SPA)  →  FastAPI (API + auth)  →  PostgreSQL (clientes, processos, docs, jobs)
                                         →  Microsoft Graph API (SharePoint/OneDrive)
                                         →  Claude API (geração de conteúdo, via BackgroundTasks)
```

| Camada | Tecnologia |
|---|---|
| Frontend | Angular 17 (standalone components) + Angular Material |
| Backend | FastAPI + Pydantic v2 + SQLModel (async) |
| Banco | PostgreSQL |
| Storage de arquivos | Microsoft Graph API (`httpx` + `MSAL`, autenticação app-only) |
| Geração de conteúdo | Claude API (Anthropic) |
| Autenticação | Microsoft Entra ID (SSO delegado para usuários do painel; client credentials para o backend acessar o Graph) |
| Migrations | Alembic |
| Containers | Docker + docker-compose |

O backend nunca acessa filesystem local. Toda leitura/escrita de arquivo passa pelo `StorageProvider` (`app/providers/storage`), e toda chamada de geração de texto passa pelo `AIProvider` (`app/providers/ai`) — ambos definidos como `Protocol`, injetados via `Depends()`. Trocar de provedor (outro storage, outro modelo de IA) não exige alterar `EntregavelService` nem os routers.

## Estrutura do repositório

```
backend/    API FastAPI, providers, migrations, testes
frontend/   SPA Angular
docker-compose.yml
```

Ver `backend/app/` para a estrutura interna (`api/`, `services/`, `providers/`, `repositories/`, `domain/`) e `frontend/src/app/` (`core/`, `features/`).

## Configuração de credenciais

Nenhuma credencial fica no código-fonte. Todos os segredos são lidos de variáveis de ambiente, carregadas a partir de arquivos `.env` que **não são versionados** (listados em `.gitignore`).

1. Copie os templates:
   ```bash
   cp .env.example .env
   cp backend/.env.example backend/.env
   ```
2. Preencha `.env` (raiz) com a senha do Postgres.
3. Preencha `backend/.env` com:
   - `ANTHROPIC_API_KEY` — chave da API Claude (console.anthropic.com).
   - `MS_GRAPH_TENANT_ID`, `MS_GRAPH_CLIENT_ID`, `MS_GRAPH_CLIENT_SECRET`, `MS_GRAPH_SITE_ID` — credenciais de aplicativo (client credentials) registradas no Entra ID com permissão `Sites.ReadWrite.All` (app-only) sobre o site do SharePoint.
   - `ENTRA_TENANT_ID`, `ENTRA_AUDIENCE` — validação de token dos usuários do painel (App Registration do frontend).
4. Preencha `frontend/src/environments/environment.ts` (`auth.clientId`, `auth.tenantId`) com os dados da App Registration do frontend.

Em produção, não mantenha valores reais em disco: use um gerenciador de segredos (Azure Key Vault, GitHub Actions secrets ou equivalente) e injete-os como variáveis de ambiente do container.

A aplicação funciona sem os segredos configurados até o momento de uso: sem `ANTHROPIC_API_KEY`, o endpoint de geração retorna erro explícito; sem `ENTRA_TENANT_ID`/`ENTRA_AUDIENCE`, as rotas autenticadas retornam `503`. Isso permite subir o ambiente e validar o restante do sistema antes de obter todas as credenciais.

## Como rodar

### Com Docker (recomendado)

```bash
docker compose up --build
```

- Backend: http://localhost:8000 (`/health`, `/docs`)
- Frontend: http://localhost:4200

### Sem Docker

Backend:
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export $(cat .env | grep -v '^#' | xargs)   # ou configure as variáveis manualmente
alembic upgrade head
uvicorn app.main:app --reload
```

Frontend:
```bash
cd frontend
npm install
npm start   # ng serve --proxy-config proxy.conf.json, aponta /api para localhost:8000
```

## Testes

Backend:
```bash
cd backend
pip install -r requirements.txt
pytest
```

Os testes de serviço (`app/tests/test_entregavel_service.py`) usam implementações fake de `StorageProvider` e `AIProvider`, portanto rodam sem credenciais reais e sem acesso à rede. Os testes de API (`app/tests/test_health.py`) sobem a aplicação FastAPI em memória.

Frontend:
```bash
cd frontend
npm install
npm test
```

Build de produção (valida que o projeto compila sem erros):
```bash
cd frontend
npm run build
```

## Contrato de API

O FastAPI expõe o schema OpenAPI em `/openapi.json`. Após qualquer mudança de endpoint no backend, regenere o client TypeScript do frontend:

```bash
cd frontend
npm run generate:api
```

O comando lê `http://localhost:8000/openapi.json` (backend precisa estar rodando) e escreve em `src/app/core/api/`. Os arquivos hoje presentes nessa pasta seguem manualmente o mesmo contrato dos schemas em `backend/app/domain/schemas.py`; qualquer divergência aparece como erro de compilação no Angular.

## Migrations

```bash
cd backend
alembic upgrade head              # aplica migrations
alembic revision -m "descricao"   # cria uma nova migration manual
```

## Modelo de dados

- `clientes` — id, nome, pasta_sharepoint_id (referência ao Graph, não path local)
- `processos` — id, cliente_id, nome, status_as_is, status_to_be
- `documentos` — id, processo_id, nome, graph_item_id, camada (bronze/as_is/to_be), tamanho_kb
- `entregaveis` — id, processo_id, tipo, graph_item_id, gerado_em
- `jobs_geracao` — id, entregavel_id, status (pendente/processando/concluido/erro), log

O estado de um processo é sempre uma consulta SQL — nunca uma varredura de filesystem.
