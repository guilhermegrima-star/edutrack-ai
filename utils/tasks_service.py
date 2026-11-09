"""
utils/tasks_service.py
-----------------------
Serviço para gerenciamento de disciplinas e obrigações acadêmicas (academic_tasks).
Esquema da tarefa:
- id: int
- title: str (text)
- description: str (text)
- due_date: str (date AAAA-MM-DD)
- status: str (text: 'Pendente', 'Em Andamento', 'Concluído')
- subject_id: int (referência para tabela subjects)
- user_id: int (opcional, referenciando o usuário)
"""

from __future__ import annotations
import os
import datetime
from typing import Any
import streamlit as st
import requests

try:
    from utils.config import get_edutrack_base_url, get_tasks_path
    BASE_URL = get_edutrack_base_url()
    TASKS_PATH = get_tasks_path()
except ImportError:
    BASE_URL = os.environ.get("EDUTRACK_BASE_URL", "https://x8ki-letl-twmt.n7.xano.io/api:gTfD518O").rstrip("/")
    TASKS_PATH = os.environ.get("EDUTRACK_TASKS_PATH", "task").strip("/")

# Lista padrão de disciplinas do curso
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


def init_tasks_store():
    """Garante que a estrutura de armazenamento no session_state exista."""
    if "academic_tasks_store" not in st.session_state:
        st.session_state["academic_tasks_store"] = [dict(t) for t in INITIAL_TASKS]
    if "subjects_store" not in st.session_state:
        st.session_state["subjects_store"] = [dict(s) for s in DEFAULT_SUBJECTS]


def get_subjects(token: str | None = None) -> list[dict[str, Any]]:
    """Retorna lista de disciplinas ativas."""
    init_tasks_store()
    if token:
        try:
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            resp = requests.get(f"{BASE_URL}/subjects", headers=headers, timeout=5)
            if resp.ok:
                data = resp.json()
                api_items = data if isinstance(data, list) else data.get("items", [])
                if api_items:
                    # Mescla disciplinas da API com metadados locais (como cores)
                    return api_items
        except Exception:
            pass
    return st.session_state["subjects_store"]


def get_tasks_by_subject(subject_id: int | None = None, token: str | None = None) -> list[dict[str, Any]]:
    """Retorna a lista de tarefas, opcionalmente filtrada por subject_id."""
    init_tasks_store()
    tasks = list(st.session_state["academic_tasks_store"])
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
    Cria uma nova obrigação acadêmica conforme o esquema:
    title, description, due_date, status, subject_id.
    """
    init_tasks_store()
    existing_ids = [t.get("id", 0) for t in st.session_state["academic_tasks_store"]]
    new_id = (max(existing_ids) + 1) if existing_ids else 1

    new_task = {
        "id": new_id,
        "title": title.strip(),
        "description": description.strip(),
        "due_date": due_date,
        "status": status.strip(),
        "subject_id": int(subject_id),
    }

    # Tentativa de chamada à API Xano se token disponível
    if token:
        try:
            headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
            endpoints = [f"{BASE_URL}/academic_tasks", f"{BASE_URL}/{TASKS_PATH}"]
            for ep in endpoints:
                resp = requests.post(
                    ep,
                    headers=headers,
                    json={
                        "title": new_task["title"],
                        "description": new_task["description"],
                        "due_date": new_task["due_date"],
                        "status": new_task["status"],
                        "subject_id": new_task["subject_id"],
                    },
                    timeout=5,
                )
                if resp.ok:
                    data = resp.json()
                    if isinstance(data, dict) and "id" in data:
                        new_task["id"] = data["id"]
                    break
        except Exception:
            pass

    st.session_state["academic_tasks_store"].append(new_task)
    return new_task


def update_task_status(task_id: int, new_status: str, token: str | None = None) -> bool:
    """Atualiza o status de uma obrigação acadêmica."""
    init_tasks_store()
    for task in st.session_state["academic_tasks_store"]:
        if int(task.get("id", 0)) == int(task_id):
            task["status"] = new_status
            if token:
                try:
                    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
                    endpoints = [f"{BASE_URL}/academic_tasks/{task_id}", f"{BASE_URL}/{TASKS_PATH}/{task_id}"]
                    for ep in endpoints:
                        resp = requests.patch(ep, headers=headers, json={"status": new_status}, timeout=5)
                        if resp.ok:
                            break
                except Exception:
                    pass
            return True
    return False


def delete_task(task_id: int, token: str | None = None) -> bool:
    """Remove uma obrigação acadêmica."""
    init_tasks_store()
    before_len = len(st.session_state["academic_tasks_store"])
    st.session_state["academic_tasks_store"] = [
        t for t in st.session_state["academic_tasks_store"] if int(t.get("id", 0)) != int(task_id)
    ]
    if len(st.session_state["academic_tasks_store"]) < before_len:
        if token:
            try:
                headers = {"Authorization": f"Bearer {token}"}
                endpoints = [f"{BASE_URL}/academic_tasks/{task_id}", f"{BASE_URL}/{TASKS_PATH}/{task_id}"]
                for ep in endpoints:
                    resp = requests.delete(ep, headers=headers, timeout=5)
                    if resp.ok:
                        break
            except Exception:
                pass
        return True
    return False


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
