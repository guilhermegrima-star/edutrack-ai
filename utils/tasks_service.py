"""
utils/tasks_service.py
-----------------------
Serviço para gerenciamento de disciplinas e obrigações acadêmicas (academic_tasks).
Comunicação direta com a API Xano (edutrack.ai) e sincronização bidirecional
com st.session_state (com fallback local seguro em caso de indisponibilidade).

Esquemas de Dados:
1. subjects (Matérias / Professores):
   - id: int
   - name: str (Nome da disciplina)
   - teacher: str (Nome do professor - ponto de ligação da entidade professor)
   - hours: int (Carga horária)
   - user_id: int (Vínculo com o usuário autenticado, definido pelo auth.id no Xano)
   - color: str (Metadado visual para renderização de cards e gráficos)

2. academic_tasks (Obrigações Acadêmicas):
   - id: int
   - title: str (Título da obrigação: lição, prova ou trabalho)
   - description: str (Critérios, instruções e referências)
   - due_date: str (Data de entrega no formato AAAA-MM-DD)
   - status: str ('Pendente', 'Em Andamento', 'Concluído')
   - subject_id: int (Referência FK para a matéria em subjects)
   - user_id: int (Vínculo com o usuário autenticado)
   - created_at: str (Timestamp de criação)
"""

from __future__ import annotations
import os
import datetime
from typing import Any

try:
    import requests
except ImportError:
    requests = None

try:
    import streamlit as st
except ImportError:
    st = None

try:
    from utils.config import get_edutrack_base_url, get_tasks_path, get_auth_token
    BASE_URL = get_edutrack_base_url()
    TASKS_PATH = get_tasks_path()
except ImportError:
    BASE_URL = os.environ.get("EDUTRACK_BASE_URL", "https://x8ki-letl-twmt.n7.xano.io/api:gTfD518O").rstrip("/")
    TASKS_PATH = os.environ.get("EDUTRACK_TASKS_PATH", "task").strip("/")
    get_auth_token = lambda: os.environ.get("EDUTRACK_TOKEN", "")

# Paleta de cores para enriquecimento visual dos cards de matérias
SUBJECT_PALETTE = [
    "#6C5CE7",  # Roxo
    "#F6C768",  # Amarelo/Ouro
    "#4E44B4",  # Índigo
    "#10B981",  # Verde Esmeralda
    "#3B82F6",  # Azul
    "#EC4899",  # Rosa
    "#8B5CF6",  # Violeta
    "#F59E0B",  # Laranja
    "#06B6D4",  # Ciano
]

# Lista padrão de disciplinas do curso (para fallback offline / demonstração)
DEFAULT_SUBJECTS = [
    {"id": 1, "name": "UI UX Fundamentals", "teacher": "Prof. Ana Ribeiro", "hours": 80, "color": "#6C5CE7"},
    {"id": 2, "name": "UI Colours theories", "teacher": "Prof. Carlos Duarte", "hours": 60, "color": "#F6C768"},
    {"id": 3, "name": "Algoritmos e Programação", "teacher": "Prof. Ricardo Neves", "hours": 80, "color": "#4E44B4"},
    {"id": 4, "name": "Inteligência Artificial & Lab", "teacher": "Prof. Guilherme Grima", "hours": 80, "color": "#10B981"},
    {"id": 5, "name": "Bases de Dados Relacionais", "teacher": "Prof. Carlos Duarte", "hours": 60, "color": "#3B82F6"},
]

