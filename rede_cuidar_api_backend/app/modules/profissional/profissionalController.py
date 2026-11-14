from typing import Any, Optional

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.core.image_upload import remove_stored_media
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

PLANOS_CAMPANHA: dict[str, dict[str, Any]] = {
    "impulso_7": {
        "codigo": "impulso_7",
        "nome": "Impulso Semanal",
        "dias": 7,
        "valor": 29.90,
        "descricao": "Seu perfil no topo da vitrine de profissionais por 7 dias com selo Destaque.",
    },
    "impulso_15": {
        "codigo": "impulso_15",
        "nome": "Destaque Quinzenal",
        "dias": 15,
        "valor": 49.90,
        "descricao": "15 dias sempre à frente nas buscas e prioridade sobre planos semanais.",
    },
    "impulso_30": {
        "codigo": "impulso_30",
        "nome": "Liderança Mensal",
        "dias": 30,
        "valor": 89.90,
        "descricao": "Máxima visibilidade por 30 dias seguidos no topo absoluto da Rede Cuidar.",
    },
}


def _profissional_data(data: dict[str, Any]) -> dict[str, Any]:
    pessoa_id = data.get("id_pessoa")

    if type(pessoa_id) is not int or pessoa_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="Campo id_pessoa deve ser um inteiro positivo.",
        )

    profissional_data: dict[str, Any] = {
        "id_pessoa": pessoa_id
    }

    for field, max_length in PROFISSIONAL_FIELDS.items():
        value = data.get(field)

        if field in {"inscricao_conselho", "area_atuacao"}:
            if value is None or (
                isinstance(value, str) and not value.strip()
            ):
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
                detail=(
                    f"Campo {field} deve ter no máximo "
                    f"{max_length} caracteres."
                ),
            )

        profissional_data[field] = value

    profissional_data["estado"] = (
        profissional_data["estado"].upper()
    )

    if (
        len(profissional_data["estado"]) != 2
        or not profissional_data["estado"].isalpha()
    ):
        raise HTTPException(
            status_code=400,
            detail="Campo estado deve conter a sigla de dois caracteres.",
        )

    cep = profissional_data["cep"]

    if len(cep) != 8 or not cep.isdigit():
        if (
            len(cep) == 9
            and cep[5] == "-"
            and cep[:5].isdigit()
            and cep[6:].isdigit()
        ):
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
        raise HTTPException(
            status_code=404,
            detail="Pessoa não encontrada."
        )

    if model.profissional_existe(pessoa_id):
        raise HTTPException(
            status_code=409,
            detail="Já existe um cadastro profissional associado a esta pessoa."
        )

    try:
        profissional_id = model.cadastrar_profissional(
            profissional_data
        )

    except IntegrityError as error:
        raise HTTPException(
            status_code=409,
            detail=(
                "Não foi possível cadastrar: a pessoa já possui "
                "cadastro profissional ou não está mais disponível."
            )
        ) from error

    return {
        "success": True,
        "message": "Profissional cadastrado com sucesso.",
        "id_profissional": profissional_id,
        "status_verificacao": "PENDENTE",
    }


def get_profissionais(pessoa_id: int, token: str) -> list[dict[str, Any]]:
    userController.autenticar(pessoa_id, token)
    return model.listar_profissionais()


def get_profissional(pessoa_id: int, token: str) -> dict[str, Any]:
    userController.autenticar(pessoa_id, token)
    profissional = model.buscar_profissional(pessoa_id)

    if profissional is None:
        raise HTTPException(
            status_code=404,
            detail="Cadastro profissional não encontrado.",
        )

    return profissional


def put_profissional(
    pessoa_id: int,
    data: dict[str, Any],
    token: str,
) -> dict[str, Any]:
    userController.autenticar(pessoa_id, token)

    if not model.pessoa_existe(pessoa_id):
        raise HTTPException(
            status_code=404,
            detail="Pessoa não encontrada.",
        )

    profissional_data = _profissional_data(
        {**data, "id_pessoa": pessoa_id}
    )

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


def validar_profissional_aprovado(pessoa_id: int, token: str) -> dict[str, Any]:
    userController.autenticar(pessoa_id, token)
    profissional = model.buscar_profissional(pessoa_id)
    if profissional is None:
        raise HTTPException(
            status_code=404,
            detail="Cadastro profissional não encontrado. Complete seus dados profissionais no Perfil.",
        )
    if profissional.get("status_verificacao") != "APROVADO":
        raise HTTPException(
            status_code=403,
            detail="Seu perfil profissional está aguardando aprovação do administrador. Enquanto isso, o painel permanece estático.",
        )
    return profissional


