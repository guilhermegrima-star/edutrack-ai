import unittest
import datetime
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import utils.exam_prep_service as exam_service


class TestExamPrepService(unittest.TestCase):
    def setUp(self):
        # Limpa o store em memória antes de cada teste
        exam_service._LOCAL_EXAM_STORE["exams"].clear()
        exam_service._LOCAL_EXAM_STORE["mock_questions"].clear()
        exam_service._LOCAL_EXAM_STORE["topic_mastery"].clear()
        exam_service._LOCAL_EXAM_STORE["study_sessions"].clear()
        exam_service.init_exam_prep_store()

    def test_create_exam_validations(self):
        today_future = (datetime.date.today() + datetime.timedelta(days=7)).isoformat()
        yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()

        # Missing title
        with self.assertRaises(ValueError):
            exam_service.create_exam(1, "UI/UX", "", today_future, "Mista", "Conteúdo suficiente de estudo com mais de 15 caracteres")

        # Invalid subject_id
        with self.assertRaises(ValueError):
            exam_service.create_exam(0, "UI/UX", "Prova 1", today_future, "Mista", "Conteúdo suficiente de estudo com mais de 15 caracteres")

        # Date in the past
        with self.assertRaises(ValueError):
            exam_service.create_exam(1, "UI/UX", "Prova 1", yesterday, "Mista", "Conteúdo suficiente de estudo com mais de 15 caracteres")

        # Content too short (< 15 chars)
        with self.assertRaises(ValueError):
            exam_service.create_exam(1, "UI/UX", "Prova 1", today_future, "Mista", "Curto")

    def test_create_exam_success(self):
        future_date = (datetime.date.today() + datetime.timedelta(days=10)).isoformat()
        exam = exam_service.create_exam(
            subject_id=2,
            subject_name="Algoritmos e Programação",
            title="Prova de Estruturas de Dados e Grafos",
            exam_date=future_date,
            exam_type="Múltipla Escolha e Prática",
            content="Árvores Binárias de Busca, Grafos, Algoritmo de Dijkstra e Programação Dinâmica",
        )

        self.assertIsNotNone(exam.get("id"))
        self.assertEqual(exam["title"], "Prova de Estruturas de Dados e Grafos")
        self.assertEqual(exam["exam_date"], future_date)

        # Verifica se gerou questões associadas
        questions = exam_service.get_mock_questions(exam["id"])
        self.assertTrue(len(questions) > 0)

    def test_generate_review_plan(self):
        future_date = (datetime.date.today() + datetime.timedelta(days=5)).isoformat()
        exam = exam_service.create_exam(
            subject_id=1,
            subject_name="UI/UX",
            title="Avaliação de Heurísticas",
            exam_date=future_date,
            exam_type="Mista",
            content="Heurísticas de Nielsen, Testes de Usabilidade e Acessibilidade Web WCAG",
        )

        plan = exam_service.generate_review_plan(exam["id"])
        self.assertEqual(plan["days_remaining"], 5)
        self.assertFalse(plan["is_emergency_d1"])
        self.assertTrue(len(plan["schedule"]) > 0)

    def test_emergency_d1_plan(self):
        tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).isoformat()
        exam = exam_service.create_exam(
            subject_id=1,
            subject_name="UI/UX",
            title="Prova Iminente de Amanhã",
            exam_date=tomorrow,
            exam_type="Mista",
            content="Conceitos vitais de última hora para a avaliação bimestral",
        )

        plan = exam_service.generate_review_plan(exam["id"])
        self.assertTrue(plan["is_emergency_d1"])
        self.assertEqual(plan["days_remaining"], 1)

    def test_update_question_status(self):
        questions = exam_service.get_mock_questions(1)
        self.assertTrue(len(questions) > 0)
        target_q_id = questions[0]["id"]

        # Edita texto e aprova
        updated = exam_service.update_question_status(target_q_id, "approved", "Texto revisado pelo aluno")
        self.assertTrue(updated)

        rev_questions = exam_service.get_mock_questions(1)
        edited_q = next(q for q in rev_questions if q["id"] == target_q_id)
        self.assertEqual(edited_q["question_text"], "Texto revisado pelo aluno")

        # Rejeita questão
        exam_service.update_question_status(target_q_id, "rejected")
        active_questions = exam_service.get_mock_questions(1, include_all_status=False)
        self.assertFalse(any(q["id"] == target_q_id for q in active_questions))

    def test_record_quiz_answer_and_prep_index(self):
        questions = exam_service.get_mock_questions(1)
        target_q = questions[0]

        # Resposta correta
        res_correct = exam_service.record_quiz_answer(
            exam_id=1,
            question_id=target_q["id"],
            selected_option=target_q["correct_option"],
            is_correct=True,
        )
        self.assertTrue(res_correct["is_correct"])
        self.assertGreater(res_correct["prep_index"], 0.0)

    def test_get_d1_emergency_review(self):
        review = exam_service.get_d1_emergency_review(1)
        self.assertIn("cards", review)
        self.assertTrue(len(review["cards"]) > 0)
        self.assertIn("recommendation", review)


if __name__ == "__main__":
    unittest.main()
