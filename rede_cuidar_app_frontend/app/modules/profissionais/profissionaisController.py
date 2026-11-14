import httpx
from typing import Any

from fastapi import Request

from app.modules.user.userController import API_BASE_URL, authorization_headers
from app.modules.user import userController


async def profissionais_context(request: Request) -> dict[str, Any]:
    nome_razao = request.session.get("nome_razao", "")
    pessoa_id = request.session.get("id_pessoa")
    token = request.session.get("token")
    profissionais: list[dict[str, Any]] = []
    profissionais_error = None
    categorias_por_chave: dict[str, str] = {}

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
            area_atuacao = profissional.get("area_atuacao")
            categoria = (
                area_atuacao.strip()
                if isinstance(area_atuacao, str) and area_atuacao.strip()
                else "Outros"
            )
            categorias_por_chave.setdefault(categoria.casefold(), categoria)
            profissionais.append(
                {
                    "nome": nome,
                    "iniciais": iniciais or "PR",
                    "categoria": categoria,
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
        "icon_nome_razao": userController.iconAvatar(nome_razao) if nome_razao else "",
        "profissionais": profissionais,
        "categorias": sorted(categorias_por_chave.values(), key=str.casefold),
        "profissionais_error": profissionais_error,
    }
