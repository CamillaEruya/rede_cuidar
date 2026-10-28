from typing import Any

from fastapi import Request

from app.modules.user import userController


def profissionais_context(request: Request) -> dict[str, Any]:
    nome_razao = request.session.get("nome_razao", "")

    return {
        "request": request,
        "nome_razao": nome_razao,
        "icon_nome_razao": userController.iconAvatar(nome_razao) if nome_razao else "",
        "profissionais": [
            {
                "nome": "Rafael Fernandes",
                "iniciais": "RF",
                "especialidade": "Terapia ocupacional",
                "descricao": "Apoio ao desenvolvimento da autonomia e às atividades do dia a dia.",
                "localidade": "Atendimento presencial e on-line",
                "categoria": "Desenvolvimento",
                "avatar": "avatar-mint",
            },
            {
                "nome": "Dra. Ana Martins",
                "iniciais": "AM",
                "especialidade": "Psicologia",
                "descricao": "Acolhimento para famílias, cuidadores e pessoas neurodivergentes.",
                "localidade": "Atendimento on-line",
                "categoria": "Saúde emocional",
                "avatar": "avatar-lilac",
            },
            {
                "nome": "Joana Lima",
                "iniciais": "JL",
                "especialidade": "Fonoaudiologia",
                "descricao": "Orientação em comunicação, linguagem e desenvolvimento infantil.",
                "localidade": "Atendimento presencial e on-line",
                "categoria": "Comunicação",
                "avatar": "avatar-blue",
            },
        ],
    }
