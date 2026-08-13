from fastapi.testclient import TestClient

from app.main import app


def test_status_integracoes_reflete_ambiente_de_desenvolvimento() -> None:
    with TestClient(app) as client:
        resposta = client.get("/api/v1/configuracoes/status")

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["ambiente"] == "development"
    assert corpo["ai_configurado"] is False
    assert corpo["graph_configurado"] is False
    assert corpo["email_configurado"] is False


def test_historico_de_entregaveis_vazio_por_padrao() -> None:
    with TestClient(app) as client:
        resposta = client.get("/api/v1/relatorios/entregaveis")

    assert resposta.status_code == 200
    assert resposta.json() == []


def test_enviar_email_sem_destinatarios_retorna_400() -> None:
    with TestClient(app) as client:
        cliente = client.post(
            "/api/v1/clientes", json={"nome": "Cliente Email", "pasta_sharepoint_id": "pasta-x"}
        ).json()
        resposta = client.post("/api/v1/relatorios/enviar-email", json={"cliente_id": cliente["id"]})

    assert resposta.status_code == 400


def test_enviar_email_sem_graph_configurado_retorna_503() -> None:
    with TestClient(app) as client:
        cliente = client.post(
            "/api/v1/clientes", json={"nome": "Cliente Email 2", "pasta_sharepoint_id": "pasta-x2"}
        ).json()
        resposta = client.post(
            "/api/v1/relatorios/enviar-email",
            json={"cliente_id": cliente["id"], "destinatarios": ["destino@example.com"]},
        )

    assert resposta.status_code == 503


def test_atualizar_destinatarios_do_cliente() -> None:
    with TestClient(app) as client:
        cliente = client.post(
            "/api/v1/clientes", json={"nome": "Cliente Destinatarios", "pasta_sharepoint_id": "pasta-y"}
        ).json()
        assert cliente["destinatarios_relatorio"] == ""

        resposta = client.patch(
            f"/api/v1/clientes/{cliente['id']}/destinatarios",
            json={"destinatarios_relatorio": "a@example.com, b@example.com"},
        )

    assert resposta.status_code == 200
    assert resposta.json()["destinatarios_relatorio"] == "a@example.com, b@example.com"


def test_listar_processos_sem_cliente_id_retorna_todos_com_nome_do_cliente() -> None:
    with TestClient(app) as client:
        cliente = client.post(
            "/api/v1/clientes", json={"nome": "Cliente Global", "pasta_sharepoint_id": "pasta-z"}
        ).json()
        client.post("/api/v1/processos", json={"cliente_id": cliente["id"], "nome": "Processo Global"})

        resposta = client.get("/api/v1/processos")

    assert resposta.status_code == 200
    processos = resposta.json()
    encontrado = next(p for p in processos if p["nome"] == "Processo Global")
    assert encontrado["cliente_nome"] == "Cliente Global"
