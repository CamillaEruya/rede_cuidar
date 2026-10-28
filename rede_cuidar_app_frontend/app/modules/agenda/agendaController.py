from typing import Any

from fastapi import Request

from app.modules.user import userController


def agenda_context(request: Request) -> dict[str, Any]:
    nome_razao = request.session.get("nome_razao", "")

    return {
        "request": request,
        "nome_razao": nome_razao,
        "icon_nome_razao": userController.iconAvatar(nome_razao) if nome_razao else "",
        "eventos": [
            {
                "dia": "26",
                "mes": "OUT",
                "dia_semana": "Segunda-feira",
                "horario": "10:00",
                "titulo": "Roda de conversa para famílias",
                "descricao": "Um encontro acolhedor para compartilhar experiências e fortalecer a rede de apoio.",
                "local": "On-line",
                "tipo": "Comunidade",
                "cor": "agenda-event-teal",
            },
            {
                "dia": "28",
                "mes": "OUT",
                "dia_semana": "Quarta-feira",
                "horario": "14:30",
                "titulo": "Desenvolvimento e autonomia no dia a dia",
                "descricao": "Conversa com terapeuta ocupacional sobre estratégias para a rotina.",
                "local": "On-line",
                "tipo": "Palestra",
                "cor": "agenda-event-purple",
            },
            {
                "dia": "31",
                "mes": "OUT",
                "dia_semana": "Sábado",
                "horario": "09:00",
                "titulo": "Manhã de acolhimento e conexão",
                "descricao": "Um espaço para conhecer outras famílias e trocar informações com a comunidade.",
                "local": "Centro Comunitário Rede Cuidar",
                "tipo": "Encontro",
                "cor": "agenda-event-peach",
            },
        ],
    }
