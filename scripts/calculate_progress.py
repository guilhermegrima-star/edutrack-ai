"""
calculate_progress.py
---------------------
Calcula a porcentagem de progresso de uma disciplina (subject) com base
em suas tarefas, consumindo os endpoints CRUD da API Xano.

Grupo de API utilizado: edutrack.ai  (canonical: gTfD518O)
  Todos os endpoints exigem autenticação JWT (Bearer token).

Endpoints utilizados:
  GET  /<TASKS_PATH>              → lista tarefas do usuário (filtro opcional: subject_id)
  GET  /<TASKS_PATH>/{id}         → detalhes de uma tarefa do usuário
  GET  /subjects/{id}             → detalhes de uma disciplina do usuário
  POST /<TASKS_PATH>              → criação de tarefa   (disponível via cliente)
  PATCH /<TASKS_PATH>/{id}        → atualização de tarefa (disponível via cliente)
  DELETE /<TASKS_PATH>/{id}       → remoção de tarefa   (disponível via cliente)

Variáveis de ambiente (.env):
  EDUTRACK_BASE_URL  — URL base do grupo edutrack.ai
                       Padrão: https://x8ki-letl-twmt.n7.xano.io/api:gTfD518O
  EDUTRACK_TASKS_PATH — segmento de path do endpoint de tarefas
                        Padrão: "academic_tasks"  (ex: "task", "tasks")
  EDUTRACK_TOKEN     — JWT de autenticação (alternativa ao argumento --token)

Regras de negócio:
  - Uma tarefa é considerada "concluída" quando status == "done" (case-insensitive).
  - O progresso é calculado como (tarefas_concluídas / total_tarefas) × 100.
  - Se não houver tarefas, o progresso é 0 e a função sinaliza isso na resposta.
  - Erros HTTP (404, 401, 500, etc.) NÃO interrompem o script: são capturados e
    retornados como JSON estruturado com o campo "error".
  - Requer autenticação JWT (token Bearer) passado ao instanciar EduTrackClient.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any

import requests
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Configuração (Streamlit Secrets / os.environ / .env)
# ---------------------------------------------------------------------------

try:
    from utils.config import get_edutrack_base_url, get_tasks_path, get_auth_token
    BASE_URL: str = get_edutrack_base_url()
    TASKS_PATH: str = get_tasks_path()
    DEFAULT_TOKEN: str = get_auth_token()
except ImportError:
    try:
        import sys
        from pathlib import Path
        sys.path.append(str(Path(__file__).resolve().parent.parent))
        from utils.config import get_edutrack_base_url, get_tasks_path, get_auth_token
        BASE_URL: str = get_edutrack_base_url()
        TASKS_PATH: str = get_tasks_path()
        DEFAULT_TOKEN: str = get_auth_token()
    except Exception:
        load_dotenv()
        BASE_URL: str = os.getenv(
            "EDUTRACK_BASE_URL",
            "https://x8ki-letl-twmt.n7.xano.io/api:gTfD518O",
        ).rstrip("/")
        TASKS_PATH: str = os.getenv("EDUTRACK_TASKS_PATH", "task").strip("/")
        DEFAULT_TOKEN: str = os.getenv("EDUTRACK_TOKEN", "")

DONE_STATUS: str = "done"  # valor do campo `status` que representa conclusão


# ---------------------------------------------------------------------------
# Tipos de retorno de erro
# ---------------------------------------------------------------------------

def _error_response(
    subject_id: int,
    subject_name: str,
    error_code: str,
    error_message: str,
) -> dict[str, Any]:
    """Monta um JSON de erro com a mesma estrutura do JSON de sucesso."""
    return {
        "subject_id": subject_id,
        "subject_name": subject_name,
        "total_tasks": 0,
        "completed_tasks": 0,
        "pending_tasks": 0,
        "progress_percent": 0.0,
        "has_tasks": False,
        "tasks_detail": [],
        "error": {
            "code": error_code,
            "message": error_message,
        },
    }


# ---------------------------------------------------------------------------
# Cliente HTTP reutilizável
# ---------------------------------------------------------------------------


@dataclass
class EduTrackClient:
    """Cliente leve para consumir os endpoints CRUD do EduTrack (Xano)."""

    token: str
    base_url: str = BASE_URL
    tasks_path: str = TASKS_PATH
    _session: requests.Session = field(default_factory=requests.Session, init=False, repr=False)

    def __post_init__(self) -> None:
        self._session.headers.update(
            {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json",
            }
        )

    # ------------------------------------------------------------------
    # Helpers internos
    # ------------------------------------------------------------------

    def _safe_get(self, url: str, params: dict[str, Any] | None = None) -> requests.Response:
        """Executa GET e retorna a Response sem lançar exceção."""
        return self._session.get(url, params=params or {})

    def _safe_post(self, url: str, payload: dict[str, Any]) -> requests.Response:
        return self._session.post(url, json=payload)

    def _safe_patch(self, url: str, payload: dict[str, Any]) -> requests.Response:
        return self._session.patch(url, json=payload)

    def _safe_delete(self, url: str) -> requests.Response:
        return self._session.delete(url)

    # ------------------------------------------------------------------
    # Subjects (disciplinas)
    # ------------------------------------------------------------------

    def get_subject(self, subject_id: int) -> dict[str, Any]:
        """GET /subjects/{subject_id} — detalhes de uma disciplina.

        Retorna o JSON da API ou um dict com chave 'error' em caso de falha HTTP.
        Nunca lança HTTPError.
        """
        resp = self._safe_get(f"{self.base_url}/subjects/{subject_id}")
        if not resp.ok:
            return {
                "error": {
                    "code": f"HTTP_{resp.status_code}",
                    "message": f"GET /subjects/{subject_id} retornou {resp.status_code}: {resp.text[:200]}",
                }
            }
        return resp.json()

    # ------------------------------------------------------------------
    # Academic Tasks (tarefas) — path configurável via tasks_path
    # ------------------------------------------------------------------

    def list_tasks(self, subject_id: int | None = None) -> dict[str, Any]:
        """GET /<tasks_path>[?subject_id=X] — lista tarefas do usuário autenticado.

        Retorna dict com chave 'items' (lista de tarefas) ou 'error' em falha HTTP.
        """
        params: dict[str, Any] = {}
        if subject_id is not None:
            params["subject_id"] = subject_id

        url = f"{self.base_url}/{self.tasks_path}"
        resp = self._safe_get(url, params=params)

        if not resp.ok:
            return {
                "items": [],
                "error": {
                    "code": f"HTTP_{resp.status_code}",
                    "message": f"GET /{self.tasks_path} retornou {resp.status_code}: {resp.text[:200]}",
                },
            }

        data = resp.json()
        # Normaliza: lista direta → {"items": [...]}
        if isinstance(data, list):
            return {"items": data}
        # Envelope com "items", "result" ou similar
        items = data.get("items", data.get("result", data.get("data", [])))
        return {"items": items if isinstance(items, list) else []}

    def get_task(self, task_id: int) -> dict[str, Any]:
        """GET /<tasks_path>/{task_id} — detalhes de uma tarefa."""
        resp = self._safe_get(f"{self.base_url}/{self.tasks_path}/{task_id}")
        if not resp.ok:
            return {
                "error": {
                    "code": f"HTTP_{resp.status_code}",
                    "message": f"GET /{self.tasks_path}/{task_id} retornou {resp.status_code}: {resp.text[:200]}",
                }
            }
        return resp.json()

    def create_task(self, payload: dict[str, Any]) -> dict[str, Any]:
        """POST /<tasks_path> — cria uma nova tarefa."""
        resp = self._safe_post(f"{self.base_url}/{self.tasks_path}", payload)
        if not resp.ok:
            return {
                "error": {
                    "code": f"HTTP_{resp.status_code}",
                    "message": f"POST /{self.tasks_path} retornou {resp.status_code}: {resp.text[:200]}",
                }
            }
        return resp.json()

    def update_task(self, task_id: int, payload: dict[str, Any]) -> dict[str, Any]:
        """PATCH /<tasks_path>/{task_id} — atualiza uma tarefa existente."""
        resp = self._safe_patch(f"{self.base_url}/{self.tasks_path}/{task_id}", payload)
        if not resp.ok:
            return {
                "error": {
                    "code": f"HTTP_{resp.status_code}",
                    "message": f"PATCH /{self.tasks_path}/{task_id} retornou {resp.status_code}: {resp.text[:200]}",
                }
            }
        return resp.json()

    def delete_task(self, task_id: int) -> dict[str, Any]:
        """DELETE /<tasks_path>/{task_id} — remove uma tarefa."""
        resp = self._safe_delete(f"{self.base_url}/{self.tasks_path}/{task_id}")
        if not resp.ok:
            return {
                "error": {
                    "code": f"HTTP_{resp.status_code}",
                    "message": f"DELETE /{self.tasks_path}/{task_id} retornou {resp.status_code}: {resp.text[:200]}",
                }
            }
        return resp.json()


# ---------------------------------------------------------------------------
# Lógica de cálculo de progresso
# ---------------------------------------------------------------------------


def calculate_progress(
    client: EduTrackClient,
    subject_id: int,
    done_status: str = DONE_STATUS,
) -> dict[str, Any]:
    """
    Calcula a porcentagem de progresso de uma disciplina com base em suas tarefas.

    Parâmetros
    ----------
    client : EduTrackClient
        Instância autenticada do cliente da API.
    subject_id : int
        ID da disciplina (subject) a ser analisada.
    done_status : str, opcional
        Valor do campo ``status`` que representa uma tarefa concluída.
        Padrão: ``"done"`` (comparação case-insensitive).

    Retorna
    -------
    dict
        Em caso de sucesso, JSON com os campos:
        - subject_id         : int   — ID da disciplina
        - subject_name       : str   — nome da disciplina
        - total_tasks        : int   — número total de tarefas
        - completed_tasks    : int   — número de tarefas concluídas
        - pending_tasks      : int   — número de tarefas pendentes
        - progress_percent   : float — porcentagem de conclusão (0–100, 2 casas decimais)
        - has_tasks          : bool  — indica se existem tarefas cadastradas
        - tasks_detail       : list  — lista resumida de cada tarefa

        Em caso de erro HTTP (404, 401, 500, etc.), os campos numéricos assumem
        valor 0/0.0/False e o dict inclui adicionalmente:
        - error: { code: str, message: str }
    """
    # 1. Busca dados da disciplina ------------------------------------------
    subject_result = client.get_subject(subject_id)
    if "error" in subject_result:
        return _error_response(
            subject_id=subject_id,
            subject_name="N/A",
            error_code=subject_result["error"]["code"],
            error_message=subject_result["error"]["message"],
        )
    subject_name: str = subject_result.get("name", "N/A")

    # 2. Busca tarefas filtradas pela disciplina -----------------------------
    tasks_result = client.list_tasks(subject_id=subject_id)
    if "error" in tasks_result:
        # Endpoint de tasks indisponível (ex: 404): retorna progresso zero com detalhe do erro
        return _error_response(
            subject_id=subject_id,
            subject_name=subject_name,
            error_code=tasks_result["error"]["code"],
            error_message=tasks_result["error"]["message"],
        )

    tasks: list[dict[str, Any]] = tasks_result["items"]

    # 3. Calcula métricas ----------------------------------------------------
    total: int = len(tasks)
    completed: int = sum(
        1 for t in tasks if str(t.get("status", "")).strip().lower() == done_status.lower()
    )
    pending: int = total - completed
    progress: float = round((completed / total) * 100, 2) if total > 0 else 0.0

    # 4. Resumo por tarefa ---------------------------------------------------
    tasks_detail: list[dict[str, Any]] = [
        {
            "id": t.get("id"),
            "title": t.get("title"),
            "status": t.get("status"),
            "due_date": t.get("due_date"),
            "is_done": str(t.get("status", "")).strip().lower() == done_status.lower(),
        }
        for t in tasks
    ]

    # 5. Monta e retorna o resultado -----------------------------------------
    return {
        "subject_id": subject_id,
        "subject_name": subject_name,
        "total_tasks": total,
        "completed_tasks": completed,
        "pending_tasks": pending,
        "progress_percent": progress,
        "has_tasks": total > 0,
        "tasks_detail": tasks_detail,
    }


# ---------------------------------------------------------------------------
# Utilitário: imprime JSON formatado
# ---------------------------------------------------------------------------


def progress_to_json(result: dict[str, Any], indent: int = 2) -> str:
    """Serializa o resultado de ``calculate_progress`` para uma string JSON."""
    return json.dumps(result, ensure_ascii=False, indent=indent)


# ---------------------------------------------------------------------------
# Ponto de entrada (uso direto via linha de comando)
# ---------------------------------------------------------------------------


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Calcula o progresso de uma disciplina no EduTrack AI."
    )
    parser.add_argument(
        "--subject-id",
        type=int,
        required=True,
        help="ID da disciplina (subject) a ser analisada.",
    )
    parser.add_argument(
        "--token",
        type=str,
        default=DEFAULT_TOKEN,
        help="Token JWT de autenticação (ou defina a env EDUTRACK_TOKEN / secrets.toml).",
    )
    parser.add_argument(
        "--done-status",
        type=str,
        default=DONE_STATUS,
        help=f'Valor de status que representa "concluído". Padrão: "{DONE_STATUS}".',
    )
    parser.add_argument(
        "--tasks-path",
        type=str,
        default=TASKS_PATH,
        help=(
            f'Segmento de path do endpoint de tarefas no Xano. '
            f'Padrão: "{TASKS_PATH}" (sobrescreva com "task" ou "tasks" conforme o Xano, '
            f'ou defina a env EDUTRACK_TASKS_PATH).'
        ),
    )
    args = parser.parse_args()

    if not args.token:
        raise SystemExit(
            "❌ Token de autenticação não informado. "
            "Use --token <JWT> ou defina a variável de ambiente EDUTRACK_TOKEN."
        )

    client = EduTrackClient(token=args.token, tasks_path=args.tasks_path)
    progress_result = calculate_progress(
        client=client,
        subject_id=args.subject_id,
        done_status=args.done_status,
    )
    print(progress_to_json(progress_result))
