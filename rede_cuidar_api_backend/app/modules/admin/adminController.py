from typing import Any

from fastapi import HTTPException

from app.modules.admin import adminModel as model
from app.modules.user import userController


def verificar_admin(pessoa_id: int, token: str) -> None:
    userController.autenticar(pessoa_id, token)
    if not model.eh_administrador(pessoa_id):
        raise HTTPException(
            status_code=403,
            detail="Acesso negado. Apenas administradores podem realizar esta ação.",
        )


def get_usuarios(admin_id: int, token: str) -> list[dict[str, Any]]:
    verificar_admin(admin_id, token)
    return model.listar_usuarios()


def put_usuario(
    admin_id: int,
    target_pessoa_id: int,
    data: dict[str, Any],
    token: str,
) -> dict[str, Any]:
    verificar_admin(admin_id, token)

    payload: dict[str, Any] = {}
    if "id_tipo_perfil" in data and data["id_tipo_perfil"] is not None:
        id_tipo_perfil = int(data["id_tipo_perfil"])
        if id_tipo_perfil < 1 or id_tipo_perfil > 9:
            raise HTTPException(status_code=400, detail="Tipo de perfil inválido.")
        if target_pessoa_id == admin_id and id_tipo_perfil != 9:
            raise HTTPException(
                status_code=400,
                detail="Você não pode remover seu próprio perfil de administrador.",
            )
        payload["id_tipo_perfil"] = id_tipo_perfil

    if "ativo" in data and data["ativo"] is not None:
        ativo = 1 if bool(data["ativo"]) else 0
        if target_pessoa_id == admin_id and ativo == 0:
            raise HTTPException(
                status_code=400,
                detail="Você não pode desativar sua própria conta de administrador.",
            )
        payload["ativo"] = ativo

    if not payload:
        raise HTTPException(status_code=400, detail="Nenhum campo válido informado.")

    if not model.atualizar_usuario(target_pessoa_id, payload):
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    return {"success": True, "message": "Usuário atualizado com sucesso."}


def get_profissionais(admin_id: int, token: str) -> list[dict[str, Any]]:
    verificar_admin(admin_id, token)
    return model.listar_profissionais_admin()


def put_status_profissional(
    admin_id: int,
    target_pessoa_id: int,
    data: dict[str, Any],
    token: str,
) -> dict[str, Any]:
    verificar_admin(admin_id, token)

    status = str(data.get("status_verificacao", "")).strip().upper()
    if status not in {"PENDENTE", "APROVADO", "REJEITADO"}:
        raise HTTPException(
            status_code=400,
            detail="Status inválido. Use PENDENTE, APROVADO ou REJEITADO.",
        )

    if not model.atualizar_status_profissional(target_pessoa_id, status):
        raise HTTPException(
            status_code=404,
            detail="Cadastro profissional não encontrado.",
        )

    return {
        "success": True,
        "message": f"Status profissional atualizado para {status}.",
    }


def get_agendas(admin_id: int, token: str) -> list[dict[str, Any]]:
    verificar_admin(admin_id, token)
    return model.listar_agendas_admin()


def put_status_agenda(
    admin_id: int,
    agenda_id: int,
    data: dict[str, Any],
    token: str,
) -> dict[str, Any]:
    verificar_admin(admin_id, token)

    status = str(data.get("status", "")).strip().upper()
    if status not in {"ATIVO", "AGENDADO", "CANCELADO", "CONCLUIDO"}:
        raise HTTPException(
            status_code=400,
            detail="Status de agenda inválido.",
        )

    if not model.atualizar_status_agenda(agenda_id, status):
        raise HTTPException(status_code=404, detail="Agendamento não encontrado.")

    return {
        "success": True,
        "message": f"Status do agendamento atualizado para {status}.",
    }


def get_publicacoes(admin_id: int, token: str) -> list[dict[str, Any]]:
    verificar_admin(admin_id, token)
    return model.listar_publicacoes_admin()


def put_status_publicacao(
    admin_id: int,
    publicacao_id: int,
    data: dict[str, Any],
    token: str,
) -> dict[str, Any]:
    verificar_admin(admin_id, token)

    ativo = 1 if bool(data.get("ativo", False)) else 0
    if not model.moderar_publicacao(publicacao_id, ativo):
        raise HTTPException(status_code=404, detail="Publicação não encontrada.")

    acao = "reativada" if ativo == 1 else "oculta/removida"
    return {"success": True, "message": f"Publicação {acao} com sucesso."}
