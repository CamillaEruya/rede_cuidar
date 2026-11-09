from typing import Any

from fastapi import APIRouter, Body, Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.modules.profissional import profissionalController as controller

router = APIRouter(prefix="/api/profissional", tags=["Profissional"])
bearer_scheme = HTTPBearer()


@router.post("", status_code=201)
def post_profissional(data: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return controller.post_profissional(data)


@router.get("")
def get_profissionais(
    pessoa_id: int = Header(..., alias="X-User-ID"),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> list[dict[str, Any]]:
    return controller.get_profissionais(pessoa_id, credentials.credentials)


@router.get("/{pessoa_id}")
def get_profissional(
    pessoa_id: int,
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict[str, Any]:
    return controller.get_profissional(pessoa_id, credentials.credentials)


@router.put("/{pessoa_id}")
def put_profissional(
    pessoa_id: int,
    data: dict[str, Any] = Body(...),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict[str, Any]:
    return controller.put_profissional(pessoa_id, data, credentials.credentials)