def get_painel_profissional(pessoa_id: int, token: str) -> dict[str, Any]:
    userController.autenticar(pessoa_id, token)
    profissional = model.buscar_profissional(pessoa_id)

    if profissional is None:
        return {
            "cadastrado": False,
            "aprovado": False,
            "status_verificacao": "NAO_CADASTRADO",
            "profissional": None,
            "divulgacoes": [],
            "campanhas": [],
            "campanha_ativa": None,
            "planos": list(PLANOS_CAMPANHA.values()),
        }

    id_profissional = profissional["id_profissional"]
    aprovado = profissional.get("status_verificacao") == "APROVADO"
    divulgacoes = model.listar_divulgacoes_profissional(id_profissional)
    campanhas = model.listar_campanhas_profissional(id_profissional)
    campanha_ativa = next((c for c in campanhas if c.get("status") == "ATIVA"), None)

    return {
        "cadastrado": True,
        "aprovado": aprovado,
        "status_verificacao": profissional.get("status_verificacao", "PENDENTE"),
        "profissional": profissional,
        "divulgacoes": divulgacoes,
        "campanhas": campanhas,
        "campanha_ativa": campanha_ativa,
        "planos": list(PLANOS_CAMPANHA.values()),
    }


def criar_divulgacao(
    pessoa_id: int,
    token: str,
    titulo: str,
    descricao: str,
    midia_url: Optional[str] = None,
    midia_tipo: Optional[str] = None,
) -> dict[str, Any]:
    profissional = validar_profissional_aprovado(pessoa_id, token)

    titulo_limpo = (titulo or "").strip()
    descricao_limpa = (descricao or "").strip()

    if not titulo_limpo or len(titulo_limpo) > 150:
        raise HTTPException(
            status_code=400,
            detail="Informe um título válido (até 150 caracteres).",
        )
    if not descricao_limpa:
        raise HTTPException(
            status_code=400,
            detail="A descrição do trabalho/serviço é obrigatória.",
        )

    id_divulgacao = model.criar_divulgacao_profissional(
        id_profissional=profissional["id_profissional"],
        titulo=titulo_limpo,
        descricao=descricao_limpa,
        midia_url=midia_url,
        midia_tipo=midia_tipo,
    )
    return {
        "success": True,
        "message": "Trabalho publicado no seu portfólio com sucesso!",
        "id_divulgacao": id_divulgacao,
    }


def excluir_divulgacao(
    pessoa_id: int,
    token: str,
    id_divulgacao: int,
) -> dict[str, Any]:
    profissional = validar_profissional_aprovado(pessoa_id, token)
    id_profissional = profissional["id_profissional"]

    item = model.buscar_divulgacao(id_divulgacao, id_profissional)
    if item is None:
        raise HTTPException(
            status_code=404,
            detail="Publicação não encontrada no seu portfólio.",
        )

    midia_url = item.get("midia_url")
    ok = model.excluir_divulgacao_profissional(id_divulgacao, id_profissional)
    if not ok:
        raise HTTPException(status_code=400, detail="Não foi possível excluir a publicação.")

    if midia_url:
        remove_stored_media(midia_url)

    return {
        "success": True,
        "message": "Divulgação removida com sucesso.",
    }


def contratar_campanha(
    pessoa_id: int,
    token: str,
    plano_codigo: str,
) -> dict[str, Any]:
    profissional = validar_profissional_aprovado(pessoa_id, token)
    plano = PLANOS_CAMPANHA.get((plano_codigo or "").strip())

    if plano is None:
        raise HTTPException(
            status_code=400,
            detail="Plano de campanha inválido.",
        )

    id_campanha = model.criar_campanha_profissional(
        id_profissional=profissional["id_profissional"],
        plano_nome=plano["nome"],
        dias=plano["dias"],
        valor=plano["valor"],
    )
    return {
        "success": True,
        "message": f"Campanha '{plano['nome']}' ({plano['dias']} dias) ativada! Seu perfil já está em destaque no topo.",
        "id_campanha": id_campanha,
    }