# Obrigações acadêmicas iniciais de exemplo
INITIAL_TASKS = [
    {
        "id": 1,
        "title": "Wireframe de Alta Fidelidade no Figma",
        "description": "Desenvolver protótipo navegável do aplicativo com guia de estilos e componentes reaproveitáveis.",
        "due_date": (datetime.date.today() + datetime.timedelta(days=2)).isoformat(),
        "status": "Em Andamento",
        "subject_id": 1,
    },
    {
        "id": 2,
        "title": "Questionário sobre Heurísticas de Nielsen",
        "description": "Responder aos 10 itens de análise ergonômica da interface selecionada.",
        "due_date": (datetime.date.today() - datetime.timedelta(days=1)).isoformat(),
        "status": "Concluído",
        "subject_id": 1,
    },
    {
        "id": 3,
        "title": "Estudo de Caso: Harmonia e Contraste WCAG",
        "description": "Elaborar paleta com taxa de contraste mínima de 4.5:1 para conformidade de acessibilidade.",
        "due_date": (datetime.date.today() + datetime.timedelta(days=4)).isoformat(),
        "status": "Pendente",
        "subject_id": 2,
    },
    {
        "id": 4,
        "title": "Implementação de Árvores Binárias em Python",
        "description": "Resolver exercícios de busca binária e percursos pré-ordem, in-ordem e pós-ordem.",
        "due_date": (datetime.date.today() + datetime.timedelta(days=6)).isoformat(),
        "status": "Em Andamento",
        "subject_id": 3,
    },
    {
        "id": 5,
        "title": "Lista 1 de Algoritmos de Ordenação",
        "description": "Implementar e comparar complexidade do MergeSort e QuickSort com arrays aleatórios.",
        "due_date": (datetime.date.today() - datetime.timedelta(days=3)).isoformat(),
        "status": "Concluído",
        "subject_id": 3,
    },
    {
        "id": 6,
        "title": "Laboratório de Fine-Tuning e Prompts com LLM",
        "description": "Construir pipeline de prompt engineering com avaliação de precisão das respostas.",
        "due_date": (datetime.date.today() + datetime.timedelta(days=8)).isoformat(),
        "status": "Pendente",
        "subject_id": 4,
    },
]

# Armazenamento em memória local defensivo para execução fora do Streamlit
_LOCAL_MEMORY_STORE: dict[str, list[dict[str, Any]]] = {}


def init_tasks_store():
    """Garante que a estrutura de armazenamento no session_state ou memória local exista."""
    try:
        if hasattr(st, "session_state") and st.session_state is not None:
            if "academic_tasks_store" not in st.session_state:
                st.session_state["academic_tasks_store"] = [dict(t) for t in INITIAL_TASKS]
            if "subjects_store" not in st.session_state:
                st.session_state["subjects_store"] = [dict(s) for s in DEFAULT_SUBJECTS]
            return
    except Exception:
        pass

    if "academic_tasks_store" not in _LOCAL_MEMORY_STORE:
        _LOCAL_MEMORY_STORE["academic_tasks_store"] = [dict(t) for t in INITIAL_TASKS]
    if "subjects_store" not in _LOCAL_MEMORY_STORE:
        _LOCAL_MEMORY_STORE["subjects_store"] = [dict(s) for s in DEFAULT_SUBJECTS]


def _get_store_list(key: str) -> list[dict[str, Any]]:
    """Recupera lista armazenada de forma segura."""
    init_tasks_store()
    try:
        if hasattr(st, "session_state") and st.session_state is not None and key in st.session_state:
            return st.session_state[key]
    except Exception:
        pass
    return _LOCAL_MEMORY_STORE.setdefault(key, [])


def _set_store_list(key: str, val: list[dict[str, Any]]):
    """Atualiza lista armazenada de forma segura."""
    init_tasks_store()
    try:
        if hasattr(st, "session_state") and st.session_state is not None:
            st.session_state[key] = val
    except Exception:
        pass
    _LOCAL_MEMORY_STORE[key] = val


def _resolve_auth_token(explicit_token: str | None = None) -> str | None:
    """Resolve o token de autenticação: parâmetro explícito -> session_state -> secrets/env."""
    if explicit_token and str(explicit_token).strip():
        return str(explicit_token).strip()
    try:
        if hasattr(st, "session_state") and st.session_state is not None:
            token = st.session_state.get("auth_token")
            if token and str(token).strip():
                return str(token).strip()
    except Exception:
        pass
    try:
        cfg_token = get_auth_token()
        if cfg_token and str(cfg_token).strip():
            return str(cfg_token).strip()
    except Exception:
        pass
    return None


def _sync_subject_into_store(subject: dict[str, Any]):
    """Sincroniza uma disciplina no store local."""
    sub_id = int(subject.get("id", 0))
    store = _get_store_list("subjects_store")
    for i, s in enumerate(store):
        if int(s.get("id", 0)) == sub_id:
            store[i] = subject
            return
    store.append(subject)


def _sync_task_into_store(task: dict[str, Any]):
    """Sincroniza uma tarefa no store local."""
    t_id = int(task.get("id", 0))
    store = _get_store_list("academic_tasks_store")
    for i, t in enumerate(store):
        if int(t.get("id", 0)) == t_id:
            store[i] = task
            return
    store.append(task)


