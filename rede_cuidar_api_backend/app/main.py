from fastapi import FastAPI

from app.modules.pessoas.pessoasRouter import router as pessoas_router
from app.modules.profissional.profissionalRouter import router as profissional_router
from app.modules.user.userRouter import router as user_router

app = FastAPI(title="Rede Cuidar API")
app.include_router(pessoas_router)
app.include_router(profissional_router)
app.include_router(user_router)


@app.get("/health", tags=["Health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
