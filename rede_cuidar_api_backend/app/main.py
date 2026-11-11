
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.core.image_upload import UPLOAD_DIR
from app.modules.pessoas.pessoasRouter import router as pessoas_router
from app.modules.profissional.profissionalRouter import router as profissional_router
from app.modules.user.userRouter import router as user_router
from app.modules.publicacao.publicacaoRouter import router as publicacao_router

app = FastAPI(title="Rede Cuidar API")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount(
    "/uploads",
    StaticFiles(directory=UPLOAD_DIR),
    name="uploads",
)

app.include_router(pessoas_router)
app.include_router(profissional_router)
app.include_router(user_router)
app.include_router(publicacao_router)


@app.get("/health", tags=["Health"])
def health() -> dict[str, str]:
    return {"status": "ok"}