# =============================================================================
# OPERAÇÕES DE DISCIPLINAS E PROFESSORES (subjects)
# =============================================================================


def get_subjects(token: str | None = None) -> list[dict[str, Any]]:
    """
    Retorna a lista de disciplinas ativas vinculadas ao usuário autenticado.
    Consulta GET /subjects no Xano quando autenticado,
    atribui paleta de cores para a UI e sincroniza o estado local.
    """
    init_tasks_store()
    resolved_token = _resolve_auth_token(token)

    if resolved_token and requests is not None:
        try:
            headers = {"Authorization": f"Bearer {resolved_token}", "Content-Type": "application/json"}
            resp = requests.get(f"{BASE_URL}/subjects", headers=headers, timeout=6)
            if resp.ok:
                data = resp.json()
                api_items = data if isinstance(data, list) else data.get("items", [])
                if isinstance(api_items, list) and len(api_items) > 0:
                    for idx, item in enumerate(api_items):
                        if not item.get("color"):
                            item["color"] = SUBJECT_PALETTE[idx % len(SUBJECT_PALETTE)]
                    _set_store_list("subjects_store", api_items)
                    return api_items
        except Exception:
            pass

    return _get_store_list("subjects_store")


def create_subject(
    name: str,
    teacher: str,
    hours: int,
    token: str | None = None,
) -> dict[str, Any]:
    """
    Cria uma nova matéria (subject) vinculada automaticamente ao usuário autenticado.
    Envia para POST /subjects no Xano, sincroniza o estado local e trata fallback.

    Regras de Negócio e Esquema:
    - name: text (Nome da disciplina, não vazio)
    - teacher: text (Nome do professor - ponto de ligação no contexto das matérias)
    - hours: int (Carga horária em horas > 0)
    - user_id: int (Atribuído automaticamente como auth.id no Xano)
    """
    init_tasks_store()

    # Validação rigorosa dos campos
    clean_name = str(name).strip() if name is not None else ""
    if not clean_name:
        raise ValueError("O nome da disciplina é obrigatório.")

    clean_teacher = str(teacher).strip() if teacher is not None else ""
    if not clean_teacher:
        raise ValueError("O nome do professor é obrigatório.")

    try:
        clean_hours = int(hours)
        if clean_hours <= 0:
            raise ValueError()
    except (TypeError, ValueError):
        raise ValueError("A carga horária deve ser um número inteiro positivo (horas > 0).")

    payload = {
        "name": clean_name,
        "teacher": clean_teacher,
        "hours": clean_hours,
    }

    resolved_token = _resolve_auth_token(token)
    created_subject: dict[str, Any] | None = None

    if resolved_token and requests is not None:
        try:
            headers = {
                "Authorization": f"Bearer {resolved_token}",
                "Content-Type": "application/json",
            }
            resp = requests.post(
                f"{BASE_URL}/subjects",
                headers=headers,
                json=payload,
                timeout=8,
            )
            if resp.ok:
                data = resp.json()
                if isinstance(data, dict) and "id" in data:
                    created_subject = dict(data)
            elif resp.status_code in (401, 403):
                try:
                    err_data = resp.json()
                    err_msg = err_data.get("message") or err_data.get("error") or "Acesso não autorizado no Xano."
                except Exception:
                    err_msg = resp.text or "Acesso negado no Xano."
                raise PermissionError(err_msg)
        except PermissionError:
            raise
        except Exception:
            # Em caso de falha de conexão/timeout, prossegue para fallback local
            pass

    if created_subject is None:
        # Fallback local com geração de id seguro
        store = _get_store_list("subjects_store")
        existing_ids = [int(s.get("id", 0)) for s in store if s.get("id") is not None]
        new_id = (max(existing_ids) + 1) if existing_ids else 1
        created_subject = {
            "id": new_id,
            **payload,
            "user_id": 1,
        }

    # Atribui cor para os cards visuais na UI
    if not created_subject.get("color"):
        store = _get_store_list("subjects_store")
        created_subject["color"] = SUBJECT_PALETTE[len(store) % len(SUBJECT_PALETTE)]

    # Sincroniza o estado local
    _sync_subject_into_store(created_subject)
    return created_subject


