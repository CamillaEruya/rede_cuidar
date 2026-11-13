import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import pymysql
from fastapi import HTTPException
from app.modules.user import userController

UPLOAD_ROOT = Path(__file__).resolve().parents[2]


def get_db_connection():
    return pymysql.connect(
        host=os.getenv("DB_HOST", "rede_cuidar_db"),
        user=os.getenv("DB_USERNAME", "root"),
        password=os.getenv("DB_PASSWORD", "123@redeCuidar"),
        database=os.getenv("DB_DATABASE", "rede_cuidar"),
        port=int(os.getenv("DB_PORT", 3306)),
        cursorclass=pymysql.cursors.DictCursor
    )


def _remover_arquivo_midia(midia_url: Optional[str]) -> None:
    if not midia_url or not midia_url.startswith("/uploads/"):
        return
    caminho = UPLOAD_ROOT / midia_url.lstrip("/")
    if caminho.exists() and caminho.is_file():
        try:
            caminho.unlink()
        except OSError:
            pass


def validar_admin(pessoa_id: int, token: str) -> None:
    if not pessoa_id or not token:
        raise HTTPException(status_code=401, detail="Credenciais administrativas ausentes.")

    userController.autenticar(pessoa_id, token)

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id_tipo_perfil, ativo FROM pessoa WHERE id_pessoa = %s",
                (pessoa_id,)
            )
            usuario = cursor.fetchone()
            if not usuario or not usuario.get("ativo") or usuario.get("id_tipo_perfil") != 9:
                raise HTTPException(
                    status_code=403,
                    detail="Acesso negado: apenas administradores podem publicar, editar ou excluir eventos na agenda."
                )
    finally:
        conn.close()


def _formatar_evento(item: Dict[str, Any]) -> Dict[str, Any]:
    meses = ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"]
    dias_semana = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]
    cores_tipo = {
        "comunidade": "agenda-event-teal",
        "palestra": "agenda-event-purple",
        "encontro": "agenda-event-peach",
    }

    dt = item["data_evento"]
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)

    tipo_raw = (item.get("tipo_evento") or "Evento").strip()
    cor = cores_tipo.get(tipo_raw.lower(), "agenda-event-teal")

    return {
        "id_agenda": item["id_agenda"],
        "id_pessoa": item["id_pessoa"],
        "dia": str(dt.day).zfill(2),
        "mes": meses[dt.month - 1],
        "dia_semana": dias_semana[dt.weekday()],
        "horario": dt.strftime("%H:%M"),
        "data_iso": dt.strftime("%Y-%m-%dT%H:%M"),
        "titulo": item["titulo"],
        "descricao": item["descricao"],
        "midia_url": item.get("midia_url"),
        "midia_tipo": item.get("midia_tipo"),
        "profissional": item.get("nome_profissional") or "Equipe Rede Cuidar",
        "area_atuacao": item.get("area_atuacao") or "Geral",
        "local": "On-line",
        "tipo": tipo_raw.capitalize(),
        "status": item["status"],
        "cor": cor,
    }


def listar_agendamentos_disponiveis(incluir_inativos: bool = False) -> List[Dict[str, Any]]:
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            where_clause = "" if incluir_inativos else "WHERE a.status = 'ATIVO'"
            query = f"""
                SELECT 
                    a.id_agenda,
                    a.id_pessoa,
                    p_prof.nome_razao AS nome_profissional,
                    prof.area_atuacao,
                    a.titulo,
                    a.descricao,
                    a.midia_url,
                    a.midia_tipo,
                    a.tipo_evento,
                    a.status,
                    a.data_evento
                FROM agenda a
                LEFT JOIN pessoa p_prof ON a.id_pessoa = p_prof.id_pessoa
                LEFT JOIN profissional prof ON prof.id_pessoa = p_prof.id_pessoa
                {where_clause}
                ORDER BY a.data_evento ASC
            """
            cursor.execute(query)
            resultados = cursor.fetchall()
            return [_formatar_evento(item) for item in resultados]
    finally:
        conn.close()


