
from typing import Any

from fastapi import (
    APIRouter,
    Body,
    Depends,
    File,
    Form,
    Header,
    UploadFile,
)
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer,
)

from app.modules.publicacao import (
    publicacaoController as controller
)


router = APIRouter(
    prefix="/api/publicacoes",
    tags=["Publicações"]
)

bearer_scheme = HTTPBearer()


@router.get("")
def get_publicacoes(
    pessoa_id: int = Header(..., alias="X-User-ID"),
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_scheme
    ),
) -> list[dict[str, Any]]:

    return controller.get_publicacoes(
        pessoa_id,
        credentials.credentials
    )


@router.post("", status_code=201)
def post_publicacao(
    data: dict[str, Any] = Body(...),
    pessoa_id: int = Header(..., alias="X-User-ID"),
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_scheme
    ),
) -> dict[str, Any]:

    return controller.post_publicacao(
        pessoa_id,
        data,
        credentials.credentials
    )


@router.post("/com-foto", status_code=201)
async def post_publicacao_com_foto(
    descricao: str = Form(""),
    foto: UploadFile = File(...),
    pessoa_id: int = Header(..., alias="X-User-ID"),
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict[str, Any]:
    return await controller.post_publicacao_com_foto(
        pessoa_id,
        descricao,
        foto,
        credentials.credentials,
    )


@router.put("/{publicacao_id}")
def put_publicacao(
    publicacao_id: int,
    data: dict[str, Any] = Body(...),
    pessoa_id: int = Header(..., alias="X-User-ID"),
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_scheme
    ),
) -> dict[str, Any]:

    return controller.put_publicacao(
        publicacao_id,
        pessoa_id,
        data,
        credentials.credentials
    )


@router.delete("/{publicacao_id}")
def delete_publicacao(
    publicacao_id: int,
    pessoa_id: int = Header(..., alias="X-User-ID"),
    credentials: HTTPAuthorizationCredentials = Depends(
        bearer_scheme
    ),
) -> dict[str, Any]:

    return controller.delete_publicacao(
        publicacao_id,
        pessoa_id,
        credentials.credentials
    )