def delete_subject(subject_id: int, token: str | None = None) -> bool:
    """Remove uma matéria no Xano e no session_state."""
    init_tasks_store()
    resolved_token = _resolve_auth_token(token)
    int_id = int(subject_id)
    store = _get_store_list("subjects_store")
    before_len = len(store)
    filtered = [s for s in store if int(s.get("id", 0)) != int_id]
    _set_store_list("subjects_store", filtered)

    if resolved_token and len(filtered) < before_len and requests is not None:
        try:
            headers = {"Authorization": f"Bearer {resolved_token}"}
            requests.delete(f"{BASE_URL}/subjects/{int_id}", headers=headers, timeout=6)
        except Exception:
            pass

    return len(filtered) < before_len


# =============================================================================
# OPERAÇÕES DE OBRIGAÇÕES ACADÊMICAS (academic_tasks)
# =============================================================================


def get_tasks_by_subject(
    subject_id: int | None = None,
    token: str | None = None,
) -> list[dict[str, Any]]:
    """
    Retorna a lista de tarefas acadêmicas pertencentes ao usuário autenticado,
    opcionalmente filtrada por subject_id.
    Consulta GET /academic_tasks no Xano e sincroniza o estado local.
    """
    init_tasks_store()
    resolved_token = _resolve_auth_token(token)

    if resolved_token and requests is not None:
        try:
            headers = {"Authorization": f"Bearer {resolved_token}", "Content-Type": "application/json"}
            params = {}
            if subject_id is not None:
                params["subject_id"] = int(subject_id)

            endpoints = [f"{BASE_URL}/academic_tasks", f"{BASE_URL}/{TASKS_PATH}"]
            for ep in endpoints:
                resp = requests.get(ep, headers=headers, params=params, timeout=6)
                if resp.ok:
                    data = resp.json()
                    api_tasks = data if isinstance(data, list) else data.get("items", [])
                    if isinstance(api_tasks, list):
                        if subject_id is None:
                            _set_store_list("academic_tasks_store", api_tasks)
                        else:
                            current = _get_store_list("academic_tasks_store")
                            remaining = [t for t in current if int(t.get("subject_id", 0)) != int(subject_id)]
                            _set_store_list("academic_tasks_store", remaining + api_tasks)
                        return sorted(api_tasks, key=lambda x: str(x.get("due_date", "")))
        except Exception:
            pass

    # Fallback local
    tasks = list(_get_store_list("academic_tasks_store"))
    if subject_id is not None:
        tasks = [t for t in tasks if int(t.get("subject_id", 0)) == int(subject_id)]
    return sorted(tasks, key=lambda x: str(x.get("due_date", "")))


