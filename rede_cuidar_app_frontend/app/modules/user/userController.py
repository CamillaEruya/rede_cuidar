import os

import httpx
from dotenv import load_dotenv
from fastapi import Request

load_dotenv()
API_BASE_URL = os.getenv("API_BASE_URL", "").rstrip("/")
FILE_BASE_URL = os.getenv("FILE_BASE_URL", "").rstrip("/")
BEARER_SCHEME = "Bearer"


def authorization_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"{BEARER_SCHEME} {token}"}


def iconAvatar(nome_razao: str) -> str:
    arr_nome_razao = nome_razao.split()
    if len(arr_nome_razao) >= 2:
        icon = "".join(arr[0] for arr in arr_nome_razao[:2])
        return icon.upper()
    return nome_razao[:2].upper()


async def autenticar(request: Request) -> tuple[bool, str]:
    pessoa_id = request.session.get("id_pessoa")
    token = request.session.get("token")

    if pessoa_id is None or not token:
        return False, "Sessão inválida ou expirada. Faça login novamente."

    try:
        async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=8.0) as client:
            response = await client.post(
                "/api/user/autenticacao",
                headers={
                    "x-user-id": str(pessoa_id),
                    **authorization_headers(token),
                },
            )
    except httpx.RequestError:
        return False, "Não foi possível conectar ao servidor. Verifique se a API está ativa."

    if response.is_success:
        return True, "autenticado com sucesso."

    detail = response.json().get("detail") if response.content else None
    if isinstance(detail, str):
        return False, detail
    return False, "Não foi possível autenticar usuario."
