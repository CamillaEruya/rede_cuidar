from pathlib import Path
import os

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from app.modules.feed.feedRoutes import router as feed_router
from app.modules.home.homeRoutes import router as home_router
from app.modules.perfil.perfilRoutes import router as perfil_router
from app.modules.agenda.agendaRoutes import router as agenda_router
from app.modules.profissionais.profissionaisRoutes import router as profissionais_router
from app.modules.biblioteca.bibliotecaRoutes import router as biblioteca_router

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY") or "rede-cuidar-dev-secret-key"

app = FastAPI(title="Rede Cuidar")
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET_KEY,
)
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.include_router(home_router)
app.include_router(feed_router)
app.include_router(perfil_router)
app.include_router(agenda_router)
app.include_router(profissionais_router)
app.include_router(biblioteca_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
