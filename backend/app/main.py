from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import clientes, configuracoes, entregaveis, processos, relatorios
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(title="MAIA API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(clientes.router, prefix="/api/v1")
app.include_router(processos.router, prefix="/api/v1")
app.include_router(entregaveis.router, prefix="/api/v1")
app.include_router(relatorios.router, prefix="/api/v1")
app.include_router(configuracoes.router, prefix="/api/v1")


@app.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    return {"status": "ok"}
