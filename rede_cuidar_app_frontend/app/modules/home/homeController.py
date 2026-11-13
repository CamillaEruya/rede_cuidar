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
    return [
        perfil
        for perfil in payload
        if isinstance(perfil, dict) and perfil.get("id_tipo_perfil") != 9
    ]


async def cadastrar_pessoa(data: dict[str, Any]) -> tuple[bool, str]:
    if int(data.get("id_tipo_perfil", 0)) == 9:
        return False, "Tipo de perfil inválido para cadastro público."

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
            if response.is_success:
                payload = response.json()
                id_pessoa = payload.get("id_pessoa")
                id_tipo_perfil = payload.get("id_tipo_perfil")

                if id_tipo_perfil is None and id_pessoa is not None:
                    res_pessoa = await client.get(f"/api/pessoas/{id_pessoa}")
                    if res_pessoa.is_success:
                        dados_pessoa = res_pessoa.json()
                        if isinstance(dados_pessoa, list) and dados_pessoa:
                            id_tipo_perfil = dados_pessoa[0].get("id_tipo_perfil")
                        elif isinstance(dados_pessoa, dict):
                            id_tipo_perfil = dados_pessoa.get("id_tipo_perfil")

                request.session["id_pessoa"] = id_pessoa
                request.session["token"] = payload.get("token")
                request.session["nome_razao"] = payload.get("nome_razao")
                request.session["id_tipo_perfil"] = id_tipo_perfil

                return True, "Login realizado com sucesso. Bem-vindo à rede."
    except httpx.RequestError:
        return False, "Não foi possível conectar ao servidor. Verifique se a API está ativa."

    detail = response.json().get("detail") if response.content else None
    if isinstance(detail, str):
        return False, detail
    return False, "Não foi possível concluir o login. Revise os dados e tente novamente."
