from typing import Any

from fastapi import APIRouter, Body, Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.modules.admin import adminController as controller

router = APIRouter(prefix="/api/admin", tags=["Administração"])
bearer_scheme = HTTPBearer()


@router.get("/usuarios")
def get_usuarios(
    admin_id: int = Header(..., alias="X-User-ID"),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> list[dict[str, Any]]:
    return controller.get_usuarios(admin_id, credentials.credentials)


@router.put("/usuarios/{pessoa_id}")
def put_usuario(
    pessoa_id: int,
    data: dict[str, Any] = Body(...),
    admin_id: int = Header(..., alias="X-User-ID"),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict[str, Any]:
    return controller.put_usuario(admin_id, pessoa_id, data, credentials.credentials)


@router.get("/profissionais")
def get_profissionais(
    admin_id: int = Header(..., alias="X-User-ID"),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> list[dict[str, Any]]:
    return controller.get_profissionais(admin_id, credentials.credentials)


@router.put("/profissionais/{pessoa_id}/status")
def put_status_profissional(
    pessoa_id: int,
    data: dict[str, Any] = Body(...),
    admin_id: int = Header(..., alias="X-User-ID"),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict[str, Any]:
    return controller.put_status_profissional(
        admin_id, pessoa_id, data, credentials.credentials
    )


@router.get("/agendas")
def get_agendas(
    admin_id: int = Header(..., alias="X-User-ID"),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> list[dict[str, Any]]:
    return controller.get_agendas(admin_id, credentials.credentials)


@router.put("/agendas/{agenda_id}/status")
def put_status_agenda(
    agenda_id: int,
    data: dict[str, Any] = Body(...),
    admin_id: int = Header(..., alias="X-User-ID"),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict[str, Any]:
    return controller.put_status_agenda(
        admin_id, agenda_id, data, credentials.credentials
    )


@router.get("/publicacoes")
def get_publicacoes(
    admin_id: int = Header(..., alias="X-User-ID"),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> list[dict[str, Any]]:
    return controller.get_publicacoes(admin_id, credentials.credentials)


@router.put("/publicacoes/{publicacao_id}/status")
def put_status_publicacao(
    publicacao_id: int,
    data: dict[str, Any] = Body(...),
    admin_id: int = Header(..., alias="X-User-ID"),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict[str, Any]:
    return controller.put_status_publicacao(
        admin_id, publicacao_id, data, credentials.credentials
    )
