from typing import Any

import httpx
from fastapi import Request

from app.modules.user.userController import API_BASE_URL, authorization_headers


def _api_message(response: httpx.Response, fallback: str) -> str:
    try:
        detail = response.json().get("detail") if response.content else None
    except (ValueError, AttributeError):
        detail = None
    return detail if isinstance(detail, str) else fallback


def _admin_headers(request: Request) -> dict[str, str] | None:
    pessoa_id = request.session.get("id_pessoa")
    token = request.session.get("token")
    if pessoa_id is None or not token:
        return None
    headers = authorization_headers(str(token))
    headers["X-User-ID"] = str(pessoa_id)
    return headers


async def carregar_painel_admin(request: Request) -> dict[str, Any]:
    headers = _admin_headers(request)
    if headers is None:
        return {
            "usuarios": [],
            "profissionais": [],
            "agendas": [],
            "publicacoes": [],
            "admin_error": "Sessão inválida. Faça login novamente.",
        }

    usuarios: list[dict[str, Any]] = []
    profissionais: list[dict[str, Any]] = []
    agendas: list[dict[str, Any]] = []
    publicacoes: list[dict[str, Any]] = []
    erros: list[str] = []

    try:
        async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=10.0) as client:
            res_u = await client.get("/api/admin/usuarios", headers=headers)
            if res_u.is_success:
                usuarios = res_u.json()
            else:
                erros.append(_api_message(res_u, "Erro ao carregar usuários."))

            res_p = await client.get("/api/admin/profissionais", headers=headers)
            if res_p.is_success:
                profissionais = res_p.json()
            else:
                erros.append(_api_message(res_p, "Erro ao carregar profissionais."))

            res_a = await client.get("/api/admin/agendas", headers=headers)
            if res_a.is_success:
                agendas = res_a.json()
            else:
                erros.append(_api_message(res_a, "Erro ao carregar agendas."))

            res_pub = await client.get("/api/admin/publicacoes", headers=headers)
            if res_pub.is_success:
                publicacoes = res_pub.json()
            else:
                erros.append(_api_message(res_pub, "Erro ao carregar publicações."))
    except httpx.RequestError:
        erros.append("Não foi possível conectar à API administrativa.")

    return {
        "usuarios": usuarios,
        "profissionais": profissionais,
        "agendas": agendas,
        "publicacoes": publicacoes,
        "admin_error": " ".join(erros) if erros else None,
    }


async def atualizar_usuario(
    request: Request,
    pessoa_id: int,
    id_tipo_perfil: int,
    ativo: int,
) -> tuple[bool, str]:
    headers = _admin_headers(request)
    if headers is None:
        return False, "Sessão inválida."

    try:
        async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=10.0) as client:
            res = await client.put(
                f"/api/admin/usuarios/{pessoa_id}",
                json={"id_tipo_perfil": id_tipo_perfil, "ativo": bool(ativo)},
                headers=headers,
            )
            if res.is_success:
                return True, res.json().get("message", "Usuário atualizado com sucesso.")
            return False, _api_message(res, "Não foi possível atualizar o usuário.")
    except httpx.RequestError:
        return False, "Falha de conexão com a API."


async def atualizar_status_profissional(
    request: Request,
    pessoa_id: int,
    status_verificacao: str,
) -> tuple[bool, str]:
    headers = _admin_headers(request)
    if headers is None:
        return False, "Sessão inválida."

    try:
        async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=10.0) as client:
            res = await client.put(
                f"/api/admin/profissionais/{pessoa_id}/status",
                json={"status_verificacao": status_verificacao},
                headers=headers,
            )
            if res.is_success:
                return True, res.json().get("message", "Status atualizado com sucesso.")
            return False, _api_message(res, "Não foi possível atualizar o profissional.")
    except httpx.RequestError:
        return False, "Falha de conexão com a API."


async def atualizar_status_agenda(
    request: Request,
    agenda_id: int,
    status: str,
) -> tuple[bool, str]:
    headers = _admin_headers(request)
    if headers is None:
        return False, "Sessão inválida."

    try:
        async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=10.0) as client:
            res = await client.put(
                f"/api/admin/agendas/{agenda_id}/status",
                json={"status": status},
                headers=headers,
            )
            if res.is_success:
                return True, res.json().get("message", "Agendamento atualizado com sucesso.")
            return False, _api_message(res, "Não foi possível atualizar o agendamento.")
    except httpx.RequestError:
        return False, "Falha de conexão com a API."


async def atualizar_status_publicacao(
    request: Request,
    publicacao_id: int,
    ativo: int,
) -> tuple[bool, str]:
    headers = _admin_headers(request)
    if headers is None:
        return False, "Sessão inválida."

    try:
        async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=10.0) as client:
            res = await client.put(
                f"/api/admin/publicacoes/{publicacao_id}/status",
                json={"ativo": bool(ativo)},
                headers=headers,
            )
            if res.is_success:
                return True, res.json().get("message", "Publicação atualizada com sucesso.")
            return False, _api_message(res, "Não foi possível moderar a publicação.")
    except httpx.RequestError:
        return False, "Falha de conexão com a API."
