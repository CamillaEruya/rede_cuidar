from typing import Any

from fastapi import APIRouter, Body, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.modules.pessoas import pessoasController as controller

router = APIRouter(prefix="/api/pessoas", tags=["Pessoas"])
bearer_scheme = HTTPBearer()
## GET ---------------------------------------------------------
@router.get("")
def get_pessoas() -> list[dict[str, Any]]:
    return controller.get_pessoas()

@router.get("/tipo-perfil")
def get_tipos_perfil() -> list[dict[str, Any]]:
    return controller.get_tipos_perfil()


@router.get("/tipo-perfil/{tipos_perfil_id}")
def get_tipo_perfil(tipos_perfil_id: int) -> list[dict[str, Any]]:
    return controller.get_tipos_perfil(tipos_perfil_id)

@router.get("/{pessoa_id}")
def get_pessoa(pessoa_id: int) -> list[dict[str, Any]]:
    return controller.get_pessoas(pessoa_id)


## POST --------------------------------------------------------
@router.post("")
def post_pessoa(data: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return controller.post_pessoa(data)



## PUT ---------------------------------------------------------
@router.put("/{pessoa_id}")
def update_pessoa(
    pessoa_id: int, 
    data: dict[str, Any] = Body(...),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> dict[str, Any]:
    print(data)
    return controller.update_pessoa(pessoa_id, data, credentials.credentials)


## DELETE ------------------------------------------------------
@router.delete("/{pessoa_id}")
def delete_pessoa(pessoa_id: int) -> dict[str, Any]:
    return controller.delete_pessoa(pessoa_id)
