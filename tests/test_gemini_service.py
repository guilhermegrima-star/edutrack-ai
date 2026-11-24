import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys
import json

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import utils.gemini_service as gemini_service
import utils.exam_prep_service as exam_service


class TestGeminiService(unittest.TestCase):
    def setUp(self):
        # Garante limpeza do store do Modo Prova antes de cada teste
        exam_service._LOCAL_EXAM_STORE["exams"].clear()
        exam_service._LOCAL_EXAM_STORE["mock_questions"].clear()
        exam_service._LOCAL_EXAM_STORE["topic_mastery"].clear()
        exam_service._LOCAL_EXAM_STORE["study_sessions"].clear()
        exam_service._LOCAL_EXAM_STORE["exam_summaries"].clear()
        exam_service.init_exam_prep_store()

    def test_clean_json_response_markdown_blocks(self):
        # Test markdown code blocks removal
        raw = "```json\n[{\"topic\": \"UX\", \"question_text\": \"Q1\"}]\n```"
        cleaned = gemini_service.clean_json_response(raw)
        self.assertEqual(cleaned, '[{"topic": "UX", "question_text": "Q1"}]')

        # Test raw text before/after json
        raw_with_text = "Aqui está a resposta:\n```json\n{\"summary\": \"Texto de resumo\"}\n```\nEspero ter ajudado!"
        cleaned_obj = gemini_service.clean_json_response(raw_with_text)
        self.assertEqual(cleaned_obj, '{"summary": "Texto de resumo"}')

    @patch("utils.gemini_service.get_gemini_api_key")
    def test_is_gemini_available(self, mock_key):
        mock_key.return_value = ""
        self.assertFalse(gemini_service.is_gemini_available())

        mock_key.return_value = "AIzaSyFakeKey12345"
        self.assertTrue(gemini_service.is_gemini_available())

    @patch("utils.gemini_service.get_gemini_api_key")
    def test_call_gemini_api_missing_key(self, mock_key):
        mock_key.return_value = ""
        with self.assertRaises(ValueError):
            gemini_service.call_gemini_api("teste")

    @patch("utils.gemini_service.requests.post")
    @patch("utils.gemini_service.get_gemini_api_key")
    def test_call_gemini_api_success(self, mock_key, mock_post):
        mock_key.return_value = "AIzaSyFakeKey"
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "candidates": [
                {
                    "content": {
                        "parts": [{"text": '{"result": "ok"}'}]
                    }
                }
            ]
        }
        mock_post.return_value = mock_resp

        result = gemini_service.call_gemini_api("qual o foco?")
        self.assertEqual(result, '{"result": "ok"}')

    @patch("utils.gemini_service.requests.post")
    @patch("utils.gemini_service.get_gemini_api_key")
    def test_call_gemini_api_errors(self, mock_key, mock_post):
        mock_key.return_value = "AIzaSyFakeKey"

        # Rate limit 429
        mock_resp_429 = MagicMock()
        mock_resp_429.status_code = 429
        mock_post.return_value = mock_resp_429
        with self.assertRaises(RuntimeError):
            gemini_service.call_gemini_api("teste")

        # Auth error 401
        mock_resp_401 = MagicMock()
        mock_resp_401.status_code = 401
        mock_post.return_value = mock_resp_401
        with self.assertRaises(PermissionError):
            gemini_service.call_gemini_api("teste")

    @patch("utils.gemini_service.call_gemini_api")
    def test_generate_ai_mock_questions_success(self, mock_call):
        sample_questions = [
            {
                "topic": "Heurísticas de Nielsen",
                "question_text": "Qual heurística foca no feedback em tempo hábil?",
                "options": ["Prevenção de erros", "Visibilidade do status do sistema", "Estética minimalista", "Ajuda e documentação"],
                "correct_option": 1,
                "explanation": "A visibilidade do status mantém o usuário informado.",
                "source_reference": "Capítulo 2 de UX",
            }
        ]
        mock_call.return_value = json.dumps(sample_questions)

        questions = gemini_service.generate_ai_mock_questions("UX", "Prova 1", "Conteúdo de Heurísticas", num_questions=1)
        self.assertEqual(len(questions), 1)
        self.assertEqual(questions[0]["correct_option"], 1)
        self.assertEqual(questions[0]["status"], "approved")

    @patch("utils.gemini_service.call_gemini_api")
    def test_generate_ai_study_plan_success(self, mock_call):
        sample_plan = [
            {
                "day": "Dia 1",
                "focus": "Conceitos Básicos",
                "topics": ["Tópico 1"],
                "tasks": ["Ler apostila", "Fazer 5 questões"],
                "study_technique": "Active Recall",
            }
        ]
        mock_call.return_value = json.dumps(sample_plan)

        plan = gemini_service.generate_ai_study_plan("Prova 1", 5, "Conteúdo", ["Tópico 1"])
        self.assertEqual(len(plan), 1)
        self.assertEqual(plan[0]["study_technique"], "Active Recall")

    @patch("utils.gemini_service.call_gemini_api")
    def test_generate_ai_summary_and_flashcards(self, mock_call):
        sample_data = {
            "summary": "Resumo completo da matéria.",
            "key_points": ["Ponto 1", "Ponto 2"],
            "flashcards": [
                {"topic": "UX", "front": "O que é SUS?", "back": "System Usability Scale"}
            ]
        }
        mock_call.return_value = json.dumps(sample_data)

        res = gemini_service.generate_ai_summary_and_flashcards("Prova 1", "Conteúdo")
        self.assertIn("summary", res)
        self.assertEqual(len(res["flashcards"]), 1)
        self.assertEqual(res["flashcards"][0]["front"], "O que é SUS?")

    @patch("utils.gemini_service.generate_ai_summary_and_flashcards")
    @patch("utils.gemini_service.is_gemini_available")
    @patch("utils.gemini_service.generate_ai_mock_questions")
    def test_create_exam_with_ai_integration(self, mock_ai_qs, mock_avail, mock_summary):
        mock_avail.return_value = True
        mock_summary.return_value = {
            "summary": "Resumo simulado",
            "key_points": ["P1"],
            "flashcards": [],
        }
        mock_ai_qs.return_value = [
            {
                "topic": "IA Generativa",
                "question_text": "Questão gerada por IA?",
                "options": ["A", "B", "C", "D"],
                "correct_option": 0,
                "explanation": "Explicação da IA",
                "source_reference": "Ementa",
                "status": "approved",
            }
        ]


        import datetime
        future_date = (datetime.date.today() + datetime.timedelta(days=7)).isoformat()
        exam = exam_service.create_exam(
            subject_id=1,
            subject_name="Inteligência Artificial",
            title="Prova Bimestral de IA",
            exam_date=future_date,
            exam_type="Múltipla Escolha",
            content="Redes Neurais, Modelos de Linguagem e Agentes Autônomos",
        )

        self.assertIsNotNone(exam.get("id"))
        questions = exam_service.get_mock_questions(exam["id"])
        self.assertEqual(len(questions), 1)
        self.assertEqual(questions[0]["question_text"], "Questão gerada por IA?")

    def test_get_exam_ai_summary_fallback(self):
        # Sem IA disponível, o fallback heurístico deve gerar resumo e flashcards
        summary_obj = exam_service.get_exam_ai_summary_and_flashcards(1)
        self.assertIn("summary", summary_obj)
        self.assertTrue(len(summary_obj.get("flashcards", [])) > 0)


if __name__ == "__main__":
    unittest.main()
