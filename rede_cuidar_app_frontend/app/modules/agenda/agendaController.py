import os
from typing import Any, Optional
import httpx
from fastapi import Request, UploadFile

from app.modules.user import userController
from app.modules.user.userController import API_BASE_URL, authorization_headers

API_PUBLIC_URL = os.getenv("API_PUBLIC_URL", "http://localhost:8001").rstrip("/")


def eh_admin(request: Request) -> bool:
    return request.session.get("id_tipo_perfil") == 9


def _headers_admin(request: Request) -> dict[str, str] | None:
    pessoa_id = request.session.get("id_pessoa")
    token = request.session.get("token")
    if not pessoa_id or not token:
        return None
    headers = authorization_headers(str(token))
    headers["X-User-ID"] = str(pessoa_id)
    return headers


def agenda_context(request: Request) -> dict[str, Any]:
    nome_razao = request.session.get("nome_razao", "")
    is_admin = eh_admin(request)
    eventos: list[dict[str, Any]] = []

    try:
        with httpx.Client(base_url=API_BASE_URL, timeout=5.0) as client:
            response = client.get(
                "/api/agenda/disponiveis",
                params={"incluir_inativos": is_admin}
            )
            if response.status_code == 200:
                eventos = response.json()
                for ev in eventos:
                    url = ev.get("midia_url")
                    if url and url.startswith("/"):
                        ev["midia_url"] = f"{API_PUBLIC_URL}{url}"
    except Exception as e:
        print(f"Aviso: Não foi possível carregar agenda da API backend ({e}).")

    return {
        "request": request,
        "nome_razao": nome_razao,
        "icon_nome_razao": userController.iconAvatar(nome_razao) if nome_razao else "",
        "eh_admin": is_admin,
        "eventos": eventos,
        "flash_msg": request.query_params.get("msg"),
        "flash_type": request.query_params.get("tipo", "success"),
    }


async def criar_evento(
    request: Request,
    titulo: str,
    descricao: str,
    tipo_evento: str,
    data_evento: str,
    midia: Optional[UploadFile] = None,
) -> tuple[bool, str]:
    headers = _headers_admin(request)
    if headers is None or not eh_admin(request):
        return False, "Apenas administradores podem publicar na agenda."

    files = None
    if midia and midia.filename:
        conteudo = await midia.read()
        if conteudo:
            files = {
                "midia": (midia.filename, conteudo, midia.content_type or "application/octet-stream")
            }

    try:
        async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=30.0) as client:
            res = await client.post(
                "/api/agenda",
                data={
                    "titulo": titulo,
                    "descricao": descricao,
                    "tipo_evento": tipo_evento,
                    "data_evento": data_evento,
                },
                files=files,
                headers=headers,
            )
            if res.is_success:
                return True, res.json().get("message", "Evento publicado com sucesso.")
            detail = res.json().get("detail") if res.content else None
            return False, detail or "Erro ao publicar evento."
    except httpx.RequestError:
        return False, "Falha de comunicação com a API."


async def atualizar_evento(
    request: Request,
    id_agenda: int,
    titulo: str,
    descricao: str,
    tipo_evento: str,
    data_evento: str,
    status: str,
    remover_midia: bool = False,
    midia: Optional[UploadFile] = None,
) -> tuple[bool, str]:
    headers = _headers_admin(request)
    if headers is None or not eh_admin(request):
        return False, "Apenas administradores podem atualizar eventos da agenda."

    files = None
    if midia and midia.filename:
        conteudo = await midia.read()
        if conteudo:
            files = {
                "midia": (midia.filename, conteudo, midia.content_type or "application/octet-stream")
            }

    try:
        async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=30.0) as client:
            res = await client.put(
                f"/api/agenda/{id_agenda}",
                data={
                    "titulo": titulo,
                    "descricao": descricao,
                    "tipo_evento": tipo_evento,
                    "data_evento": data_evento,
                    "status": status,
                    "remover_midia": "true" if remover_midia else "false",
                },
                files=files,
                headers=headers,
            )
            if res.is_success:
                return True, res.json().get("message", "Evento atualizado com sucesso.")
            detail = res.json().get("detail") if res.content else None
            return False, detail or "Erro ao atualizar evento."
    except httpx.RequestError:
        return False, "Falha de comunicação com a API."


async def excluir_evento(request: Request, id_agenda: int) -> tuple[bool, str]:
    headers = _headers_admin(request)
    if headers is None or not eh_admin(request):
        return False, "Apenas administradores podem excluir eventos da agenda."

    try:
        async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=10.0) as client:
            res = await client.delete(f"/api/agenda/{id_agenda}", headers=headers)
            if res.is_success:
                return True, res.json().get("message", "Publicação excluída com sucesso.")
            detail = res.json().get("detail") if res.content else None
            return False, detail or "Erro ao excluir publicação."
    except httpx.RequestError:
        return False, "Falha de comunicação com a API."