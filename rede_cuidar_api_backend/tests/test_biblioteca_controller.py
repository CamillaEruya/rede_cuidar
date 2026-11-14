import os
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from fastapi import HTTPException
from google.genai import errors

from app.modules.biblioteca.bibliotecaController import (
    DocumentChunk,
    _rank_chunks,
    _sources,
    _split_text,
    responder_chat,
)
from app.modules.biblioteca.bibliotecaModel import ChatRequest


class BibliotecaControllerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.chunks = [
            DocumentChunk(
                "comunicacao.pdf",
                4,
                "A comunicação pode ser apoiada com recursos alternativos.",
            )
        ]

    def test_ranks_chunks_by_query_relevance(self) -> None:
        relevant = DocumentChunk(
            "comunicacao.pdf",
            2,
            "A comunicação alternativa ajuda no desenvolvimento da linguagem.",
        )
        unrelated = DocumentChunk(
            "rotina.pdf",
            1,
            "A organização da rotina diária pode trazer previsibilidade.",
        )

        ranked = _rank_chunks(
            "comunicação alternativa",
            [unrelated, relevant],
        )

        self.assertEqual(ranked[0], relevant)

    def test_returns_no_chunks_when_query_has_no_match(self) -> None:
        chunks = [
            DocumentChunk("rotina.pdf", 1, "Organização das atividades diárias.")
        ]

        self.assertEqual(_rank_chunks("comunicação alternativa", chunks), [])

    def test_chat_history_accepts_longer_assistant_answers(self) -> None:
        request = ChatRequest(
            message="Pode explicar melhor?",
            history=[
                {
                    "role": "assistant",
                    "content": "Informação relevante. " * 40,
                }
            ],
        )

        self.assertGreater(len(request.history[0].content), 500)

    def test_expands_clinical_queries_to_relevant_symptom_terms(self) -> None:
        symptoms = DocumentChunk(
            "guia-tdah.pdf",
            1,
            "O TDAH é uma condição do neurodesenvolvimento. "
            "Os sinais incluem desatenção, hiperatividade e impulsividade.",
        )
        unrelated = DocumentChunk(
            "beneficios.pdf",
            1,
            "O diagnóstico de TDAH não garante automaticamente o benefício.",
        )

        ranked = _rank_chunks(
            "Quais são as características clínicas do TDAH?",
            [unrelated, symptoms],
        )

        self.assertEqual(ranked[0], symptoms)

    def test_excludes_reference_only_pages_from_search(self) -> None:
        reference = DocumentChunk(
            "fontes.pdf",
            2,
            "Fontes oficiais e leitura complementar "
            "https://example.org TDAH avaliação diagnóstico",
        )
        useful = DocumentChunk(
            "guia.pdf",
            1,
            "A avaliação clínica considera sintomas persistentes de TDAH.",
        )

        ranked = _rank_chunks(
            "avaliação clínica para TDAH",
            [reference, useful],
        )

        self.assertEqual(ranked, [useful])

    def test_splits_long_pages_without_losing_page_reference(self) -> None:
        chunks = _split_text("palavra " * 400, "guia.pdf", 3)

        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(chunk.document == "guia.pdf" for chunk in chunks))
        self.assertTrue(all(chunk.page == 3 for chunk in chunks))

    def test_sources_include_each_document_page_once(self) -> None:
        chunks = [
            DocumentChunk("guia.pdf", 1, "primeiro trecho"),
            DocumentChunk("guia.pdf", 1, "segundo trecho"),
            DocumentChunk("guia.pdf", 2, "outra página"),
        ]

        self.assertEqual(
            _sources(chunks),
            [
                {"document": "guia.pdf", "page": 1},
                {"document": "guia.pdf", "page": 2},
            ],
        )

    def test_orchestrator_returns_answer_and_pdf_sources(self) -> None:
        generate_content = Mock(
            return_value=SimpleNamespace(
                text="A comunicação pode ser apoiada."
            )
        )
        client = SimpleNamespace(
            models=SimpleNamespace(generate_content=generate_content)
        )

        with (
            patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}),
            patch(
                "app.modules.biblioteca.bibliotecaController._load_pdf_chunks",
                return_value=self.chunks,
            ),
            patch(
                "app.modules.biblioteca.bibliotecaController.genai.Client",
                return_value=client,
            ) as gemini_client,
        ):
            result = responder_chat(ChatRequest(message="Como apoiar a comunicação?"))

        self.assertEqual(
            result,
            {
                "answer": "A comunicação pode ser apoiada.",
                "sources": [{"document": "comunicacao.pdf", "page": 4}],
            },
        )
        gemini_client.assert_called_once_with(api_key="test-key")
        generate_content.assert_called_once()
        self.assertEqual(
            generate_content.call_args.kwargs["model"],
            "gemini-3.5-flash-lite",
        )
        config = generate_content.call_args.kwargs["config"]
        self.assertEqual(config.temperature, 0.55)
        self.assertIn("conversa entre duas pessoas", config.system_instruction)
        self.assertIn("sem inventar", config.system_instruction)

    def test_quota_error_returns_free_tier_guidance(self) -> None:
        client = SimpleNamespace(
            models=SimpleNamespace(
                generate_content=Mock(
                    side_effect=errors.APIError(
                        429,
                        {"error": {"status": "RESOURCE_EXHAUSTED"}},
                    )
                )
            )
        )
        with (
            patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}),
            patch(
                "app.modules.biblioteca.bibliotecaController._load_pdf_chunks",
                return_value=self.chunks,
            ),
            patch(
                "app.modules.biblioteca.bibliotecaController.genai.Client",
                return_value=client,
            ),
        ):
            with self.assertRaises(HTTPException) as raised:
                responder_chat(ChatRequest(message="Como apoiar a comunicação?"))

        self.assertEqual(raised.exception.status_code, 503)
        self.assertIn("limite gratuito", raised.exception.detail)

    def test_missing_gemini_key_reports_configuration_needed(self) -> None:
        with (
            patch.dict(os.environ, {"GEMINI_API_KEY": ""}),
            patch(
                "app.modules.biblioteca.bibliotecaController._load_pdf_chunks",
                return_value=self.chunks,
            ),
        ):
            with self.assertRaises(HTTPException) as raised:
                responder_chat(ChatRequest(message="Como apoiar a comunicação?"))

        self.assertEqual(raised.exception.status_code, 503)
        self.assertIn("GEMINI_API_KEY", raised.exception.detail)


if __name__ == "__main__":
    unittest.main()
