from typing import Any

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.modules.profissional import profissionalModel as model
from app.modules.user import userController

PROFISSIONAL_FIELDS = {
    "endereco": 200,
    "numero": 20,
    "cidade": 100,
    "estado": 2,
    "cep": 9,
    "telefone": 20,
    "descricao": None,
    "inscricao_conselho": 50,
    "area_atuacao": 150,
}


def _profissional_data(data: dict[str, Any]) -> dict[str, Any]:
    pessoa_id = data.get("id_pessoa")
    if type(pessoa_id) is not int or pessoa_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="Campo id_pessoa deve ser um inteiro positivo.",
        )

    profissional_data: dict[str, Any] = {"id_pessoa": pessoa_id}

    for field, max_length in PROFISSIONAL_FIELDS.items():
        value = data.get(field)
        if field in {"inscricao_conselho", "area_atuacao"}:
            if value is None or isinstance(value, str) and not value.strip():
                profissional_data[field] = None
                continue

        if not isinstance(value, str) or not value.strip():
            raise HTTPException(
                status_code=400,
                detail=f"Campo {field} obrigatório.",
            )

        value = value.strip()
        if max_length is not None and len(value) > max_length:
            raise HTTPException(
                status_code=400,
                detail=f"Campo {field} deve ter no máximo {max_length} caracteres.",
            )
        profissional_data[field] = value

    profissional_data["estado"] = profissional_data["estado"].upper()
    if len(profissional_data["estado"]) != 2 or not profissional_data["estado"].isalpha():
        raise HTTPException(
            status_code=400,
            detail="Campo estado deve conter a sigla de dois caracteres.",
        )

    if len(profissional_data["cep"]) != 8 or not profissional_data["cep"].isdigit():
        cep = profissional_data["cep"]
        if len(cep) == 9 and cep[5] == "-" and cep[:5].isdigit() and cep[6:].isdigit():
            profissional_data["cep"] = cep[:5] + cep[6:]
        else:
            raise HTTPException(
                status_code=400,
                detail="Campo cep deve conter 8 dígitos, com ou sem hífen.",
            )

    return profissional_data


def post_profissional(data: dict[str, Any]) -> dict[str, Any]:
    profissional_data = _profissional_data(data)
    pessoa_id = profissional_data["id_pessoa"]

    if not model.pessoa_existe(pessoa_id):
        raise HTTPException(status_code=404, detail="Pessoa não encontrada.")

    if model.profissional_existe(pessoa_id):
        raise HTTPException(
            status_code=409,
            detail="Já existe um cadastro profissional associado a esta pessoa.",
        )

    try:
        profissional_id = model.cadastrar_profissional(profissional_data)
    except IntegrityError as error:
        raise HTTPException(
            status_code=409,
            detail="Não foi possível cadastrar: a pessoa já possui cadastro profissional ou não está mais disponível.",
        ) from error

    return {
        "success": True,
        "message": "Profissional cadastrado com sucesso.",
        "id_profissional": profissional_id,
        "status_verificacao": "PENDENTE",
    }


def get_profissional(pessoa_id: int, token: str) -> dict[str, Any]:
    userController.autenticar(pessoa_id, token)
    profissional = model.buscar_profissional(pessoa_id)
    if profissional is None:
        raise HTTPException(
            status_code=404,
            detail="Cadastro profissional não encontrado.",
        )
    return profissional


def get_profissionais(pessoa_id: int, token: str) -> list[dict[str, Any]]:
    userController.autenticar(pessoa_id, token)
    return model.listar_profissionais()


def put_profissional(
    pessoa_id: int,
    data: dict[str, Any],
    token: str,
) -> dict[str, Any]:
    userController.autenticar(pessoa_id, token)
    profissional_data = _profissional_data({**data, "id_pessoa": pessoa_id})

    if not model.pessoa_existe(pessoa_id):
        raise HTTPException(status_code=404, detail="Pessoa não encontrada.")

    try:
        profissional = model.buscar_profissional(pessoa_id)
        if profissional is None:
            profissional_id = model.cadastrar_profissional(profissional_data)
            status_verificacao = "PENDENTE"
            message = "Cadastro profissional realizado com sucesso."
        else:
            if not model.atualizar_profissional(pessoa_id, profissional_data):
                raise HTTPException(
                    status_code=409,
                    detail="Não foi possível atualizar o cadastro profissional.",
                )
            profissional_id = profissional["id_profissional"]
            status_verificacao = profissional["status_verificacao"]
            message = "Cadastro profissional atualizado com sucesso."
    except IntegrityError as error:
        raise HTTPException(
            status_code=409,
            detail="Não foi possível salvar o cadastro profissional.",
        ) from error

    return {
        "success": True,
        "message": message,
        "id_profissional": profissional_id,
        "status_verificacao": status_verificacao,
    }
