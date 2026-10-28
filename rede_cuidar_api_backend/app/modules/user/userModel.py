from sqlalchemy import select, text
from typing import Any
from app.core.tables import get_table, row_to_dict
from app.database import engine


def listar_login(data: dict[str, Any]) -> list[dict[str, Any]]:
    table = get_table('pessoa')
    query = select(
        table.c.id_pessoa,
        table.c.email,
        table.c.senha,
        table.c.chave,
        table.c.nome_razao
    )

    if 'email' in data:
        query = query.where(table.c.email == data.get('email'))

    if 'id_pessoa' in data:
        query = query.where(table.c.id_pessoa == data.get('id_pessoa'))

    with engine.connect() as connection:
        return [row_to_dict(row) for row in connection.execute(query)]

def listar_rate_limits_excedidos(quantidade_acao: int) -> list[dict[str, Any]]:
    query = text("""
        SELECT r.*
        FROM rate_limit AS r
        WHERE r.data >= NOW() - INTERVAL 10 MINUTE
          AND r.email IN (
              SELECT email
              FROM rate_limit
              WHERE data >= NOW() - INTERVAL 10 MINUTE
              GROUP BY email
              HAVING COUNT(*) >= :quantidade_acao
          )
        ORDER BY r.email, r.data DESC
    """)

    with engine.connect() as connection:
        return [
            row_to_dict(row)
            for row in connection.execute(query, {"quantidade_acao": quantidade_acao})
        ]