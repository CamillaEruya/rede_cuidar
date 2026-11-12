import unittest

from app.modules.biblioteca.noticiasController import _parse_google_news_feed


class BibliotecaNewsTests(unittest.TestCase):
    def test_returns_three_recent_articles_from_trusted_sources_only(self) -> None:
        items = []
        sources = [
            ("Agência Brasil", "https://agenciabrasil.ebc.com.br"),
            ("Ministério da Saúde", "https://www.gov.br/saude"),
            ("Fiocruz", "https://portal.fiocruz.br"),
            ("Agência Gov", "https://agenciagov.ebc.com.br"),
            ("Notícia falsa", "https://gov.br.example.com"),
        ]
        titles = [
            "Autismo: conheça direitos e políticas",
            "TDAH em adultos: novas orientações",
            "Neurodiversidade nas escolas",
            "Enem tem participação recorde de concluintes",
            "Notícia sobre autismo",
        ]
        for index, (source, source_url) in enumerate(sources):
            items.append(
                f"""
                <item>
                  <title>{titles[index]}</title>
                  <link>https://news.google.com/rss/articles/{index}</link>
                  <description>&lt;p&gt;Esta matéria traz informações sobre direitos, inclusão e apoio para pessoas neurodivergentes. &lt;b&gt;Leia mais&lt;/b&gt;.&lt;/p&gt;</description>
                  <source url="{source_url}">{source}</source>
                  <pubDate>Tue, 10 Nov 2026 10:00:00 GMT</pubDate>
                </item>
                """
            )
        feed = (
            '<?xml version="1.0" encoding="UTF-8"?><rss><channel>'
            + "".join(items)
            + "</channel></rss>"
        ).encode()

        articles = _parse_google_news_feed(feed)

        self.assertEqual(len(articles), 3)
        self.assertEqual(articles[0].source, "Agência Brasil")
        self.assertEqual(articles[0].title, "Autismo: conheça direitos e políticas")
        self.assertIn("pessoas neurodivergentes", articles[0].summary)
        self.assertEqual(articles[0].date, "10/11/2026")
        self.assertTrue(all(article.url.startswith("https://news.google.com/") for article in articles))

    def test_rejects_non_google_article_links(self) -> None:
        feed = """
        <rss><channel><item>
          <title>Matéria</title>
          <link>https://news.google.com.evil.example/article</link>
          <description>Resumo</description>
          <source url="https://www.gov.br">Governo Federal</source>
        </item></channel></rss>
        """.encode()

        self.assertEqual(_parse_google_news_feed(feed), [])


if __name__ == "__main__":
    unittest.main()
