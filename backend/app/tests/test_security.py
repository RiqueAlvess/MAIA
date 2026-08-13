import jwt
import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

import app.core.security as security_module
from app.core.config import Settings
from app.core.security import DEV_USER, get_current_user


def _settings(**overrides) -> Settings:
    valores = {"environment": "development", "entra_tenant_id": "", "entra_audience": ""}
    valores.update(overrides)
    return Settings(**valores)


async def test_bypassa_autenticacao_em_desenvolvimento_sem_configuracao() -> None:
    resultado = await get_current_user(credentials=None, settings=_settings())
    assert resultado == DEV_USER


async def test_exige_configuracao_em_producao() -> None:
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(credentials=None, settings=_settings(environment="production"))

    assert exc_info.value.status_code == 503


async def test_exige_token_quando_auth_esta_configurada() -> None:
    settings = _settings(entra_tenant_id="tenant-123", entra_audience="api://maia")

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(credentials=None, settings=settings)

    assert exc_info.value.status_code == 401


async def test_rejeita_token_invalido_quando_auth_esta_configurada(monkeypatch: pytest.MonkeyPatch) -> None:
    def _decode_falso(token: str, settings: Settings) -> dict:
        raise jwt.InvalidTokenError("assinatura inválida")

    monkeypatch.setattr(security_module, "_decode_token", _decode_falso)

    settings = _settings(entra_tenant_id="tenant-123", entra_audience="api://maia")
    credenciais = HTTPAuthorizationCredentials(scheme="Bearer", credentials="token-invalido")

    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(credentials=credenciais, settings=settings)

    assert exc_info.value.status_code == 401
