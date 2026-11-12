from typing import Any
from typing import Literal

import httpx
from fastapi import Request
from pydantic import BaseModel, Field

from app.modules.user.userController import API_BASE_URL, authorization_headers
from app.modules.user import userController


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)
    history: list[ChatMessage] = Field(default_factory=list, max_length=8)


def biblioteca_context(request: Request) -> dict[str, Any]:
    nome_razao = request.session.get("nome_razao", "")

    return {
        "request": request,
        "nome_razao": nome_razao,
        "icon_nome_razao": userController.iconAvatar(nome_razao) if nome_razao else "",
    }


def _api_message(response: httpx.Response, fallback: str) -> str:
    try:
        detail = response.json().get("detail") if response.content else None
    except (ValueError, AttributeError):
        detail = None

    return detail if isinstance(detail, str) else fallback


async def buscar_noticias(
    request: Request,
) -> tuple[dict[str, Any] | None, str | None, int]:
    pessoa_id = request.session.get("id_pessoa")
    token = request.session.get("token")
    if pessoa_id is None or not token:
        return None, "Sessão inválida. Faça login novamente.", 401

    try:
        async with httpx.AsyncClient(
            base_url=API_BASE_URL,
            timeout=18.0,
        ) as client:
            response = await client.get(
                "/api/biblioteca/noticias",
                headers={
                    "X-User-ID": str(pessoa_id),
                    **authorization_headers(token),
                },
            )
            response.raise_for_status()
            result = response.json()
    except httpx.RequestError:
        return None, "Não foi possível conectar à API. Verifique se ela está ativa.", 503
    except httpx.HTTPStatusError as error:
        return (
            None,
            _api_message(error.response, "Não foi possível buscar notícias agora."),
            error.response.status_code,
        )
    except ValueError:
        return None, "A API retornou uma resposta inválida.", 502

    articles = result.get("articles") if isinstance(result, dict) else None
    if (
        not isinstance(articles, list)
        or len(articles) > 3
        or not all(
            isinstance(article, dict)
            and all(
                isinstance(article.get(field), str)
                for field in ("source", "date", "title", "summary", "url")
            )
            and article["url"].startswith("https://news.google.com/")
            for article in articles
        )
    ):
        return None, "A API retornou uma lista de notícias inválida.", 502

    return result, None, 200


async def enviar_mensagem(
    request: Request,
    data: ChatRequest,
) -> tuple[dict[str, Any] | None, str | None, int]:
    pessoa_id = request.session.get("id_pessoa")
    token = request.session.get("token")
    if pessoa_id is None or not token:
        return None, "Sessão inválida. Faça login novamente.", 401

    payload = {
        "message": data.message,
        "history": [message.model_dump() for message in data.history[-8:]],
    }
    try:
        async with httpx.AsyncClient(
            base_url=API_BASE_URL,
            timeout=60.0,
        ) as client:
            response = await client.post(
                "/api/biblioteca/chat",
                headers={
                    "X-User-ID": str(pessoa_id),
                    **authorization_headers(token),
                },
                json=payload,
            )
            response.raise_for_status()
            result = response.json()
    except httpx.RequestError:
        return (
            None,
            "Não foi possível conectar à API. Verifique se ela está ativa.",
            503,
        )
    except httpx.HTTPStatusError as error:
        return (
            None,
            _api_message(
                error.response,
                "Não foi possível responder à mensagem. Tente novamente.",
            ),
            error.response.status_code,
        )
    except ValueError:
        return None, "A API retornou uma resposta inválida.", 502

    if (
        not isinstance(result, dict)
        or not isinstance(result.get("answer"), str)
        or not isinstance(result.get("sources"), list)
        or not all(
            isinstance(source, dict)
            and isinstance(source.get("document"), str)
            and isinstance(source.get("page"), int)
            for source in result["sources"]
        )
    ):
        return None, "A API retornou uma resposta inválida.", 502

    return result, None, 200