def create_task(
    title: str,
    description: str,
    due_date: str,
    status: str,
    subject_id: int,
    token: str | None = None,
) -> dict[str, Any]:
    """
    Cria uma nova obrigação acadêmica conforme o esquema da tabela academic_tasks:
    - title: text (obrigatório)
    - description: text (opcional)
    - due_date: date (AAAA-MM-DD, obrigatório)
    - status: text ('Pendente', 'Em Andamento', 'Concluído')
    - subject_id: int (FK para a tabela subjects)
    - user_id: int (vinculado automaticamente no backend como auth.id)

    Valida que a matéria pertence ao usuário autenticado antes do envio.
    Envia para POST /academic_tasks no Xano com Bearer token e sincroniza o estado local.
    """
    init_tasks_store()

    # Validação do título
    clean_title = str(title).strip() if title is not None else ""
    if not clean_title:
        raise ValueError("O título da obrigação acadêmica é obrigatório.")

    # Validação da data
    clean_due = str(due_date).strip() if due_date is not None else ""
    if not clean_due:
        raise ValueError("A data de entrega da obrigação acadêmica é obrigatória.")

    # Validação da disciplina
    if subject_id is None:
        raise ValueError("A disciplina vinculada (subject_id) é obrigatória.")

    try:
        int_subject_id = int(subject_id)
        if int_subject_id <= 0:
            raise ValueError()
    except (TypeError, ValueError):
        raise ValueError("O identificador da disciplina (subject_id) deve ser um número inteiro válido.")

    clean_status = str(status).strip() if status else "Pendente"
    clean_desc = str(description).strip() if description else ""

    resolved_token = _resolve_auth_token(token)

    # Validação de que a disciplina pertence ao usuário autenticado
    user_subjects = get_subjects(token=resolved_token)
    user_subject_ids = [int(s.get("id", 0)) for s in user_subjects if s.get("id") is not None]
    if user_subject_ids and int_subject_id not in user_subject_ids:
        raise ValueError(f"Acesso negado: a disciplina ID #{int_subject_id} não pertence ao usuário autenticado.")

    payload = {
        "title": clean_title,
        "description": clean_desc,
        "due_date": clean_due,
        "status": clean_status,
        "subject_id": int_subject_id,
    }

    created_task: dict[str, Any] | None = None

    if resolved_token and requests is not None:
        try:
            headers = {
                "Authorization": f"Bearer {resolved_token}",
                "Content-Type": "application/json",
            }
            endpoints = [f"{BASE_URL}/academic_tasks", f"{BASE_URL}/{TASKS_PATH}"]
            for ep in endpoints:
                resp = requests.post(ep, headers=headers, json=payload, timeout=8)
                if resp.ok:
                    data = resp.json()
                    if isinstance(data, dict) and "id" in data:
                        created_task = dict(data)
                        break
                elif resp.status_code in (401, 403):
                    try:
                        err_data = resp.json()
                        err_msg = err_data.get("message") or err_data.get("error") or "Acesso negado pelo backend."
                    except Exception:
                        err_msg = resp.text or "Acesso negado pelo backend."
                    raise PermissionError(err_msg)
        except PermissionError:
            raise
        except Exception:
            pass

    if created_task is None:
        store = _get_store_list("academic_tasks_store")
        existing_ids = [int(t.get("id", 0)) for t in store if t.get("id") is not None]
        new_id = (max(existing_ids) + 1) if existing_ids else 1
        created_task = {
            "id": new_id,
            **payload,
            "created_at": datetime.datetime.now().isoformat(),
        }

    _sync_task_into_store(created_task)
    return created_task


def update_task_status(task_id: int, new_status: str, token: str | None = None) -> bool:
    """Atualiza o status de uma obrigação acadêmica no Xano e localmente."""
    init_tasks_store()
    resolved_token = _resolve_auth_token(token)

    tasks = _get_store_list("academic_tasks_store")
    int_id = int(task_id)
    updated = False
    for task in tasks:
        if int(task.get("id", 0)) == int_id:
            task["status"] = str(new_status).strip()
            updated = True
            break

    if resolved_token and updated and requests is not None:
        try:
            headers = {"Authorization": f"Bearer {resolved_token}", "Content-Type": "application/json"}
            endpoints = [f"{BASE_URL}/academic_tasks/{int_id}", f"{BASE_URL}/{TASKS_PATH}/{int_id}"]
            for ep in endpoints:
                resp = requests.patch(ep, headers=headers, json={"status": str(new_status).strip()}, timeout=6)
                if resp.ok:
                    break
        except Exception:
            pass

    return updated


def delete_task(task_id: int, token: str | None = None) -> bool:
    """Remove uma obrigação acadêmica no Xano e localmente."""
    init_tasks_store()
    resolved_token = _resolve_auth_token(token)

    tasks = _get_store_list("academic_tasks_store")
    int_id = int(task_id)
    before_len = len(tasks)
    filtered = [t for t in tasks if int(t.get("id", 0)) != int_id]
    _set_store_list("academic_tasks_store", filtered)

    if resolved_token and len(filtered) < before_len and requests is not None:
        try:
            headers = {"Authorization": f"Bearer {resolved_token}"}
            endpoints = [f"{BASE_URL}/academic_tasks/{int_id}", f"{BASE_URL}/{TASKS_PATH}/{int_id}"]
            for ep in endpoints:
                resp = requests.delete(ep, headers=headers, timeout=6)
                if resp.ok:
                    break
        except Exception:
            pass

    return len(filtered) < before_len


def calculate_subject_progress(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    """Calcula estatísticas de tarefas e taxa percentual de conclusão."""
    total = len(tasks)
    if total == 0:
        return {"total": 0, "completed": 0, "pending": 0, "percent": 0.0}

    completed = sum(1 for t in tasks if str(t.get("status", "")).strip().lower() in ("concluído", "concluido", "done"))
    pending = total - completed
    percent = round((completed / total) * 100, 1)

    return {
        "total": total,
        "completed": completed,
        "pending": pending,
        "percent": percent,
    }