def criar_evento_agenda(
    pessoa_id: int,
    token: str,
    dados: Dict[str, Any],
    midia_url: Optional[str] = None,
    midia_tipo: Optional[str] = None,
) -> Dict[str, Any]:
    validar_admin(pessoa_id, token)

    titulo = (dados.get("titulo") or "").strip()
    descricao = (dados.get("descricao") or "").strip()
    tipo_evento = (dados.get("tipo_evento") or "Comunidade").strip()
    data_evento = (dados.get("data_evento") or "").strip()

    if not titulo or not descricao or not data_evento:
        raise HTTPException(status_code=400, detail="Título, descrição e data/hora do evento são obrigatórios.")

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO agenda (id_pessoa, titulo, descricao, midia_url, midia_tipo, tipo_evento, status, data_evento)
                VALUES (%s, %s, %s, %s, %s, %s, 'ATIVO', %s)
                """,
                (pessoa_id, titulo, descricao, midia_url, midia_tipo, tipo_evento, data_evento)
            )
            conn.commit()
            novo_id = cursor.lastrowid
        return {"success": True, "id_agenda": novo_id, "message": "Evento publicado na agenda com sucesso."}
    finally:
        conn.close()


def atualizar_evento_agenda(
    id_agenda: int,
    pessoa_id: int,
    token: str,
    dados: Dict[str, Any],
    nova_midia_url: Optional[str] = None,
    nova_midia_tipo: Optional[str] = None,
    remover_midia: bool = False,
) -> Dict[str, Any]:
    validar_admin(pessoa_id, token)

    titulo = (dados.get("titulo") or "").strip()
    descricao = (dados.get("descricao") or "").strip()
    tipo_evento = (dados.get("tipo_evento") or "Comunidade").strip()
    data_evento = (dados.get("data_evento") or "").strip()
    status = (dados.get("status") or "ATIVO").strip().upper()

    if status not in ("ATIVO", "CANCELADO", "CONCLUIDO"):
        raise HTTPException(status_code=400, detail="Status inválido.")

    if not titulo or not descricao or not data_evento:
        raise HTTPException(status_code=400, detail="Título, descrição e data/hora são obrigatórios.")

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT midia_url, midia_tipo FROM agenda WHERE id_agenda = %s", (id_agenda,))
            atual = cursor.fetchone()
            if not atual:
                raise HTTPException(status_code=404, detail="Evento não encontrado.")

            midia_url_final = atual.get("midia_url")
            midia_tipo_final = atual.get("midia_tipo")

            if nova_midia_url:
                _remover_arquivo_midia(midia_url_final)
                midia_url_final = nova_midia_url
                midia_tipo_final = nova_midia_tipo
            elif remover_midia:
                _remover_arquivo_midia(midia_url_final)
                midia_url_final = None
                midia_tipo_final = None

            cursor.execute(
                """
                UPDATE agenda
                SET titulo = %s,
                    descricao = %s,
                    midia_url = %s,
                    midia_tipo = %s,
                    tipo_evento = %s,
                    data_evento = %s,
                    status = %s
                WHERE id_agenda = %s
                """,
                (titulo, descricao, midia_url_final, midia_tipo_final, tipo_evento, data_evento, status, id_agenda)
            )
            conn.commit()
        return {"success": True, "message": "Evento atualizado com sucesso."}
    finally:
        conn.close()


def excluir_evento_agenda(id_agenda: int, pessoa_id: int, token: str) -> Dict[str, Any]:
    validar_admin(pessoa_id, token)

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT midia_url FROM agenda WHERE id_agenda = %s", (id_agenda,))
            evento = cursor.fetchone()
            if not evento:
                raise HTTPException(status_code=404, detail="Evento não encontrado.")

            cursor.execute("DELETE FROM agenda WHERE id_agenda = %s", (id_agenda,))
            conn.commit()
            _remover_arquivo_midia(evento.get("midia_url"))

        return {"success": True, "message": "Publicação excluída da agenda com sucesso."}
    finally:
        conn.close()