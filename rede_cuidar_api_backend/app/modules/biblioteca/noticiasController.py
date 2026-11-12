import re
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
import unicodedata
from urllib.parse import urlencode, urlsplit
from xml.etree import ElementTree

import httpx
from fastapi import HTTPException

from app.modules.biblioteca.bibliotecaModel import NewsArticle


GOOGLE_NEWS_RSS_URL = "https://news.google.com/rss/search"
TRUSTED_DOMAINS = (
    "gov.br",
    "fiocruz.br",
    "ebc.com.br",
    "unicef.org",
    "who.int",
    "g1.globo.com",
    "bbc.com",
    "bbc.co.uk",
    "uol.com.br",
    "estadao.com.br",
    "folha.uol.com.br",
    "cnnbrasil.com.br",
    "camara.leg.br",
    "senado.leg.br",
)
SEARCH_TERMS = (
    '"pessoas atípicas" OR neurodivergente OR neurodiversidade OR '
    'autismo OR autista OR TDAH OR "pessoa com deficiência" OR '
    '"síndrome de Down" OR "deficiência intelectual"'
)
RELEVANT_TITLE_TERMS = (
    "autis",
    "tdah",
    "neurodiverg",
    "neurodivers",
    "atipic",
    "deficiencia",
    "pcd",
    "sindrome de down",
)
MAX_ARTICLES = 3
MAX_FEED_SIZE = 1_000_000


class _TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


def _plain_text(value: str) -> str:
    parser = _TextExtractor()
    parser.feed(value)
    return re.sub(r"\s+", " ", " ".join(parser.parts)).strip()


def _normalize(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value.casefold())
    return "".join(character for character in decomposed if not unicodedata.combining(character))


def _is_trusted_source(source_url: str) -> bool:
    try:
        parsed = urlsplit(source_url)
        hostname = (parsed.hostname or "").casefold().rstrip(".")
    except ValueError:
        return False
    return (
        parsed.scheme == "https"
        and not parsed.username
        and not parsed.password
        and any(
            hostname == domain or hostname.endswith(f".{domain}")
            for domain in TRUSTED_DOMAINS
        )
    )


def _format_date(value: str) -> str:
    if not value:
        return "Data não informada"
    try:
        return parsedate_to_datetime(value).strftime("%d/%m/%Y")
    except (TypeError, ValueError, OverflowError):
        return "Data não informada"


def _parse_google_news_feed(content: bytes) -> list[NewsArticle]:
    if len(content) > MAX_FEED_SIZE:
        raise HTTPException(
            status_code=502,
            detail="A busca de notícias retornou dados acima do limite esperado.",
        )
    try:
        root = ElementTree.fromstring(content)
    except ElementTree.ParseError as error:
        raise HTTPException(
            status_code=502,
            detail="O Google News retornou um feed de notícias inválido.",
        ) from error

    articles: list[NewsArticle] = []
    seen_urls: set[str] = set()
    for item in root.findall(".//item"):
        source_element = item.find("source")
        source_url = source_element.get("url", "") if source_element is not None else ""
        source = _plain_text(source_element.text or "") if source_element is not None else ""
        url = (item.findtext("link") or "").strip()
        title = _plain_text(item.findtext("title") or "")
        summary = _plain_text(item.findtext("description") or "")
        try:
            parsed_article_url = urlsplit(url)
            valid_article_url = (
                parsed_article_url.scheme == "https"
                and parsed_article_url.hostname == "news.google.com"
                and not parsed_article_url.username
                and not parsed_article_url.password
                and parsed_article_url.port in (None, 443)
            )
        except ValueError:
            valid_article_url = False
        normalized_title = _normalize(title)

        if (
            not _is_trusted_source(source_url)
            or not valid_article_url
            or not title
            or not source
            or not any(term in normalized_title for term in RELEVANT_TITLE_TERMS)
            or url in seen_urls
        ):
            continue

        seen_urls.add(url)
        if (
            len(summary) < 60
            or _normalize(title) in _normalize(summary)
            or _normalize(source) in _normalize(summary)
        ):
            summary = "Acesse a notícia para ler a matéria completa."
        articles.append(
            NewsArticle(
                source=source,
                date=_format_date(item.findtext("pubDate") or ""),
                title=title,
                summary=summary[:360],
                url=url,
            )
        )
        if len(articles) == MAX_ARTICLES:
            break
    return articles


async def buscar_noticias() -> list[dict[str, str]]:
    source_query = " OR ".join(f"site:{domain}" for domain in TRUSTED_DOMAINS)
    query = f"({SEARCH_TERMS}) ({source_query}) when:30d"
    params = urlencode(
        {
            "q": query,
            "hl": "pt-BR",
            "gl": "BR",
            "ceid": "BR:pt-419",
        }
    )

    try:
        async with httpx.AsyncClient(timeout=12.0, follow_redirects=True) as client:
            response = await client.get(
                f"{GOOGLE_NEWS_RSS_URL}?{params}",
                headers={"User-Agent": "RedeCuidar/1.0 (news feed)"},
            )
            response.raise_for_status()
    except httpx.TimeoutException as error:
        raise HTTPException(
            status_code=504,
            detail="A busca de notícias demorou demais. Tente novamente.",
        ) from error
    except httpx.HTTPStatusError as error:
        raise HTTPException(
            status_code=502,
            detail="O Google News não conseguiu concluir a busca agora.",
        ) from error
    except httpx.RequestError as error:
        raise HTTPException(
            status_code=503,
            detail="Não foi possível conectar ao Google News.",
        ) from error

    return [
        article.model_dump()
        for article in _parse_google_news_feed(response.content)
    ]
