from typing import Any

import httpx
from fastapi import Request, UploadFile

from app.modules.user import userController
from app.modules.user.userController import API_BASE_URL, authorization_headers

MAX_FOTO_SIZE = 5 * 1024 * 1024


def _api_message(response: httpx.Response, fallback: str) -> str:
    try:
        detail = response.json().get("detail") if response.content else None
    except (ValueError, AttributeError):
        detail = None

    return detail if isinstance(detail, str) else fallback


async def listar_publicacoes(
    request: Request,
) -> tuple[list[dict[str, Any]], str | None]:
    pessoa_id = request.session.get("id_pessoa")
    token = request.session.get("token")

    if pessoa_id is None or not token:
        return [], "Sessão inválida. Faça login novamente."

    try:
        async with httpx.AsyncClient(
            base_url=API_BASE_URL,
            timeout=8.0,
        ) as client:
            response = await client.get(
                "/api/publicacoes",
                headers={
                    "X-User-ID": str(pessoa_id),
                    **authorization_headers(token),
                },
            )
            response.raise_for_status()
            payload = response.json()
    except httpx.RequestError:
        return [], "Não foi possível conectar à API para carregar o feed."
    except httpx.HTTPStatusError as error:
        return [], _api_message(
            error.response,
            "A API não conseguiu carregar as publicações. Tente novamente.",
        )
    except ValueError:
        return [], "A API retornou uma lista de publicações inválida."

    if not isinstance(payload, list) or not all(
        isinstance(publicacao, dict) for publicacao in payload
    ):
        return [], "A API retornou uma lista de publicações inválida."

    publicacoes = []
    for index, publicacao in enumerate(payload):
        nome = publicacao.get("nome_razao") or "Pessoa da comunidade"
        foto = publicacao.get("foto")
        foto_url = None
        if isinstance(foto, str):
            if foto.startswith("/uploads/"):
                foto_url = f"{API_BASE_URL}{foto}"
            elif foto.startswith(("http://", "https://")):
                foto_url = foto
        foto_perfil = publicacao.get("foto_perfil")
        foto_perfil_url = None
        if isinstance(foto_perfil, str):
            if foto_perfil.startswith("/uploads/"):
                foto_perfil_url = f"{API_BASE_URL}{foto_perfil}"
            elif foto_perfil.startswith(("http://", "https://")):
                foto_perfil_url = foto_perfil
        publicacoes.append(
            {
                **publicacao,
                "nome_razao": nome,
                "iniciais": userController.iconAvatar(nome),
                "avatar_class": (
                    "avatar-peach",
                    "avatar-mint",
                    "avatar-blue",
                    "avatar-lilac",
                )[index % 4],
                "foto_url": foto_url,
                "foto_perfil_url": foto_perfil_url,
            }
        )

    return publicacoes, None


async def criar_publicacao(
    request: Request,
    descricao: str,
    foto: UploadFile | None = None,
) -> tuple[bool, str]:
    pessoa_id = request.session.get("id_pessoa")
    token = request.session.get("token")

    if pessoa_id is None or not token:
        return False, "Sessão inválida. Faça login novamente."

    descricao = descricao.strip()
    if len(descricao) > 1000:
        return False, "A publicação deve ter no máximo 1000 caracteres."
    if not descricao and foto is None:
        return False, "Escreva algo ou selecione uma foto para publicar."

    try:
        if foto is not None and foto.filename:
            conteudo = await foto.read(MAX_FOTO_SIZE + 1)
            if len(conteudo) > MAX_FOTO_SIZE:
                return False, "A foto deve ter no máximo 5 MB."
            if not conteudo:
                return False, "O arquivo selecionado está vazio."

            request_args = {
                "data": {"descricao": descricao},
                "files": {
                    "foto": (
                        foto.filename,
                        conteudo,
                        foto.content_type or "application/octet-stream",
                    )
                },
            }
            endpoint = "/api/publicacoes/com-foto"
        else:
            request_args = {"json": {"descricao": descricao}}
            endpoint = "/api/publicacoes"

        async with httpx.AsyncClient(
            base_url=API_BASE_URL,
            timeout=8.0,
        ) as client:
            response = await client.post(
                endpoint,
                headers={
                    "X-User-ID": str(pessoa_id),
                    **authorization_headers(token),
                },
                **request_args,
            )
            response.raise_for_status()
            payload = response.json()
    except httpx.RequestError:
        return False, "Não foi possível conectar à API. Verifique se ela está ativa."
    except httpx.HTTPStatusError as error:
        return False, _api_message(
            error.response,
            "Não foi possível publicar. Tente novamente.",
        )
    except ValueError:
        return False, "A API retornou uma resposta inválida ao publicar."

    if not isinstance(payload, dict) or payload.get("success") is not True:
        return False, "A API não confirmou a publicação."

    message = payload.get("message")
    return True, (
        message
        if isinstance(message, str)
        else "Publicação compartilhada com sucesso."
    )
