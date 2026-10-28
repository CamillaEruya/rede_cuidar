import os
from typing import Any

import httpx
from dotenv import load_dotenv
from fastapi import Request

load_dotenv()
API_BASE_URL = os.getenv("API_BASE_URL", "").rstrip("/")


def home_context(request: Request, message: str | None = None) -> dict[str, Any]:
    return {
        "request": request,
        "message": message,
        "api_url": API_BASE_URL,
    }


async def listar_tipos_perfil() -> list[dict[str, Any]]:
    try:
        async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=8.0) as client:
            response = await client.get("/api/pessoas/tipo-perfil")
            response.raise_for_status()
            payload = response.json()
    except (httpx.HTTPError, ValueError):
        return []

    if not isinstance(payload, list):
        return []
    return [perfil for perfil in payload if isinstance(perfil, dict)]


async def cadastrar_pessoa(data: dict[str, Any]) -> tuple[bool, str]:
    try:
        async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=8.0) as client:
            response = await client.post("/api/pessoas", json=data)
    except httpx.RequestError:
        return False, "Não foi possível conectar ao servidor. Verifique se a API está ativa."

    if response.is_success:
        return True, "Cadastro realizado com sucesso. Agora você pode entrar na rede."

    detail = response.json().get("detail") if response.content else None
    if isinstance(detail, str):
        return False, detail
    return False, "Não foi possível concluir o cadastro. Revise os dados e tente novamente."


async def logar(request: Request, data: dict[str, Any]) -> tuple[bool, str]:
    try:
        async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=8.0) as client:
            response = await client.post("/api/user/login", json=data)
    except httpx.RequestError:
        return False, "Não foi possível conectar ao servidor. Verifique se a API está ativa."

    if response.is_success:
        payload = response.json()

        request.session["id_pessoa"] = payload.get("id_pessoa")
        request.session["token"] = payload.get("token")
        request.session["nome_razao"] = payload.get("nome_razao")

        return True, "Login realizado com sucesso. Bem-vindo à rede."

    detail = response.json().get("detail") if response.content else None
    if isinstance(detail, str):
        return False, detail
    return False, "Não foi possível concluir o login. Revise os dados e tente novamente."