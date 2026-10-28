from typing import Any

from fastapi import Request
import httpx

from app.modules.user.userController import API_BASE_URL

from app.modules.user import userController

async def perfil_context(request: Request) -> dict[str, Any]:
    try:
        async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=8.0) as client:
            response = await client.get(f"/api/pessoas/{request.session.get('id_pessoa')}")
            response.raise_for_status()
            payload = response.json()

            response_tipos = await client.get("/api/pessoas/tipo-perfil")
            response_tipos.raise_for_status()
            tipos_perfil = response_tipos.json()

        if not isinstance(payload, list) or not payload:
            raise ValueError("Nenhum registro de pessoa foi retornado.")

        pessoa = payload[0]
        if not isinstance(pessoa, dict):
            raise ValueError("O registro de pessoa retornado é inválido.")

        if not isinstance(tipos_perfil, list):
            raise ValueError("A lista de tipos de perfil é inválida.")

        id_tipo_perfil = pessoa.get("id_tipo_perfil")

        perfil_nome = next(
            (
                perfil.get("nome")
                for perfil in tipos_perfil
                if isinstance(perfil, dict)
                and str(perfil.get("id_tipo_perfil")) == str(id_tipo_perfil)
            ),
            "Não informado"
            )

        return {
            'request': request,
            "nome_razao": pessoa.get("nome_razao"),
            "icon_nome_razao": userController.iconAvatar(pessoa.get("nome_razao")),
            "email": pessoa.get("email"),
            "tipo": pessoa.get("tipo"),
            "cpf_cnpj": pessoa.get("cpf_cnpj"),
            "perfil": pessoa.get("id_tipo_pessoa"),
            "id_tipo_perfil": pessoa.get("id_tipo_perfil"),
            "perfil_nome": perfil_nome,
            "tipos_perfil": tipos_perfil,
        }
    except (httpx.HTTPError, ValueError):
        return {
            'request': request,
            "nome_razao": "",
            "icon_nome_razao": "",
            "email": "",
            "tipo": "",
            "cpf_cnpj": "",
            "perfil": "",
            "id_tipo_perfil": None,
            "perfil_nome": "Não informado",
            "tipos_perfil": [],
        }

async def atualizar(
    request: Request,
    data: dict[str, Any]
) -> tuple[bool, str]:

    id_pessoa = request.session.get("id_pessoa")
    token = request.session.get("token")

    if not id_pessoa:
        return False, "Usuário não identificado. Faça login novamente."

    if data.get("senha") != data.get("confirmar_senha"):
        return False, "As senhas não coincidem."

    try:
        async with httpx.AsyncClient(
            base_url=API_BASE_URL,
            timeout=8.0
        ) as client:
            
            response = await client.put(
                f"/api/pessoas/{id_pessoa}",
                headers={
                    "Authorization": f"Bearer {token}",
                },
                json=data
            )

    except httpx.RequestError:
        return False, "Não foi possível conectar ao servidor. Verifique se a API está ativa."

    if response.is_success:
        return True, "Cadastro atualizado com sucesso."

    try:
        detail = response.json().get("detail") if response.content else None
    except (ValueError, AttributeError):
        detail = None

    if isinstance(detail, str):
        return False, detail

    return False, f"Não foi possível atualizar o cadastro."
    


    