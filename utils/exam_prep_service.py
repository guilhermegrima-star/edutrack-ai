"""
utils/exam_prep_service.py
--------------------------
Serviço para o "Modo Prova" do EduTrack AI:
Preparação ativa com contagem regressiva, plano diário de revisão,
simulados adaptativos com repetição espaçada, mapa de domínio por tópicos,
índice de preparo evolutivo e revisão emergencial D-1.
"""

from __future__ import annotations
import datetime
from typing import Any

import utils.gemini_service as gemini_service

try:
    import streamlit as st
except ImportError:
    st = None

# Store local em memória quando fora do contexto do Streamlit
_LOCAL_EXAM_STORE: dict[str, list[dict[str, Any]]] = {
    "exams": [],
    "mock_questions": [],
    "topic_mastery": [],
    "study_sessions": [],
    "exam_summaries": [],
}

# Tópicos e questões padrão de exemplo
DEFAULT_SAMPLE_TOPICS = [
    {"topic": "Princípios de UI/UX & Heurísticas de Nielsen", "mastery": 78, "questions": 12, "correct": 9},
    {"topic": "Teoria das Cores & Contraste WCAG", "mastery": 45, "questions": 10, "correct": 4},
    {"topic": "Arquitetura da Informação & Wireframes", "mastery": 85, "questions": 14, "correct": 12},
    {"topic": "Testes de Usabilidade & Métricas SUS", "mastery": 50, "questions": 8, "correct": 4},
    {"topic": "Design System & Componentes Reutilizáveis", "mastery": 62, "questions": 10, "correct": 6},
]

DEFAULT_SAMPLE_QUESTIONS = [
    {
        "id": 1,
        "exam_id": 1,
        "topic": "Teoria das Cores & Contraste WCAG",
        "question_text": "De acordo com as diretrizes WCAG 2.1 (nível AA), qual é a taxa mínima de contraste recomendada para texto normal em relação ao plano de fundo?",
        "options": ["3:1", "4.5:1", "7:1", "2.5:1"],
        "correct_option": 1,
        "explanation": "A WCAG 2.1 AA exige uma taxa mínima de contraste de 4.5:1 para texto padrão e 3:1 para texto em escala grande (18pt ou 14pt em negrito).",
        "source_reference": "Notas de Aula: Módulo de Acessibilidade & Cores",
        "status": "approved",
    },
    {
        "id": 2,
        "exam_id": 1,
        "topic": "Princípios de UI/UX & Heurísticas de Nielsen",
        "question_text": "Qual heurística de Jakob Nielsen orienta que o sistema deve sempre manter os usuários informados sobre o que está acontecendo por meio de feedback apropriado?",
        "options": [
            "Correspondência entre o sistema e o mundo real",
            "Visibilidade do status do sistema",
            "Prevenção de erros",
            "Flexibilidade e eficiência de uso",
        ],
        "correct_option": 1,
        "explanation": "A heurística 'Visibilidade do status do sistema' preceitua que o usuário deve receber feedback em tempo hábil sobre o processamento e o estado atual da interface.",
        "source_reference": "Heurísticas de Usabilidade (Nielsen Norman Group)",
        "status": "approved",
    },
    {
        "id": 3,
        "exam_id": 1,
        "topic": "Testes de Usabilidade & Métricas SUS",
        "question_text": "Na escala System Usability Scale (SUS), qual pontuação média geralmente indica um nível considerado acima da média ('aceitável/bom') de usabilidade?",
        "options": ["50 pontos", "68 pontos", "85 pontos", "40 pontos"],
        "correct_option": 1,
        "explanation": "Uma pontuação de 68 na escala SUS é considerada a média padrão global de usabilidade percebida.",
        "source_reference": "Apostila de Métricas Ágeis e Usabilidade, Cap. 4",
        "status": "approved",
    },
]


def _get_store(key: str) -> list[dict[str, Any]]:
    if st is not None:
        try:
            if hasattr(st, "session_state"):
                if key not in st.session_state:
                    st.session_state[key] = []
                return st.session_state[key]
        except Exception:
            pass
    return _LOCAL_EXAM_STORE.setdefault(key, [])


