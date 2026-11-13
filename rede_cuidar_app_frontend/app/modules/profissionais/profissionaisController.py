import re
from typing import Any, Optional

import httpx
from fastapi import Request, UploadFile

from app.modules.user import userController
from app.modules.user.userController import API_BASE_URL, authorization_headers


def _montar_whatsapp_url(telefone: str | None) -> str | None:
    if not telefone:
        return None
    digitos = re.sub(r"\D", "", telefone)
    if len(digitos) < 10:
        return None
    if not digitos.startswith("55"):
        digitos = f"55{digitos}"
    return f"https://wa.me/{digitos}"


def _extract_error(response: httpx.Response, fallback: str) -> str:
    try:
        payload = response.json()
        if isinstance(payload, dict):
            detail = payload.get("detail") or payload.get("message")
            if isinstance(detail, str) and detail.strip():
                return detail.strip()
    except ValueError:
        pass
    return fallback


async def profissionais_context(request: Request) -> dict[str, Any]:
    nome_razao = request.session.get("nome_razao", "")
    pessoa_id = request.session.get("id_pessoa")
    token = request.session.get("token")
    profissionais: list[dict[str, Any]] = []
    profissionais_error = None

    try:
        async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=8.0) as client:
            response = await client.get(
                "/api/profissional",
                headers={
                    "X-User-ID": str(pessoa_id),
                    **authorization_headers(token or ""),
                },
            )
            response.raise_for_status()
            payload = response.json()

        if not isinstance(payload, list) or not all(
            isinstance(profissional, dict) for profissional in payload
        ):
            raise ValueError("A API retornou uma lista de profissionais inválida.")

        for index, profissional in enumerate(payload):
            nome = profissional.get("nome_razao") or "Profissional"
            iniciais = "".join(parte[0] for parte in nome.split()[:2]).upper()
            telefone = profissional.get("telefone")
            profissionais.append(
                {
                    "id_profissional": profissional.get("id_profissional"),
                    "nome": nome,
                    "iniciais": iniciais or "PR",
                    "especialidade": profissional.get("area_atuacao")
                    or profissional.get("inscricao_conselho")
                    or "Profissional",
                    "descricao": profissional.get("descricao") or "",
                    "localidade": ", ".join(
                        valor
                        for valor in (
                            profissional.get("cidade"),
                            profissional.get("estado"),
                        )
                        if valor
                    )
                    or "Localidade não informada",
                    "inscricao_conselho": profissional.get("inscricao_conselho"),
                    "telefone": telefone,
                    "whatsapp_url": _montar_whatsapp_url(telefone),
                    "destaque": bool(profissional.get("destaque")),
                    "campanha_plano": profissional.get("campanha_plano"),
                    "divulgacoes": profissional.get("divulgacoes") or [],
                    "avatar": ("avatar-mint", "avatar-lilac", "avatar-blue")[
                        index % 3
                    ],
                }
            )
    except httpx.RequestError:
        profissionais_error = (
            "Não foi possível carregar os profissionais. Verifique a conexão e tente novamente."
        )
    except httpx.HTTPStatusError:
        profissionais_error = (
            "A API não conseguiu carregar os profissionais. Tente novamente mais tarde."
        )
    except ValueError:
        profissionais_error = "A resposta da lista de profissionais é inválida."

    return {
        "request": request,
        "nome_razao": nome_razao,
        "foto_perfil_url": request.session.get("foto_perfil_url"),
        "icon_nome_razao": userController.iconAvatar(nome_razao) if nome_razao else "",
        "profissionais": profissionais,
        "profissionais_error": profissionais_error,
    }


async def painel_context(request: Request) -> dict[str, Any]:
    nome_razao = request.session.get("nome_razao", "")
    pessoa_id = request.session.get("id_pessoa")
    token = request.session.get("token")

    painel: dict[str, Any] = {
        "cadastrado": False,
        "aprovado": False,
        "status_verificacao": "NAO_CADASTRADO",
        "profissional": None,
        "divulgacoes": [],
        "campanhas": [],
        "campanha_ativa": None,
        "planos": [],
    }
    painel_error = None

    try:
        async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=8.0) as client:
            response = await client.get(
                "/api/profissional/painel",
                headers={
                    "X-User-ID": str(pessoa_id),
                    **authorization_headers(token or ""),
                },
            )
            response.raise_for_status()
            data = response.json()
            if isinstance(data, dict):
                painel.update(data)
    except httpx.HTTPStatusError as exc:
        painel_error = _extract_error(
            exc.response,
            "Não foi possível carregar os dados do painel profissional.",
        )
    except httpx.RequestError:
        painel_error = "Não foi possível conectar à API do painel profissional."

    return {
        "request": request,
        "nome_razao": nome_razao,
        "foto_perfil_url": request.session.get("foto_perfil_url"),
        "icon_nome_razao": userController.iconAvatar(nome_razao) if nome_razao else "",
        "painel": painel,
        "painel_error": painel_error,
    }


async def publicar_divulgacao(
    request: Request,
    titulo: str,
    descricao: str,
    midia: Optional[UploadFile] = None,
) -> tuple[bool, str]:
    pessoa_id = request.session.get("id_pessoa")
    token = request.session.get("token")

    files: dict[str, Any] = {}
    if midia is not None and midia.filename:
        conteudo = await midia.read()
        if conteudo:
            files["midia"] = (
                midia.filename,
                conteudo,
                midia.content_type or "application/octet-stream",
            )

    try:
        async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=30.0) as client:
            response = await client.post(
                "/api/profissional/divulgacao",
                headers={
                    "X-User-ID": str(pessoa_id),
                    **authorization_headers(token or ""),
                },
                data={
                    "titulo": titulo.strip(),
                    "descricao": descricao.strip(),
                },
                files=files or None,
            )
            if response.status_code >= 400:
                return False, _extract_error(
                    response,
                    "Não foi possível publicar a divulgação.",
                )
            payload = response.json()
            return True, payload.get("message") or "Divulgação publicada com sucesso!"
    except httpx.RequestError:
        return False, "Erro de conexão ao publicar divulgação."


async def excluir_divulgacao(
    request: Request,
    id_divulgacao: int,
) -> tuple[bool, str]:
    pessoa_id = request.session.get("id_pessoa")
    token = request.session.get("token")

    try:
        async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=10.0) as client:
            response = await client.delete(
                f"/api/profissional/divulgacao/{id_divulgacao}",
                headers={
                    "X-User-ID": str(pessoa_id),
                    **authorization_headers(token or ""),
                },
            )
            if response.status_code >= 400:
                return False, _extract_error(
                    response,
                    "Não foi possível excluir a divulgação.",
                )
            payload = response.json()
            return True, payload.get("message") or "Divulgação excluída."
    except httpx.RequestError:
        return False, "Erro de conexão ao excluir divulgação."


async def ativar_campanha(
    request: Request,
    plano_codigo: str,
) -> tuple[bool, str]:
    pessoa_id = request.session.get("id_pessoa")
    token = request.session.get("token")

    try:
        async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=10.0) as client:
            response = await client.post(
                "/api/profissional/campanha",
                headers={
                    "X-User-ID": str(pessoa_id),
                    **authorization_headers(token or ""),
                },
                json={"plano_codigo": plano_codigo},
            )
            if response.status_code >= 400:
                return False, _extract_error(
                    response,
                    "Não foi possível ativar a campanha.",
                )
            payload = response.json()
            return True, payload.get("message") or "Campanha ativada com sucesso!"
    except httpx.RequestError:
        return False, "Erro de conexão ao ativar campanha."