from typing import Any, Optional

from fastapi import APIRouter, Body, Depends, File, Form, Header, UploadFile
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.image_upload import store_media
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


@router.get("/painel")
def get_painel_profissional(
    pessoa_id: int = Header(..., alias="X-User-ID"),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict[str, Any]:
    return controller.get_painel_profissional(pessoa_id, credentials.credentials)


@router.post("/divulgacao", status_code=201)
async def post_divulgacao(
    titulo: str = Form(...),
    descricao: str = Form(...),
    midia: Optional[UploadFile] = File(None),
    pessoa_id: int = Header(..., alias="X-User-ID"),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict[str, Any]:
    controller.validar_profissional_aprovado(pessoa_id, credentials.credentials)

    midia_url = None
    midia_tipo = None
    if midia is not None and midia.filename:
        midia_url, midia_tipo, _ = await store_media(midia, "profissional")

    return controller.criar_divulgacao(
        pessoa_id=pessoa_id,
        token=credentials.credentials,
        titulo=titulo,
        descricao=descricao,
        midia_url=midia_url,
        midia_tipo=midia_tipo,
    )


@router.delete("/divulgacao/{id_divulgacao}")
def delete_divulgacao(
    id_divulgacao: int,
    pessoa_id: int = Header(..., alias="X-User-ID"),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict[str, Any]:
    return controller.excluir_divulgacao(
        pessoa_id=pessoa_id,
        token=credentials.credentials,
        id_divulgacao=id_divulgacao,
    )


@router.post("/campanha", status_code=201)
def post_campanha(
    data: dict[str, Any] = Body(...),
    pessoa_id: int = Header(..., alias="X-User-ID"),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict[str, Any]:
    return controller.contratar_campanha(
        pessoa_id=pessoa_id,
        token=credentials.credentials,
        plano_codigo=str(data.get("plano_codigo") or ""),
    )


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