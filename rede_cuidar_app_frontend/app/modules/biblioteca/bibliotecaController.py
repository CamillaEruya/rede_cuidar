from typing import Any

from fastapi import Request

from app.modules.user import userController


def biblioteca_context(request: Request) -> dict[str, Any]:
    nome_razao = request.session.get("nome_razao", "")

    return {
        "request": request,
        "nome_razao": nome_razao,
        "icon_nome_razao": userController.iconAvatar(nome_razao) if nome_razao else "",
        "noticias": [
            {
                "categoria": "Comunidade",
                "data": "23 de outubro de 2026",
                "titulo": "Acolhimento também se constrói em rede",
                "resumo": "Conheça iniciativas e espaços de troca que aproximam famílias e fortalecem vínculos.",
                "cor": "library-news-teal",
                "icone": "♡",
            },
            {
                "categoria": "Informação",
                "data": "20 de outubro de 2026",
                "titulo": "Pequenas estratégias para uma rotina mais previsível",
                "resumo": "Ideias simples para organizar atividades e conversar sobre mudanças no dia a dia.",
                "cor": "library-news-purple",
                "icone": "✦",
            },
            {
                "categoria": "Rede Cuidar",
                "data": "16 de outubro de 2026",
                "titulo": "Novos encontros chegando à comunidade",
                "resumo": "Acompanhe a agenda para encontrar rodas de conversa, palestras e momentos de conexão.",
                "cor": "library-news-peach",
                "icone": "☆",
            },
        ],
    }
