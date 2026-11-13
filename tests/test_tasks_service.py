import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Ensure requests and streamlit can be imported/mocked for testing
if "requests" not in sys.modules:
    mock_req_module = MagicMock()
    sys.modules["requests"] = mock_req_module
else:
    mock_req_module = sys.modules["requests"]

if "streamlit" not in sys.modules:
    mock_st_module = MagicMock()
    mock_st_module.session_state = {}
    sys.modules["streamlit"] = mock_st_module

import utils.tasks_service as tasks_service
tasks_service.requests = mock_req_module


class TestTasksService(unittest.TestCase):
    def setUp(self):
        # Reset local memory store and session_state before each test
        tasks_service._LOCAL_MEMORY_STORE.clear()
        if hasattr(tasks_service.st, "session_state") and isinstance(tasks_service.st.session_state, dict):
            tasks_service.st.session_state.clear()
        tasks_service.init_tasks_store()

    def test_create_subject_validates_required_fields(self):
        # Missing or empty name
        with self.assertRaises(ValueError):
            tasks_service.create_subject("", "Prof. Silva", 60)
        with self.assertRaises(ValueError):
            tasks_service.create_subject("   ", "Prof. Silva", 60)

        # Missing or empty teacher
        with self.assertRaises(ValueError):
            tasks_service.create_subject("Matemática", "", 60)
        with self.assertRaises(ValueError):
            tasks_service.create_subject("Matemática", "   ", 60)

        # Invalid hours
        with self.assertRaises(ValueError):
            tasks_service.create_subject("Matemática", "Prof. Silva", 0)
        with self.assertRaises(ValueError):
            tasks_service.create_subject("Matemática", "Prof. Silva", -10)
        with self.assertRaises(ValueError):
            tasks_service.create_subject("Matemática", "Prof. Silva", "invalid")

    @patch("utils.tasks_service.requests.post")
    def test_create_subject_xano_success(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "id": 101,
            "name": "Inteligência Artificial",
            "teacher": "Prof. Guilherme",
            "hours": 80,
            "user_id": 5,
        }
        mock_post.return_value = mock_resp

        sub = tasks_service.create_subject(
            name="Inteligência Artificial",
            teacher="Prof. Guilherme",
            hours=80,
            token="fake-jwt-token",
        )

        self.assertEqual(sub["id"], 101)
        self.assertEqual(sub["name"], "Inteligência Artificial")
        self.assertEqual(sub["teacher"], "Prof. Guilherme")
        self.assertEqual(sub["hours"], 80)
        self.assertIn("color", sub)

        # Verify API request
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertTrue(args[0].endswith("/subjects"))
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer fake-jwt-token")
        self.assertEqual(
            kwargs["json"],
            {"name": "Inteligência Artificial", "teacher": "Prof. Guilherme", "hours": 80},
        )

        # Verify presence in store
        subjects = tasks_service.get_subjects()
        self.assertTrue(any(s.get("id") == 101 for s in subjects))

    @patch("utils.tasks_service.requests.post")
    def test_create_subject_local_fallback_on_network_failure(self, mock_post):
        mock_post.side_effect = Exception("Network timeout")

        sub = tasks_service.create_subject(
            name="Redes de Computadores",
            teacher="Prof. Ricardo",
            hours=60,
            token="fake-jwt-token",
        )

        self.assertIsNotNone(sub.get("id"))
        self.assertEqual(sub["name"], "Redes de Computadores")
        self.assertEqual(sub["teacher"], "Prof. Ricardo")
        self.assertEqual(sub["hours"], 60)

        # Verify store has the new subject
        subjects = tasks_service.get_subjects()
        self.assertTrue(any(s.get("name") == "Redes de Computadores" for s in subjects))

    def test_create_task_validates_required_fields(self):
        with self.assertRaises(ValueError):
            tasks_service.create_task("", "desc", "2026-11-20", "Pendente", 1)

        with self.assertRaises(ValueError):
            tasks_service.create_task("Título", "desc", "", "Pendente", 1)

        with self.assertRaises(ValueError):
            tasks_service.create_task("Título", "desc", "2026-11-20", "Pendente", None)

    def test_create_task_validates_subject_ownership(self):
        # Default subjects have IDs 1, 2, 3, 4, 5
        # Subject ID 999 does not belong to the user
        with self.assertRaises(ValueError) as ctx:
            tasks_service.create_task(
                title="Exercício de Grafos",
                description="Resolver itens",
                due_date="2026-11-25",
                status="Pendente",
                subject_id=999,
            )
        self.assertIn("não pertence ao usuário", str(ctx.exception).lower())

    @patch("utils.tasks_service.requests.post")
    def test_create_task_xano_success(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "id": 202,
            "title": "Projeto Final Streamlit",
            "description": "Criar dashboard integrado",
            "due_date": "2026-11-30",
            "status": "Em Andamento",
            "subject_id": 1,
            "user_id": 5,
        }
        mock_post.return_value = mock_resp

        task = tasks_service.create_task(
            title="Projeto Final Streamlit",
            description="Criar dashboard integrado",
            due_date="2026-11-30",
            status="Em Andamento",
            subject_id=1,
            token="fake-jwt-token",
        )

        self.assertEqual(task["id"], 202)
        self.assertEqual(task["title"], "Projeto Final Streamlit")
        self.assertEqual(task["subject_id"], 1)

        # Verify API request
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertTrue("/academic_tasks" in args[0] or "/task" in args[0])
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer fake-jwt-token")
        self.assertEqual(kwargs["json"]["title"], "Projeto Final Streamlit")
        self.assertEqual(kwargs["json"]["subject_id"], 1)

        # Verify task is in local store
        tasks = tasks_service.get_tasks_by_subject(subject_id=1)
        self.assertTrue(any(t.get("id") == 202 for t in tasks))

    @patch("utils.tasks_service.requests.post")
    def test_create_task_permission_error_from_backend(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.ok = False
        mock_resp.status_code = 403
        mock_resp.json.return_value = {
            "message": "Acesso negado: a matéria informada não pertence a você"
        }
        mock_post.return_value = mock_resp

        with self.assertRaises(PermissionError):
            tasks_service.create_task(
                title="Tentativa Indevida",
                description="",
                due_date="2026-11-20",
                status="Pendente",
                subject_id=1,
                token="fake-jwt-token",
            )

    @patch("utils.tasks_service.requests.get")
    def test_get_subjects_from_xano(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.json.return_value = [
            {"id": 10, "name": "Deep Learning", "teacher": "Prof. Turing", "hours": 90, "user_id": 1}
        ]
        mock_get.return_value = mock_resp

        subs = tasks_service.get_subjects(token="jwt-123")
        self.assertEqual(len(subs), 1)
        self.assertEqual(subs[0]["name"], "Deep Learning")
        self.assertIn("color", subs[0])

    @patch("utils.tasks_service.requests.get")
    def test_get_tasks_by_subject_from_xano(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_resp.json.return_value = [
            {"id": 50, "title": "Paper Review", "due_date": "2026-11-15", "status": "Pendente", "subject_id": 1},
            {"id": 51, "title": "Coding Assignment", "due_date": "2026-11-12", "status": "Concluído", "subject_id": 1},
        ]
        mock_get.return_value = mock_resp

        tasks = tasks_service.get_tasks_by_subject(subject_id=1, token="jwt-123")
        self.assertEqual(len(tasks), 2)
        # Verify sorted by due_date
        self.assertEqual(tasks[0]["id"], 51)
        self.assertEqual(tasks[1]["id"], 50)

    @patch("utils.tasks_service.requests.patch")
    def test_update_task_status(self, mock_patch):
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_patch.return_value = mock_resp

        # Task 1 exists in INITIAL_TASKS
        ok = tasks_service.update_task_status(1, "Concluído", token="jwt-123")
        self.assertTrue(ok)
        tasks = tasks_service.get_tasks_by_subject(subject_id=1)
        task_1 = next(t for t in tasks if t["id"] == 1)
        self.assertEqual(task_1["status"], "Concluído")

    @patch("utils.tasks_service.requests.delete")
    def test_delete_task(self, mock_delete):
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_delete.return_value = mock_resp

        before_count = len(tasks_service.get_tasks_by_subject())
        ok = tasks_service.delete_task(1, token="jwt-123")
        self.assertTrue(ok)
        after_count = len(tasks_service.get_tasks_by_subject())
        self.assertEqual(after_count, before_count - 1)

    @patch("utils.tasks_service.requests.delete")
    def test_delete_subject(self, mock_delete):
        mock_resp = MagicMock()
        mock_resp.ok = True
        mock_delete.return_value = mock_resp

        before_count = len(tasks_service.get_subjects())
        ok = tasks_service.delete_subject(1, token="jwt-123")
        self.assertTrue(ok)
        after_count = len(tasks_service.get_subjects())
        self.assertEqual(after_count, before_count - 1)

    def test_calculate_subject_progress(self):
        tasks = [
            {"status": "Concluído"},
            {"status": "concluido"},
            {"status": "Em Andamento"},
            {"status": "Pendente"},
        ]
        prog = tasks_service.calculate_subject_progress(tasks)
        self.assertEqual(prog["total"], 4)
        self.assertEqual(prog["completed"], 2)
        self.assertEqual(prog["pending"], 2)
        self.assertEqual(prog["percent"], 50.0)

        empty_prog = tasks_service.calculate_subject_progress([])
        self.assertEqual(empty_prog["total"], 0)
        self.assertEqual(empty_prog["percent"], 0.0)


if __name__ == "__main__":
    unittest.main()
