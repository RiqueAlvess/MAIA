from fastapi.testclient import TestClient

from app.main import app


def test_health_check_returns_ok() -> None:
    with TestClient(app) as client:
        resposta = client.get("/health")

    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok"}


def test_clientes_endpoint_requires_authentication() -> None:
    with TestClient(app) as client:
        resposta = client.get("/api/v1/clientes")

    assert resposta.status_code == 401
