from typing import Any

from sqlalchemy import insert, select, update

from app.core.tables import get_table, row_to_dict
from app.database import engine


def listar_profissionais() -> list[dict[str, Any]]:
    profissional = get_table("profissional")
    pessoa = get_table("pessoa")
    query = (
        select(
            profissional.c.id_profissional,
            pessoa.c.nome_razao,
            profissional.c.cidade,
            profissional.c.estado,
            profissional.c.descricao,
            profissional.c.inscricao_conselho,
            profissional.c.area_atuacao,
        )
        .select_from(
            profissional.join(
                pessoa,
                profissional.c.id_pessoa == pessoa.c.id_pessoa,
            )
        )
        .where(pessoa.c.ativo == 1)
        .order_by(pessoa.c.nome_razao)
    )

    with engine.connect() as connection:
        return [row_to_dict(row) for row in connection.execute(query)]


def buscar_profissional(pessoa_id: int) -> dict[str, Any] | None:
    table = get_table("profissional")
    query = select(table).where(table.c.id_pessoa == pessoa_id)

    with engine.connect() as connection:
        row = connection.execute(query).first()
        return row_to_dict(row) if row is not None else None


def pessoa_existe(pessoa_id: int) -> bool:
    table = get_table("pessoa")
    query = select(table.c.id_pessoa).where(table.c.id_pessoa == pessoa_id)

    with engine.connect() as connection:
        return connection.execute(query).first() is not None


def profissional_existe(pessoa_id: int) -> bool:
    table = get_table("profissional")
    query = select(table.c.id_profissional).where(table.c.id_pessoa == pessoa_id)

    with engine.connect() as connection:
        return connection.execute(query).first() is not None


def cadastrar_profissional(data: dict[str, Any]) -> int:
    table = get_table("profissional")
    with engine.begin() as connection:
        result = connection.execute(insert(table).values(**data))
        return int(result.inserted_primary_key[0])


def atualizar_profissional(pessoa_id: int, data: dict[str, Any]) -> bool:
    table = get_table("profissional")
    profissional_data = {
        key: value for key, value in data.items() if key != "id_pessoa"
    }

    with engine.begin() as connection:
        result = connection.execute(
            update(table)
            .where(table.c.id_pessoa == pessoa_id)
            .values(**profissional_data)
        )
        if result.rowcount > 0:
            return True
        query = select(table.c.id_profissional).where(table.c.id_pessoa == pessoa_id)
        return connection.execute(query).first() is not None
