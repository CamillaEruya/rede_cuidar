import re
from typing import Any

import httpx
from fastapi import Request, UploadFile

from app.modules.user import userController
from app.modules.user.userController import API_BASE_URL, authorization_headers

PROFISSIONAL_FIELDS = (
    "endereco",
    "numero",
    "cidade",
    "estado",
    "cep",
    "telefone",
    "descricao",
    "inscricao_conselho",
    "area_atuacao",
)


async def perfil_context(request: Request) -> dict[str, Any]:
    pessoa_id = request.session.get("id_pessoa")
    token = request.session.get("token")

    try:
        async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=8.0) as client:
            response = await client.get(f"/api/pessoas/{pessoa_id}")
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
            "Não informado",
        )

        documento = re.sub(
            r"[^0-9A-Z]",
            "",
            str(pessoa.get("cpf_cnpj") or "").upper(),
        )
        is_cnpj = len(documento) == 14
        profissional = {field: "" for field in PROFISSIONAL_FIELDS}
        profissional["status_verificacao"] = "PENDENTE"
        profissional_cadastrado = False
        profissional_error = None

        if is_cnpj:
            try:
                async with httpx.AsyncClient(
                    base_url=API_BASE_URL,
                    timeout=8.0,
                ) as client:
                    response_profissional = await client.get(
                        f"/api/profissional/{pessoa_id}",
                        headers=authorization_headers(token or ""),
                    )

                if response_profissional.status_code != 404:
                    response_profissional.raise_for_status()
                    payload_profissional = response_profissional.json()
                    if not isinstance(payload_profissional, dict):
                        raise ValueError("O cadastro profissional retornado é inválido.")
                    profissional.update(
                        {
                            field: payload_profissional.get(field) or ""
                            for field in PROFISSIONAL_FIELDS
                        }
                    )
                    profissional["status_verificacao"] = payload_profissional.get(
                        "status_verificacao",
                        "PENDENTE",
                    )
                    profissional_cadastrado = True
            except httpx.HTTPError:
                profissional_error = (
                    "Não foi possível carregar os dados profissionais. Tente novamente."
                )
            except ValueError:
                profissional_error = "A resposta dos dados profissionais é inválida."

        return {
            "request": request,
            "nome_razao": pessoa.get("nome_razao"),
            "icon_nome_razao": userController.iconAvatar(pessoa.get("nome_razao") or ""),
            "foto_perfil_url": (
                f"{API_BASE_URL}{pessoa['foto_perfil']}"
                if isinstance(pessoa.get("foto_perfil"), str)
                and pessoa["foto_perfil"].startswith("/uploads/")
                else None
            ),
            "email": pessoa.get("email"),
            "tipo": pessoa.get("tipo"),
            "cpf_cnpj": pessoa.get("cpf_cnpj"),
            "perfil": pessoa.get("id_tipo_pessoa"),
            "id_tipo_perfil": id_tipo_perfil,
            "perfil_nome": perfil_nome,
            "tipos_perfil": tipos_perfil,
            "is_cnpj": is_cnpj,
            "profissional": profissional,
            "profissional_cadastrado": profissional_cadastrado,
            "profissional_error": profissional_error,
        }
    except (httpx.HTTPError, ValueError):
        return {
            "request": request,
            "nome_razao": "",
            "icon_nome_razao": "",
            "foto_perfil_url": None,
            "email": "",
            "tipo": "",
            "cpf_cnpj": "",
            "perfil": "",
            "id_tipo_perfil": None,
            "perfil_nome": "Não informado",
            "tipos_perfil": [],
            "is_cnpj": False,
            "profissional": {field: "" for field in PROFISSIONAL_FIELDS},
            "profissional_cadastrado": False,
            "profissional_error": None,
        }


async def atualizar_profissional(
    request: Request,
    data: dict[str, Any],
) -> tuple[bool, str]:
    pessoa_id = request.session.get("id_pessoa")
    token = request.session.get("token")
    if not pessoa_id or not token:
        return False, "Sessão inválida. Faça login novamente."

    try:
        async with httpx.AsyncClient(
            base_url=API_BASE_URL,
            timeout=8.0,
        ) as client:
            response = await client.put(
                f"/api/profissional/{pessoa_id}",
                headers=authorization_headers(token),
                json=data,
            )
    except httpx.RequestError:
        return False, "Não foi possível conectar ao servidor. Verifique se a API está ativa."

    if response.is_success:
        try:
            result = response.json()
        except ValueError:
            return False, "A API retornou uma resposta inválida ao salvar os dados."
        return True, result.get(
            "message",
            "Cadastro profissional atualizado com sucesso.",
        )

    try:
        detail = response.json().get("detail") if response.content else None
    except (ValueError, AttributeError):
        detail = None

    if isinstance(detail, str):
        return False, detail
    return False, "Não foi possível atualizar o cadastro profissional."


async def atualizar(
    request: Request,
    data: dict[str, Any],
) -> tuple[bool, str]:
    id_pessoa = request.session.get("id_pessoa")
    token = request.session.get("token")

    if not id_pessoa or not token:
        return False, "Usuário não identificado. Faça login novamente."

    if data.get("senha") != data.get("confirmar_senha"):
        return False, "As senhas não coincidem."

    try:
        async with httpx.AsyncClient(
            base_url=API_BASE_URL,
            timeout=8.0,
        ) as client:
            response = await client.put(
                f"/api/pessoas/{id_pessoa}",
                headers=authorization_headers(token),
                json=data,
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
    return False, "Não foi possível atualizar o cadastro."


async def atualizar_foto_perfil(
    request: Request,
    foto: UploadFile,
) -> tuple[bool, str]:
    pessoa_id = request.session.get("id_pessoa")
    token = request.session.get("token")
    if pessoa_id is None or not token:
        return False, "Sessão inválida. Faça login novamente."

    try:
        conteudo = await foto.read(5 * 1024 * 1024 + 1)
    except OSError:
        return False, "Não foi possível ler a imagem selecionada."

    if len(conteudo) > 5 * 1024 * 1024:
        return False, "A foto deve ter no máximo 5 MB."
    if not conteudo:
        return False, "Selecione uma foto para enviar."

    try:
        async with httpx.AsyncClient(
            base_url=API_BASE_URL,
            timeout=15.0,
        ) as client:
            response = await client.put(
                f"/api/pessoas/{pessoa_id}/foto-perfil",
                headers=authorization_headers(token),
                files={
                    "foto": (
                        foto.filename or "foto",
                        conteudo,
                        foto.content_type or "application/octet-stream",
                    )
                },
            )
    except httpx.RequestError:
        return False, "Não foi possível conectar à API. Verifique se ela está ativa."

    if response.is_success:
        try:
            result = response.json()
        except ValueError:
            return False, "A API retornou uma resposta inválida ao salvar a foto."
        message = result.get("message") if isinstance(result, dict) else None
        return True, (
            message
            if isinstance(message, str)
            else "Foto de perfil atualizada com sucesso."
        )

    try:
        detail = response.json().get("detail") if response.content else None
    except (ValueError, AttributeError):
        detail = None

    if isinstance(detail, str):
        return False, detail
    return False, "Não foi possível atualizar a foto de perfil."
