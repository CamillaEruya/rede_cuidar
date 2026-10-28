from typing import Any
from sqlalchemy import delete, insert, select, update, text
from app.core.tables import get_table, row_to_dict
from app.database import engine

def listar_pessoas(pessoa_id: int | None = None) -> list[dict[str, Any]]:
    table = get_table("pessoa")
    query = select(
        table.c.id_pessoa, 
        table.c.id_tipo_pessoa, 
        table.c.id_tipo_perfil,
        table.c.nome_razao, 
        table.c.email, 
        table.c.cpf_cnpj, 
        table.c.ativo
    ).order_by(table.c.id_pessoa)
    if pessoa_id is not None:
        query = query.where(table.c.id_pessoa == pessoa_id)

    with engine.connect() as connection:
        return [row_to_dict(row) for row in connection.execute(query)]


def listar_tipos_perfil(tipos_perfil_id: int | None = None) -> list[dict[str, Any]]:
    table = get_table("tipo_perfil")
    query = select(table).order_by(table.c.id_tipo_perfil)
    if tipos_perfil_id is not None:
        query = query.where(table.c.id_tipo_perfil == tipos_perfil_id)

    with engine.connect() as connection:
        return [row_to_dict(row) for row in connection.execute(query)]


def cadastrar_pessoa(data: dict[str, Any]) -> int:
    table = get_table("pessoa")
    with engine.begin() as connection:
        result = connection.execute(insert(table).values(**data))
        return int(result.inserted_primary_key[0])



def atualizar_pessoa(pessoa_id: int, data: dict[str, Any]) -> bool:
    table = get_table("pessoa")
    with engine.begin() as connection:
        result = connection.execute(
            update(table).where(table.c.id_pessoa == pessoa_id).values(**data)
        )
        return result.rowcount > 0


def deletar_pessoa(pessoa_id: int) -> bool:
    table = get_table("pessoa")
    with engine.begin() as connection:
        result = connection.execute(
            delete(table).where(table.c.id_pessoa == pessoa_id)
        )
        return result.rowcount > 0

def cadastrar_rate_limit(tipo: str, data: str, email: str) -> int:
    table = get_table("rate_limit")
    with engine.begin() as connection:
        result = connection.execute(insert(table).values(tipo=tipo, data=data, email=email))
        return int(result.inserted_primary_key[0])
    
def verifica_cpf_cnpj(cpf_cnpj: str) -> bool:
    table = get_table("pessoa")
    query = (
        select(table.c.id_pessoa)
        .where(table.c.cpf_cnpj == cpf_cnpj)
        .limit(1)
    )

    with engine.connect() as connection:
        return connection.execute(query).first() is not None