from datetime import datetime, timedelta
from typing import Any, Optional

from sqlalchemy import delete, insert, select, update

from app.core.tables import get_table, row_to_dict
from app.database import engine


def _expirar_campanhas_vencidas(connection) -> None:
    campanha = get_table("campanha_profissional")
    agora = datetime.now()
    connection.execute(
        update(campanha)
        .where(campanha.c.status == "ATIVA", campanha.c.data_fim <= agora)
        .values(status="EXPIRADA")
    )


def listar_profissionais() -> list[dict[str, Any]]:
    profissional = get_table("profissional")
    pessoa = get_table("pessoa")
    campanha = get_table("campanha_profissional")
    divulgacao = get_table("profissional_divulgacao")

    agora = datetime.now()

    with engine.begin() as connection:
        _expirar_campanhas_vencidas(connection)

        query = (
            select(
                profissional.c.id_profissional,
                profissional.c.id_pessoa,
                pessoa.c.nome_razao,
                profissional.c.cidade,
                profissional.c.estado,
                profissional.c.telefone,
                profissional.c.descricao,
                profissional.c.inscricao_conselho,
                profissional.c.area_atuacao,
                profissional.c.status_verificacao,
            )
            .select_from(
                profissional.join(
                    pessoa,
                    profissional.c.id_pessoa == pessoa.c.id_pessoa,
                )
            )
            .where(
                pessoa.c.ativo == 1,
                profissional.c.status_verificacao == "APROVADO",
            )
            .order_by(pessoa.c.nome_razao)
        )
        lista_prof = [row_to_dict(row) for row in connection.execute(query)]

        if not lista_prof:
            return []

        ids_prof = [p["id_profissional"] for p in lista_prof]

        # Busca campanhas ativas vigentes
        camp_query = (
            select(campanha)
            .where(
                campanha.c.id_profissional.in_(ids_prof),
                campanha.c.status == "ATIVA",
                campanha.c.data_fim > agora,
            )
            .order_by(campanha.c.valor.desc(), campanha.c.data_fim.desc())
        )
        campanhas_ativas: dict[int, dict[str, Any]] = {}
        for row in connection.execute(camp_query):
            c = row_to_dict(row)
            pid = c["id_profissional"]
            if pid not in campanhas_ativas:
                campanhas_ativas[pid] = c

        # Busca divulgações/trabalhos publicados pelos profissionais aprovados
        div_query = (
            select(divulgacao)
            .where(divulgacao.c.id_profissional.in_(ids_prof))
            .order_by(divulgacao.c.id_divulgacao.desc())
        )
        divulgacoes_por_prof: dict[int, list[dict[str, Any]]] = {}
        for row in connection.execute(div_query):
            d = row_to_dict(row)
            if isinstance(d.get("data_criacao"), datetime):
                d["data_criacao"] = d["data_criacao"].strftime("%d/%m/%Y")
            divulgacoes_por_prof.setdefault(d["id_profissional"], []).append(d)

        for p in lista_prof:
            pid = p["id_profissional"]
            camp = campanhas_ativas.get(pid)
            p["destaque"] = camp is not None
            p["campanha_plano"] = camp["plano_nome"] if camp else None
            p["campanha_valor"] = float(camp["valor"]) if camp else 0.0
            p["divulgacoes"] = divulgacoes_por_prof.get(pid, [])

        # Ordena: profissionais com campanha ativa sempre na frente (maior investimento primeiro), depois ordem alfabética
        lista_prof.sort(
            key=lambda item: (
                0 if item["destaque"] else 1,
                -item["campanha_valor"],
                (item.get("nome_razao") or "").lower(),
            )
        )
        return lista_prof


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


# --- DIVULGAÇÕES DE TRABALHO / PORTFÓLIO ---

def listar_divulgacoes_profissional(id_profissional: int) -> list[dict[str, Any]]:
    divulgacao = get_table("profissional_divulgacao")
    query = (
        select(divulgacao)
        .where(divulgacao.c.id_profissional == id_profissional)
        .order_by(divulgacao.c.id_divulgacao.desc())
    )
    with engine.connect() as connection:
        itens = []
        for row in connection.execute(query):
            d = row_to_dict(row)
            if isinstance(d.get("data_criacao"), datetime):
                d["data_criacao"] = d["data_criacao"].strftime("%d/%m/%Y %H:%M")
            itens.append(d)
        return itens


def criar_divulgacao_profissional(
    id_profissional: int,
    titulo: str,
    descricao: str,
    midia_url: Optional[str] = None,
    midia_tipo: Optional[str] = None,
) -> int:
    divulgacao = get_table("profissional_divulgacao")
    with engine.begin() as connection:
        result = connection.execute(
            insert(divulgacao).values(
                id_profissional=id_profissional,
                titulo=titulo,
                descricao=descricao,
                midia_url=midia_url,
                midia_tipo=midia_tipo,
            )
        )
        return int(result.inserted_primary_key[0])


def buscar_divulgacao(id_divulgacao: int, id_profissional: int) -> dict[str, Any] | None:
    divulgacao = get_table("profissional_divulgacao")
    query = select(divulgacao).where(
        divulgacao.c.id_divulgacao == id_divulgacao,
        divulgacao.c.id_profissional == id_profissional,
    )
    with engine.connect() as connection:
        row = connection.execute(query).first()
        return row_to_dict(row) if row is not None else None


def excluir_divulgacao_profissional(id_divulgacao: int, id_profissional: int) -> bool:
    divulgacao = get_table("profissional_divulgacao")
    with engine.begin() as connection:
        result = connection.execute(
            delete(divulgacao).where(
                divulgacao.c.id_divulgacao == id_divulgacao,
                divulgacao.c.id_profissional == id_profissional,
            )
        )
        return result.rowcount > 0


# --- CAMPANHAS DE MARKETING ---

def listar_campanhas_profissional(id_profissional: int) -> list[dict[str, Any]]:
    campanha = get_table("campanha_profissional")
    with engine.begin() as connection:
        _expirar_campanhas_vencidas(connection)
        query = (
            select(campanha)
            .where(campanha.c.id_profissional == id_profissional)
            .order_by(campanha.c.id_campanha.desc())
        )
        itens = []
        for row in connection.execute(query):
            c = row_to_dict(row)
            c["valor"] = float(c["valor"])
            if isinstance(c.get("data_inicio"), datetime):
                c["data_inicio_fmt"] = c["data_inicio"].strftime("%d/%m/%Y %H:%M")
            if isinstance(c.get("data_fim"), datetime):
                c["data_fim_fmt"] = c["data_fim"].strftime("%d/%m/%Y %H:%M")
            itens.append(c)
        return itens


def criar_campanha_profissional(
    id_profissional: int,
    plano_nome: str,
    dias: int,
    valor: float,
) -> int:
    campanha = get_table("campanha_profissional")
    agora = datetime.now()
    data_fim = agora + timedelta(days=dias)

    with engine.begin() as connection:
        _expirar_campanhas_vencidas(connection)
        # Substitui eventual campanha ativa anterior para não duplicar cobrança simultânea
        connection.execute(
            update(campanha)
            .where(
                campanha.c.id_profissional == id_profissional,
                campanha.c.status == "ATIVA",
            )
            .values(status="EXPIRADA")
        )
        result = connection.execute(
            insert(campanha).values(
                id_profissional=id_profissional,
                plano_nome=plano_nome,
                dias=dias,
                valor=valor,
                status="ATIVA",
                data_inicio=agora,
                data_fim=data_fim,
            )
        )
        return int(result.inserted_primary_key[0])