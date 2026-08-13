import pytest_asyncio
from sqlmodel import SQLModel

from app.db.session import engine
from app.domain import models  # noqa: F401 - garante que as tabelas sejam registradas


@pytest_asyncio.fixture(autouse=True)
async def preparar_banco():
    async with engine.begin() as conexao:
        await conexao.run_sync(SQLModel.metadata.create_all)
    yield