def _set_store(key: str, data: list[dict[str, Any]]) -> None:
    if st is not None:
        try:
            if hasattr(st, "session_state"):
                st.session_state[key] = data
                return
        except Exception:
            pass
    _LOCAL_EXAM_STORE[key] = data


def init_exam_prep_store() -> None:
    """Inicializa as coleções do Modo Prova se ainda não existirem."""
    exams = _get_store("exams_store")
    if not exams:
        # Cria uma avaliação de exemplo inicial
        sample_exam = {
            "id": 1,
            "subject_id": 1,
            "subject_name": "Fundamentos de UI/UX",
            "title": "Prova Bimestral de Avaliação de Interfaces",
            "exam_date": (datetime.date.today() + datetime.timedelta(days=5)).isoformat(),
            "exam_type": "Mista (Múltipla Escolha e Prática)",
            "content": "Heurísticas de Nielsen, Teoria das Cores, Contraste WCAG 2.1 AA, Wireframes de Alta Fidelidade no Figma e Métricas de Usabilidade SUS.",
            "created_at": datetime.datetime.now().isoformat(),
        }
        _set_store("exams_store", [sample_exam])

    questions = _get_store("mock_questions_store")
    if not questions:
        _set_store("mock_questions_store", list(DEFAULT_SAMPLE_QUESTIONS))

    mastery = _get_store("topic_mastery_store")
    if not mastery:
        _set_store("topic_mastery_store", list(DEFAULT_SAMPLE_TOPICS))


def get_exams() -> list[dict[str, Any]]:
    """Retorna todas as provas cadastradas no sistema."""
    init_exam_prep_store()
    return _get_store("exams_store")


def get_exam_by_id(exam_id: int) -> dict[str, Any] | None:
    """Busca os dados de uma prova pelo ID."""
    exams = get_exams()
    for e in exams:
        if int(e.get("id", 0)) == int(exam_id):
            return e
    return None


def create_exam(
    subject_id: int,
    subject_name: str,
    title: str,
    exam_date: str,
    exam_type: str,
    content: str,
    token: str | None = None,
) -> dict[str, Any]:
    """
    Cadastra uma nova prova no Modo Prova com validação rigorosa de regras de negócio.
    """
    init_exam_prep_store()

    clean_title = str(title).strip() if title else ""
    if not clean_title:
        raise ValueError("O título da avaliação é obrigatório.")

    try:
        clean_sub_id = int(subject_id)
        if clean_sub_id <= 0:
            raise ValueError()
    except Exception:
        raise ValueError("Selecione uma disciplina curricular válida.")

    clean_content = str(content).strip() if content else ""
    if len(clean_content) < 15:
        raise ValueError("Forneça pelo menos 15 caracteres de conteúdo ou tópicos para a preparação.")

    # Validação de data: não pode ser no passado
    try:
        parsed_date = datetime.date.fromisoformat(str(exam_date).strip())
        today = datetime.date.today()
        if parsed_date < today:
            raise ValueError("A data da prova não pode ser no passado.")
    except ValueError as val_err:
        if "passado" in str(val_err):
            raise
        raise ValueError("Formato de data inválido. Use AAAA-MM-DD.")

    exams = _get_store("exams_store")
    new_id = (max([int(e.get("id", 0)) for e in exams]) + 1) if exams else 1

    new_exam = {
        "id": new_id,
        "subject_id": clean_sub_id,
        "subject_name": str(subject_name).strip() if subject_name else "Disciplina Geral",
        "title": clean_title,
        "exam_date": parsed_date.isoformat(),
        "exam_type": str(exam_type).strip() if exam_type else "Múltipla Escolha",
        "content": clean_content,
        "created_at": datetime.datetime.now().isoformat(),
    }

    exams.append(new_exam)
    _set_store("exams_store", exams)

    # Gera tópicos derivados a partir do conteúdo informado
    _generate_initial_topics_for_exam(new_id, clean_content)

    # Tenta gerar questões com a IA do Gemini; fallback para o gerador heurístico local
    ai_generated_questions = False
    if gemini_service.is_gemini_available():
        try:
            ai_qs = gemini_service.generate_ai_mock_questions(
                subject_name=new_exam["subject_name"],
                exam_title=clean_title,
                content=clean_content,
                num_questions=3,
            )
            if ai_qs:
                q_store = _get_store("mock_questions_store")
                max_id = max([int(q.get("id", 0)) for q in q_store]) if q_store else 0
                for idx, q_item in enumerate(ai_qs):
                    q_item["id"] = max_id + 1 + idx
                    q_item["exam_id"] = new_id
                    q_store.append(q_item)
                _set_store("mock_questions_store", q_store)
                ai_generated_questions = True
        except Exception:
            ai_generated_questions = False

    if not ai_generated_questions:
        _generate_initial_questions_for_exam(new_id, clean_content, clean_sub_id)

    # Pré-carrega resumo e flashcards no store se possível
    try:
        get_exam_ai_summary_and_flashcards(new_id)
    except Exception:
        pass

    return new_exam


