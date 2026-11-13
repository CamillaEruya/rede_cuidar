
from typing import Any

from sqlalchemy import insert, select, update

from app.core.tables import get_table, row_to_dict
from app.database import engine


def listar_publicacoes() -> list[dict[str, Any]]:
    publicacao = get_table("publicacao")
    pessoa = get_table("pessoa")

    query = (
        select(
            publicacao.c.id_publicacao,
            publicacao.c.id_pessoa,
            pessoa.c.nome_razao,
            pessoa.c.foto_perfil,
            publicacao.c.descricao,
            publicacao.c.foto,
            publicacao.c.data_publicacao,
        )
        .select_from(
            publicacao.join(
                pessoa,
                publicacao.c.id_pessoa == pessoa.c.id_pessoa,
            )
        )
        .where(
            publicacao.c.ativo == 1,
            pessoa.c.ativo == 1,
        )
        .order_by(publicacao.c.data_publicacao.desc(),
                  publicacao.c.id_publicacao.desc())
    )

    with engine.connect() as connection:
        return [
            row_to_dict(row)
            for row in connection.execute(query)
        ]


def buscar_publicacao(
    publicacao_id: int,
) -> dict[str, Any] | None:
    table = get_table("publicacao")

    query = select(table).where(
        table.c.id_publicacao == publicacao_id,
        table.c.ativo == 1,
    )

    with engine.connect() as connection:
        row = connection.execute(query).first()
        return row_to_dict(row) if row is not None else None


def cadastrar_publicacao(data: dict[str, Any]) -> int:
    table = get_table("publicacao")

    with engine.begin() as connection:
        result = connection.execute(
            insert(table).values(**data)
        )
        return int(result.inserted_primary_key[0])


def atualizar_publicacao(
    publicacao_id: int,
    pessoa_id: int,
    data: dict[str, Any],
) -> bool:
    table = get_table("publicacao")

    publicacao_data = {
        key: value
        for key, value in data.items()
        if key in {"descricao", "foto"}
    }

    if not publicacao_data:
        return False

    with engine.begin() as connection:
        result = connection.execute(
            update(table)
            .where(
                table.c.id_publicacao == publicacao_id,
                table.c.id_pessoa == pessoa_id,
                table.c.ativo == 1,
            )
            .values(**publicacao_data)
        )
        return result.rowcount > 0


def deletar_publicacao(
    publicacao_id: int,
    pessoa_id: int,
) -> bool:
    table = get_table("publicacao")

    with engine.begin() as connection:
        result = connection.execute(
            update(table)
            .where(
                table.c.id_publicacao == publicacao_id,
                table.c.id_pessoa == pessoa_id,
                table.c.ativo == 1,
            )
            .values(ativo=0)
        )
        return result.rowcount > 0
