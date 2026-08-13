# MAIA — Mapeamento Assistido por IA

Plataforma para condução de mapeamento de processos: cadastro de clientes e processos, armazenamento de documentação em SharePoint/OneDrive via Microsoft Graph e geração de entregáveis (AS IS, TO BE, RACI, gaps, dashboards de maturidade, status semanal e pauta de reunião) em `.docx`.

## Arquitetura

```
Angular (SPA)  →  FastAPI (API + auth)  →  SQLite (clientes, processos, docs, jobs)
                                         →  Microsoft Graph API (SharePoint/OneDrive)
                                         →  Claude API (geração de conteúdo, via BackgroundTasks)
```

| Camada | Tecnologia |
|---|---|
| Frontend | Angular 17 (standalone components) + Angular Material |
| Backend | FastAPI + Pydantic v2 + SQLModel (async) |
| Banco | SQLite (arquivo local, sem serviço externo) |
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

Nenhuma credencial fica no código-fonte. Todos os segredos são lidos de variáveis de ambiente, carregadas de `backend/.env` — um arquivo **não versionado** (listado em `.gitignore`) e **opcional**: sem ele, o backend sobe normalmente com um banco SQLite local e a geração de entregáveis desabilitada até a chave da IA ser configurada.

Para habilitar as integrações:
1. Copie o template:
   ```bash
   cp backend/.env.example backend/.env
   ```
2. Preencha `backend/.env` com:
   - `ANTHROPIC_API_KEY` — chave da API Claude (console.anthropic.com).
   - `MS_GRAPH_TENANT_ID`, `MS_GRAPH_CLIENT_ID`, `MS_GRAPH_CLIENT_SECRET`, `MS_GRAPH_SITE_ID` — credenciais de aplicativo (client credentials) registradas no Entra ID com permissão `Sites.ReadWrite.All` (app-only) sobre o site do SharePoint.
   - `MS_GRAPH_SENDER_UPN` — caixa de correio remetente do envio de relatórios por e-mail (`POST /relatorios/enviar-email`), via Microsoft Graph. Requer a permissão de aplicativo `Mail.Send` (com consentimento de admin) no mesmo app registration acima.
   - `ENTRA_TENANT_ID`, `ENTRA_AUDIENCE` — validação de token dos usuários do painel (App Registration do frontend).
3. Preencha `frontend/src/environments/environment.ts` (`auth.clientId`, `auth.tenantId`) com os dados da App Registration do frontend.

Em produção, não mantenha valores reais em disco: use um gerenciador de segredos (Azure Key Vault, GitHub Actions secrets ou equivalente) e injete-os como variáveis de ambiente do container.

### Comportamento sem credenciais configuradas

A aplicação foi pensada para subir e ser navegável antes de qualquer credencial existir:

- **`ANTHROPIC_API_KEY`** ausente — a geração de entregáveis retorna erro explícito só quando acionada; o resto da aplicação funciona normalmente.
- **`MS_GRAPH_*`** ausente — mesma lógica: só falha quando um entregável tenta ser salvo no SharePoint.
- **`MS_GRAPH_SENDER_UPN`** ausente — o envio de relatório por e-mail (tela Relatórios) retorna `503` só quando acionado; navegar e consultar o histórico continuam funcionando normalmente.
- **Login (Entra ID)** — controlado por `ENVIRONMENT` (`backend/.env`, padrão `development`):
  - `ENVIRONMENT=development` (padrão) **e** `ENTRA_TENANT_ID`/`ENTRA_AUDIENCE` ausentes → a API libera as rotas sem exigir token, e o frontend não tenta redirecionar para o login da Microsoft (isso é o que faz `docker compose up` funcionar sem nenhum `.env`). Basta não preencher `auth.clientId`/`auth.tenantId` em `frontend/src/environments/environment.ts`.
  - `ENVIRONMENT=production` → o backend **exige** `ENTRA_TENANT_ID`/`ENTRA_AUDIENCE` configurados (responde `503` até serem definidos) e passa a validar token em toda rota. Configure também `auth.clientId`/`auth.tenantId` no frontend para o login funcionar — sem isso a build de produção também bloqueia a navegação.

Ou seja: em desenvolvimento a ausência de credenciais é ignorada; em produção ela é obrigatória.

## Como rodar

### Com Docker (recomendado)

Um único comando sobe tudo — sem necessidade de instalar Python, Node ou de criar o arquivo `.env` antes:

```bash
docker compose up --build
```

O que acontece automaticamente:
- As dependências de Python e de Node são instaladas dentro da imagem de cada serviço no `--build` (nada é instalado na máquina host).
- O container do backend aplica as migrations (`alembic upgrade head`) antes de subir a API, criando o banco SQLite na primeira execução.
- O banco fica em um volume Docker próprio (`sqlite_data`), então os dados persistem entre reinícios (`docker compose down` sem `-v`) mesmo sem `.env`.
- O código do backend (`backend/app`) é montado como volume e o servidor roda com `--reload`, então alterações no host refletem no container automaticamente.
- O frontend já sobe compilado e servido por nginx, com `/api` já roteado para o backend (`nginx.conf`) — não é preciso configurar URLs manualmente.

- Backend: http://localhost:8000 (`/health`, `/docs`)
- Frontend: http://localhost:4200

Para reconstruir as imagens após mudar dependências (`requirements.txt` ou `package.json`), rode `docker compose up --build` novamente.

### Sem Docker

Backend:
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
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

- `clientes` — id, nome, pasta_sharepoint_id (referência ao Graph, não path local), destinatarios_relatorio
- `processos` — id, cliente_id, nome, status_as_is, status_to_be
- `documentos` — id, processo_id, nome, graph_item_id, camada (bronze/as_is/to_be), tamanho_kb
- `entregaveis` — id, processo_id, tipo, graph_item_id, gerado_em
- `jobs_geracao` — id, entregavel_id, status (pendente/processando/concluido/erro), log

O estado de um processo é sempre uma consulta SQL — nunca uma varredura de filesystem.

## Navegação

| Tela | O que mostra |
|---|---|
| Dashboard | Visão geral: contagem de clientes, tipos de entregável suportados, ambiente de autenticação |
| Clientes | Cadastro de clientes e acesso aos processos de cada um |
| Processos | Todos os processos mapeados, de todos os clientes, com status AS IS/TO BE |
| Relatórios | Histórico consolidado de entregáveis gerados (todos os clientes), com filtro por cliente/tipo e envio por e-mail |
| Configurações | Status real das integrações (IA, Graph, autenticação, e-mail) e destinatários padrão de relatório por cliente |

Cada processo tem sua própria Central de Entregáveis (acessível a partir de Clientes ou Processos) com os 7 tipos suportados: AS IS, Gaps, TO BE, Matriz RACI, Dashboard de Maturidade, Status Semanal e Pauta de Reunião.