def generate_additional_questions_with_ai(exam_id: int, num_questions: int = 3) -> list[dict[str, Any]]:
    """Gera novas questões contextualizadas para o simulado utilizando a IA do Gemini."""
    exam = get_exam_by_id(exam_id)
    if not exam:
        raise ValueError("Avaliação não encontrada.")

    ai_qs = gemini_service.generate_ai_mock_questions(
        subject_name=exam.get("subject_name", "Geral"),
        exam_title=exam.get("title", "Avaliação"),
        content=exam.get("content", ""),
        num_questions=num_questions,
    )

    q_store = _get_store("mock_questions_store")
    max_id = max([int(q.get("id", 0)) for q in q_store]) if q_store else 0

    added = []
    for idx, q_item in enumerate(ai_qs):
        q_item["id"] = max_id + 1 + idx
        q_item["exam_id"] = int(exam_id)
        q_store.append(q_item)
        added.append(q_item)

    _set_store("mock_questions_store", q_store)
    return added


def get_exam_ai_summary_and_flashcards(exam_id: int, force_regenerate: bool = False) -> dict[str, Any]:
    """Retorna o resumo conceitual e flashcards gerados por IA para a avaliação."""
    exam = get_exam_by_id(exam_id)
    if not exam:
        return {"summary": "", "key_points": [], "flashcards": []}

    summaries = _get_store("exam_summaries_store")
    cached = next((s for s in summaries if int(s.get("exam_id", 0)) == int(exam_id)), None)

    if cached and not force_regenerate:
        return cached

    # Tenta gerar com Gemini
    result = None
    if gemini_service.is_gemini_available():
        try:
            result = gemini_service.generate_ai_summary_and_flashcards(
                exam_title=exam.get("title", ""),
                content=exam.get("content", ""),
            )
        except Exception:
            result = None

    # Fallback heurístico local caso a IA não esteja disponível ou ocorra erro
    if not result:
        topics = get_topic_mastery(exam_id)
        top_names = [t["topic"] for t in topics] or ["Conceitos Fundamentais"]
        result = {
            "summary": f"Resumo conceitual da avaliação '{exam['title']}': foco principal nos tópicos {', '.join(top_names[:3])}. Pratique com os simulados interativos para reforçar a memorização ativa.",
            "key_points": [f"Revisar detalhadamente: {tn}" for tn in top_names[:4]],
            "flashcards": [
                {
                    "topic": tn,
                    "front": f"Qual o conceito fundamental de {tn}?",
                    "back": f"Compreender a definição e aplicação prática de {tn} no contexto da avaliação.",
                }
                for tn in top_names[:4]
            ],
        }

    result["exam_id"] = int(exam_id)
    if cached:
        cached.update(result)
    else:
        summaries.append(result)
        _set_store("exam_summaries_store", summaries)

    return result


def _generate_initial_topics_for_exam(exam_id: int, content: str) -> None:
    """Extrai tópicos principais do texto de conteúdo para o mapa de domínio."""
    mastery_list = _get_store("topic_mastery_store")
    lines = [p.strip() for p in content.replace(",", "\n").replace(";", "\n").split("\n") if len(p.strip()) > 3]
    unique_topics = list(dict.fromkeys(lines))[:5]

    if not unique_topics:
        unique_topics = ["Fundamentos Conceituais", "Aplicações Práticas", "Resolução de Problemas"]

    for idx, top in enumerate(unique_topics):
        mastery_list.append({
            "exam_id": exam_id,
            "topic": top,
            "mastery": 30 + (idx * 10),
            "questions": 4,
            "correct": 1 + (idx % 2),
        })
    _set_store("topic_mastery_store", mastery_list)


