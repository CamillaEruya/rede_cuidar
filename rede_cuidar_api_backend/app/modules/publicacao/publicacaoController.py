
from typing import Any

from fastapi import HTTPException, UploadFile
from sqlalchemy.exc import SQLAlchemyError

from app.core.image_upload import store_image
from app.modules.publicacao import publicacaoModel as model
from app.modules.user import userController


PUBLICACAO_FIELDS = {
    "descricao",
    "foto",
}


def _publicacao_data(
    data: dict[str, Any],
) -> dict[str, Any]:

    publicacao_data = {
        key: value
        for key, value in data.items()
        if key in PUBLICACAO_FIELDS
    }

    descricao = publicacao_data.get("descricao")
    foto = publicacao_data.get("foto")

    if descricao is not None:
        if not isinstance(descricao, str):
            raise HTTPException(
                status_code=400,
                detail="Descrição inválida."
            )

        descricao = descricao.strip()

        if len(descricao) > 1000:
            raise HTTPException(
                status_code=400,
                detail="A descrição deve ter no máximo 1000 caracteres."
            )

        publicacao_data["descricao"] = descricao or None

    if foto is not None:
        if not isinstance(foto, str) or not foto.strip():
            raise HTTPException(
                status_code=400,
                detail="Caminho da foto inválido."
            )

        foto = foto.strip()

        if len(foto) > 255:
            raise HTTPException(
                status_code=400,
                detail="Caminho da foto muito longo."
            )

        publicacao_data["foto"] = foto

    return publicacao_data


def get_publicacoes(
    pessoa_id: int,
    token: str,
) -> list[dict[str, Any]]:

    userController.autenticar(pessoa_id, token)

    return model.listar_publicacoes()


def post_publicacao(
    pessoa_id: int,
    data: dict[str, Any],
    token: str,
) -> dict[str, Any]:

    userController.autenticar(pessoa_id, token)
    return _criar_publicacao(pessoa_id, data)


def _criar_publicacao(
    pessoa_id: int,
    data: dict[str, Any],
) -> dict[str, Any]:
    publicacao_data = _publicacao_data(data)
    if (
        not publicacao_data.get("descricao")
        and not publicacao_data.get("foto")
    ):
        raise HTTPException(
            status_code=400,
            detail="Informe uma descrição ou foto."
        )

    publicacao_data["id_pessoa"] = pessoa_id

    publicacao_id = model.cadastrar_publicacao(
        publicacao_data
    )

    return {
        "success": True,
        "message": "Publicação cadastrada com sucesso.",
        "id_publicacao": publicacao_id,
    }


async def post_publicacao_com_foto(
    pessoa_id: int,
    descricao: str,
    foto: UploadFile,
    token: str,
) -> dict[str, Any]:
    userController.autenticar(pessoa_id, token)

    caminho_publico, caminho_arquivo = await store_image(foto, "publicacoes")

    try:
        return _criar_publicacao(
            pessoa_id,
            {"descricao": descricao, "foto": caminho_publico},
        )
    except (HTTPException, SQLAlchemyError):
        caminho_arquivo.unlink(missing_ok=True)
        raise


def put_publicacao(
    publicacao_id: int,
    pessoa_id: int,
    data: dict[str, Any],
    token: str,
) -> dict[str, Any]:

    userController.autenticar(pessoa_id, token)

    publicacao = model.buscar_publicacao(publicacao_id)

    if publicacao is None:
        raise HTTPException(
            status_code=404,
            detail="Publicação não encontrada."
        )

    if publicacao["id_pessoa"] != pessoa_id:
        raise HTTPException(
            status_code=403,
            detail="Você não pode editar esta publicação."
        )

    publicacao_data = _publicacao_data(data)

    descricao = publicacao_data.get(
        "descricao",
        publicacao.get("descricao")
    )

    foto = publicacao_data.get(
        "foto",
        publicacao.get("foto")
    )

    if not descricao and not foto:
        raise HTTPException(
            status_code=400,
            detail="A publicação precisa ter descrição ou foto."
        )

    if not publicacao_data:
        raise HTTPException(
            status_code=400,
            detail="Nenhum campo informado para atualização."
        )

    if not model.atualizar_publicacao(
        publicacao_id,
        pessoa_id,
        publicacao_data,
    ):
        raise HTTPException(
            status_code=404,
            detail="Publicação não encontrada ou não atualizada."
        )

    return {
        "success": True,
        "message": "Publicação atualizada com sucesso."
    }


def delete_publicacao(
    publicacao_id: int,
    pessoa_id: int,
    token: str,
) -> dict[str, Any]:

    userController.autenticar(pessoa_id, token)

    publicacao = model.buscar_publicacao(publicacao_id)

    if publicacao is None:
        raise HTTPException(
            status_code=404,
            detail="Publicação não encontrada."
        )

    if publicacao["id_pessoa"] != pessoa_id:
        raise HTTPException(
            status_code=403,
            detail="Você não pode excluir esta publicação."
        )

    if not model.deletar_publicacao(
        publicacao_id,
        pessoa_id,
    ):
        raise HTTPException(
            status_code=404,
            detail="Publicação não encontrada."
        )

    return {
        "success": True,
        "message": "Publicação excluída com sucesso."
    }
