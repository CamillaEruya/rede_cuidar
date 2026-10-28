from typing import Any
from fastapi import APIRouter, Body, Header, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.modules.user import userController as controller

router = APIRouter(prefix="/api/user", tags=["User"])
bearer_scheme = HTTPBearer()


@router.post("/autenticacao")
def post_autenticacao(
    pessoa_id = Header(..., alias="X-User-ID"),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> dict[str, Any]:
    return controller.post_autenticacao(pessoa_id, credentials.credentials)



@router.post("/login")
def post_login(data: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return controller.post_login(data)
