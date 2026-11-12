from typing import Any

from fastapi import APIRouter, Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.modules.biblioteca import bibliotecaController as controller
from app.modules.biblioteca.bibliotecaModel import (
    ChatRequest,
    ChatResponse,
    NewsResponse,
)
from app.modules.user import userController
from app.modules.biblioteca import noticiasController


router = APIRouter(prefix="/api/biblioteca", tags=["Biblioteca"])
bearer_scheme = HTTPBearer()


@router.get("/noticias", response_model=NewsResponse)
async def get_news(
    pessoa_id: int = Header(..., alias="X-User-ID"),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict[str, Any]:
    userController.autenticar(pessoa_id, credentials.credentials)
    return {"articles": await noticiasController.buscar_noticias()}


@router.post("/chat", response_model=ChatResponse)
def post_chat(
    data: ChatRequest,
    pessoa_id: int = Header(..., alias="X-User-ID"),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict[str, Any]:
    userController.autenticar(pessoa_id, credentials.credentials)
    return controller.responder_chat(data)