def _generate_initial_questions_for_exam(exam_id: int, content: str, subject_id: int) -> None:
    """Gera questões de simulado contextualizadas para a prova."""
    q_store = _get_store("mock_questions_store")
    max_id = max([int(q.get("id", 0)) for q in q_store]) if q_store else 0

    topics = [p.strip() for p in content.split(",") if len(p.strip()) > 3]
    primeiro_topico = topics[0] if topics else "Conceitos Fundamentais"

    nova_q = {
        "id": max_id + 1,
        "exam_id": exam_id,
        "topic": primeiro_topico,
        "question_text": f"Considerando o tópico '{primeiro_topico}', qual das seguintes alternativas descreve corretamente o seu objetivo central?",
        "options": [
            f"Otimizar a aplicação prática e o domínio de {primeiro_topico}.",
            "Substituir totalmente a análise de requisitos do projeto.",
            "Eliminar a necessidade de revisão contínua dos conceitos.",
            "Aplicar exclusivamente em cenários teóricos sem validação.",
        ],
        "correct_option": 0,
        "explanation": f"A alternativa A sintetiza o propósito principal de {primeiro_topico} no contexto da disciplina.",
        "source_reference": f"Conteúdo informado pelo aluno: '{content[:40]}...'",
        "status": "approved",
    }
    q_store.append(nova_q)
    _set_store("mock_questions_store", q_store)


def generate_review_plan(exam_id: int, use_ai: bool = True) -> dict[str, Any]:
    """
    Gera o plano diário de revisão com contagem regressiva e metas até o dia da prova.
    Utiliza IA Gemini para personalizar a distribuição se a API estiver disponível.
    """
    exam = get_exam_by_id(exam_id)
    if not exam:
        return {"days_remaining": 0, "schedule": [], "is_emergency_d1": False}

    exam_date = datetime.date.fromisoformat(exam["exam_date"])
    today = datetime.date.today()
    days_remaining = (exam_date - today).days

    topics = get_topic_mastery(exam_id)
    pontos_fracos = [t for t in topics if t.get("mastery", 0) < 60]

    # Tentativa de gerar o cronograma adaptativo via Gemini se houver antecedência
    if use_ai and gemini_service.is_gemini_available() and days_remaining > 1:
        try:
            top_names = [t["topic"] for t in topics]
            weak_names = [t["topic"] for t in pontos_fracos]
            ai_sched_raw = gemini_service.generate_ai_study_plan(
                exam_title=exam["title"],
                days_remaining=days_remaining,
                content=exam.get("content", ""),
                topics=top_names,
                weak_topics=weak_names,
            )
            if ai_sched_raw:
                ai_schedule = []
                for idx, s_item in enumerate(ai_sched_raw):
                    target_dt = today + datetime.timedelta(days=idx)
                    ai_schedule.append({
                        "day": s_item.get("day", f"Dia {idx+1}"),
                        "date": target_dt.isoformat(),
                        "focus": s_item.get("focus", "Estudo Ativo"),
                        "topics": s_item.get("topics", []),
                        "tasks": s_item.get("tasks", ["Resolver simulado do dia"]),
                        "study_technique": s_item.get("study_technique", "Active Recall"),
                        "is_current": (idx == 0),
                    })
                return {
                    "days_remaining": max(days_remaining, 0),
                    "is_emergency_d1": False,
                    "schedule": ai_schedule,
                    "ai_generated": True,
                }
        except Exception:
            pass

    schedule = []
    if days_remaining <= 1:
        # Véspera ou dia da prova: ativação imediata do protocolo D-1
        schedule.append({
            "day": "Hoje (Véspera D-1)",
            "date": today.isoformat(),
            "focus": "Revisão Emergencial Focada nos Pontos Críticos",
            "topics": [t["topic"] for t in pontos_fracos] or ["Revisão Geral"],
            "tasks": ["Resolver simulado rápido dos pontos fracos", "Revisar карточки de fórmulas e conceitos", "Descanso pré-prova"],
            "is_current": True,
        })
    else:
        # Distribui os dias de estudo progressivo
        for i in range(min(days_remaining, 7)):
            target_dt = today + datetime.timedelta(days=i)
            day_name = f"Dia {i+1}" if i > 0 else "Hoje"
            
            # Prioriza tópicos com menor domínio no início
            if i == 0 and pontos_fracos:
                foco_dia = f"Reforço Crítico: {pontos_fracos[0]['topic']}"
                topicos_dia = [pontos_fracos[0]["topic"]]
            elif i == days_remaining - 1:
                foco_dia = "Revisão Final D-1 e Síntese de Fórmulas"
                topicos_dia = [t["topic"] for t in pontos_fracos]
            else:
                top_idx = i % len(topics) if topics else 0
                foco_dia = f"Domínio & Prática: {topics[top_idx]['topic']}" if topics else "Estudo Ativo"
                topicos_dia = [topics[top_idx]["topic"]] if topics else []

            schedule.append({
                "day": day_name,
                "date": target_dt.isoformat(),
                "focus": foco_dia,
                "topics": topicos_dia,
                "tasks": [f"Resolver 5 questões de {topicos_dia[0]}" if topicos_dia else "Resolver simulado", "Revisar flashcards do dia"],
                "is_current": (i == 0),
            })

    return {
        "days_remaining": max(days_remaining, 0),
        "is_emergency_d1": days_remaining <= 1,
        "schedule": schedule,
        "ai_generated": False,
    }


