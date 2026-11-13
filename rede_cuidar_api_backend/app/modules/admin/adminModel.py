from typing import Any

from sqlalchemy import inspect, literal, select, update

from app.core.tables import get_table, row_to_dict
from app.database import engine


def eh_administrador(pessoa_id: int) -> bool:
    pessoa = get_table("pessoa")
    query = select(pessoa.c.id_tipo_perfil, pessoa.c.ativo).where(
        pessoa.c.id_pessoa == pessoa_id
    )
    with engine.connect() as connection:
        row = connection.execute(query).first()
        if row is None:
            return False
        data = row_to_dict(row)
        return data.get("id_tipo_perfil") == 9 and data.get("ativo") == 1


def listar_usuarios() -> list[dict[str, Any]]:
    pessoa = get_table("pessoa")
    tipo_perfil = get_table("tipo_perfil")

    query = (
        select(
            pessoa.c.id_pessoa,
            pessoa.c.nome_razao,
            pessoa.c.email,
            pessoa.c.cpf_cnpj,
            pessoa.c.id_tipo_perfil,
            tipo_perfil.c.nome.label("nome_perfil"),
            pessoa.c.ativo,
        )
        .select_from(
            pessoa.outerjoin(
                tipo_perfil,
                pessoa.c.id_tipo_perfil == tipo_perfil.c.id_tipo_perfil,
            )
        )
        .order_by(pessoa.c.id_pessoa.desc())
    )

    with engine.connect() as connection:
        return [row_to_dict(row) for row in connection.execute(query)]


def atualizar_usuario(pessoa_id: int, data: dict[str, Any]) -> bool:
    pessoa = get_table("pessoa")
    campos_permitidos = {
        k: v for k, v in data.items() if k in {"id_tipo_perfil", "ativo"}
    }
    if not campos_permitidos:
        return False

    with engine.begin() as connection:
        result = connection.execute(
            update(pessoa)
            .where(pessoa.c.id_pessoa == pessoa_id)
            .values(**campos_permitidos)
        )
        return result.rowcount > 0


def listar_profissionais_admin() -> list[dict[str, Any]]:
    profissional = get_table("profissional")
    pessoa = get_table("pessoa")

    colunas = [
        profissional.c.id_profissional,
        profissional.c.id_pessoa,
        pessoa.c.nome_razao,
        pessoa.c.email,
        profissional.c.cidade,
        profissional.c.estado,
        profissional.c.telefone,
        profissional.c.descricao,
        profissional.c.inscricao_conselho,
        profissional.c.status_verificacao,
    ]
    if "area_atuacao" in profissional.c:
        colunas.append(profissional.c.area_atuacao)

    query = (
        select(*colunas)
        .select_from(
            profissional.join(
                pessoa,
                profissional.c.id_pessoa == pessoa.c.id_pessoa,
            )
        )
        .order_by(profissional.c.id_profissional.desc())
    )

    with engine.connect() as connection:
        return [row_to_dict(row) for row in connection.execute(query)]


def atualizar_status_profissional(pessoa_id: int, status_verificacao: str) -> bool:
    profissional = get_table("profissional")
    with engine.begin() as connection:
        result = connection.execute(
            update(profissional)
            .where(profissional.c.id_pessoa == pessoa_id)
            .values(status_verificacao=status_verificacao)
        )
        return result.rowcount > 0


def listar_agendas_admin() -> list[dict[str, Any]]:
    agenda = get_table("agenda")
    pessoa = get_table("pessoa")

    query = (
        select(
            agenda.c.id_agenda,
            agenda.c.id_pessoa,
            pessoa.c.nome_razao.label("nome_profissional"),
            literal(None).label("id_cliente"),
            literal(None).label("nome_cliente"),
            agenda.c.titulo,
            agenda.c.descricao,
            agenda.c.tipo_evento,
            agenda.c.status,
            agenda.c.data_evento,
        )
        .select_from(
            agenda.join(pessoa, agenda.c.id_pessoa == pessoa.c.id_pessoa)
        )
        .order_by(agenda.c.data_evento.desc(), agenda.c.id_agenda.desc())
    )

    with engine.connect() as connection:
        return [row_to_dict(row) for row in connection.execute(query)]


def atualizar_status_agenda(agenda_id: int, status: str) -> bool:
    agenda = get_table("agenda")
    with engine.begin() as connection:
        result = connection.execute(
            update(agenda)
            .where(agenda.c.id_agenda == agenda_id)
            .values(status=status)
        )
        return result.rowcount > 0


def listar_publicacoes_admin() -> list[dict[str, Any]]:
    if not inspect(engine).has_table("publicacao"):
        return []

    publicacao = get_table("publicacao")
    pessoa = get_table("pessoa")

    query = (
        select(
            publicacao.c.id_publicacao,
            publicacao.c.id_pessoa,
            pessoa.c.nome_razao,
            publicacao.c.descricao,
            publicacao.c.foto,
            publicacao.c.data_publicacao,
            publicacao.c.ativo,
        )
        .select_from(
            publicacao.join(
                pessoa,
                publicacao.c.id_pessoa == pessoa.c.id_pessoa,
            )
        )
        .order_by(publicacao.c.id_publicacao.desc())
    )

    with engine.connect() as connection:
        return [row_to_dict(row) for row in connection.execute(query)]


def moderar_publicacao(publicacao_id: int, ativo: int) -> bool:
    if not inspect(engine).has_table("publicacao"):
        return False

    publicacao = get_table("publicacao")
    with engine.begin() as connection:
        result = connection.execute(
            update(publicacao)
            .where(publicacao.c.id_publicacao == publicacao_id)
            .values(ativo=ativo)
        )
        return result.rowcount > 0