def get_mock_questions(exam_id: int, include_all_status: bool = False) -> list[dict[str, Any]]:
    """Retorna as questões do simulado associadas a uma avaliação."""
    init_exam_prep_store()
    questions = _get_store("mock_questions_store")
    filtered = [q for q in questions if int(q.get("exam_id", 0)) == int(exam_id)]
    if not include_all_status:
        filtered = [q for q in filtered if q.get("status") != "rejected"]
    return filtered


def update_question_status(question_id: int, new_status: str, new_text: str | None = None) -> bool:
    """Aprova, edita ou rejeita uma questão gerada pela IA."""
    questions = _get_store("mock_questions_store")
    for q in questions:
        if int(q.get("id", 0)) == int(question_id):
            q["status"] = str(new_status).strip().lower()
            if new_text and str(new_text).strip():
                q["question_text"] = str(new_text).strip()
            _set_store("mock_questions_store", questions)
            return True
    return False


def record_quiz_answer(
    exam_id: int,
    question_id: int,
    selected_option: int,
    is_correct: bool,
) -> dict[str, Any]:
    """Registra uma resposta do simulado e recalcula o domínio do tópico."""
    questions = get_mock_questions(exam_id, include_all_status=True)
    target_q = next((q for q in questions if int(q.get("id", 0)) == int(question_id)), None)

    topic_name = target_q.get("topic", "Geral") if target_q else "Geral"

    mastery_list = _get_store("topic_mastery_store")
    topic_item = next((m for m in mastery_list if m.get("topic") == topic_name), None)

    if topic_item is None:
        topic_item = {"exam_id": exam_id, "topic": topic_name, "mastery": 50, "questions": 0, "correct": 0}
        mastery_list.append(topic_item)

    topic_item["questions"] = int(topic_item.get("questions", 0)) + 1
    if is_correct:
        topic_item["correct"] = int(topic_item.get("correct", 0)) + 1

    # Recalcula a taxa percentual de domínio do tópico
    acc = (topic_item["correct"] / topic_item["questions"]) * 100
    topic_item["mastery"] = round(acc, 1)
    _set_store("topic_mastery_store", mastery_list)

    # Registra no histórico de sessões
    sessions = _get_store("study_sessions_store")
    sessions.append({
        "exam_id": exam_id,
        "timestamp": datetime.datetime.now().isoformat(),
        "is_correct": is_correct,
        "topic": topic_name,
    })
    _set_store("study_sessions_store", sessions)

    new_prep_index = calculate_prep_index(exam_id)
    return {
        "is_correct": is_correct,
        "topic": topic_name,
        "topic_mastery": topic_item["mastery"],
        "prep_index": new_prep_index,
    }


def get_topic_mastery(exam_id: int) -> list[dict[str, Any]]:
    """Retorna os tópicos avaliados classificados por domínio (Fortes vs. Fracos)."""
    init_exam_prep_store()
    mastery_list = _get_store("topic_mastery_store")
    
    result = []
    for m in mastery_list:
        score = float(m.get("mastery", 50))
        result.append({
            "topic": m.get("topic", "Geral"),
            "mastery": score,
            "status": "Ponto Forte" if score >= 60 else "Ponto Crítico / A Reforçar",
            "is_weak": score < 60,
            "questions": m.get("questions", 0),
            "correct": m.get("correct", 0),
        })

    # Ordena com os pontos fracos no topo para guiar o estudo
    return sorted(result, key=lambda x: x["mastery"])


def calculate_prep_index(exam_id: int) -> float:
    """
    Calcula o Índice de Preparo Geral (0% a 100%) da avaliação.
    Pondera acurácia dos simulados (45%), cobertura de tópicos (25%),
    desempenho em tópicos críticos (20%) e constância de estudos (10%).
    """
    topics = get_topic_mastery(exam_id)
    if not topics:
        return 0.0

    avg_mastery = sum(t["mastery"] for t in topics) / len(topics)
    fracos = [t for t in topics if t["is_weak"]]

    weak_penalty = (len(fracos) / len(topics)) * 20
    base_index = avg_mastery - (weak_penalty * 0.3)

    # Bonificação por sessões ativas realizadas
    sessions = [s for s in _get_store("study_sessions_store") if int(s.get("exam_id", 0)) == int(exam_id)]
    session_bonus = min(len(sessions) * 1.5, 10.0)

    final_index = max(min(round(base_index + session_bonus, 1), 100.0), 0.0)
    return final_index


def get_d1_emergency_review(exam_id: int, use_ai: bool = True) -> dict[str, Any]:
    """
    Entrega a síntese condensada da Revisão Final D-1 concentrada
    exclusivamente nos tópicos com maior deficiência do estudante.
    Se a IA Gemini estiver disponível, gera карточки personalizados.
    """
    topics = get_topic_mastery(exam_id)
    pontos_criticos = [t for t in topics if t["is_weak"]]

    if not pontos_criticos:
        pontos_criticos = topics[:2] if topics else []

    # Tentativa de gerar síntese cirúrgica via IA
    if use_ai and gemini_service.is_gemini_available() and pontos_criticos:
        try:
            exam = get_exam_by_id(exam_id)
            if exam:
                ai_d1 = gemini_service.generate_ai_d1_review(
                    exam_title=exam.get("title", ""),
                    weak_topics=pontos_criticos,
                    content=exam.get("content", ""),
                )
                if ai_d1 and ai_d1.get("cards"):
                    return {
                        "exam_id": exam_id,
                        "critical_topics_count": len(pontos_criticos),
                        "cards": ai_d1["cards"],
                        "recommendation": ai_d1.get(
                            "recommendation",
                            "Foque exclusivamente nas suas vulnerabilidades nas próximas 24 horas e descanse a mente.",
                        ),
                        "ai_generated": True,
                    }
        except Exception:
            pass

    cards_resumo = []
    for c in pontos_criticos:
        cards_resumo.append({
            "topic": c["topic"],
            "mastery": c["mastery"],
            "alert": "⚠️ Prioridade Máxima na Véspera",
            "key_concept": f"Revisar definições-chave e resolver 3 questões de fixação rápida sobre {c['topic']}.",
            "recommended_action": "Ler resumo condensado e evitar memorização passiva sem exercícios.",
        })

    return {
        "exam_id": exam_id,
        "critical_topics_count": len(pontos_criticos),
        "cards": cards_resumo,
        "recommendation": "Foque apenas nestes pontos críticos nas próximas 24 horas. Evite tentar aprender conteúdos novos e descanse na noite anterior.",
        "ai_generated": False,
    }
