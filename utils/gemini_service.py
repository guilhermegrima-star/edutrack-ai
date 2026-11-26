"""
utils/gemini_service.py
-----------------------
Serviço centralizado de inteligência artificial generativa via Google Gemini.
Provê cliente REST resiliente, geração de simulados adaptativos, cronogramas
inteligentes, resumos conceituais, flashcards e revisão emergencial D-1.
"""

from __future__ import annotations

import json
import re
from typing import Any
import requests

from utils.config import get_gemini_api_key

GEMINI_API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
DEFAULT_MODEL = "gemini-3.5-flash-lite"
FALLBACK_MODELS = [
    "gemini-3.5-flash-lite",
    "gemini-3.8-flash",
    "gemini-3.5-flash",
    "gemini-flash-latest",
]


def is_gemini_available() -> bool:

    """Verifica se a chave da API do Google Gemini está configurada."""
    key = get_gemini_api_key()
    return bool(key and len(key.strip()) > 5)


def clean_json_response(raw_text: str) -> str:
    """
    Higieniza a resposta da IA, extraindo o bloco JSON caso venha encapsulado
    em marcações de código markdown (```json ... ```).
    """
    if not raw_text or not isinstance(raw_text, str):
        return ""

    cleaned = raw_text.strip()

    # Procura por blocos de markdown ```json ... ``` ou ``` ... ```
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", cleaned)
    if match:
        cleaned = match.group(1).strip()

    # Remove possíveis caracteres invisíveis ou prefixos antes da primeira chave ou colchete
    start_bracket = cleaned.find("[")
    start_brace = cleaned.find("{")

    if start_bracket != -1 and (start_brace == -1 or start_bracket < start_brace):
        end_bracket = cleaned.rfind("]")
        if end_bracket != -1:
            cleaned = cleaned[start_bracket : end_bracket + 1]
    elif start_brace != -1:
        end_brace = cleaned.rfind("}")
        if end_brace != -1:
            cleaned = cleaned[start_brace : end_brace + 1]

    return cleaned


def call_gemini_api(
    prompt: str,
    system_instruction: str = "",
    model: str = DEFAULT_MODEL,
    temperature: float = 0.2,
    timeout: int = 15,
) -> str:
    """
    Executa chamada HTTP REST à API do Google Gemini com fallback automático
    entre modelos compatíveis (ex: gemini-3.5-flash-lite, gemini-3.8-flash).
    Levanta exceções tratáveis em caso de chave ausente, rate limit ou timeout.
    """
    api_key = get_gemini_api_key()
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY não configurada. Defina a chave em .streamlit/secrets.toml ou no ambiente."
        )

    models_to_try = [model]
    for fb in FALLBACK_MODELS:
        if fb not in models_to_try:
            models_to_try.append(fb)

    payload: dict[str, Any] = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}],
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": temperature,
        },
    }

    if system_instruction:
        payload["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }

    headers = {"Content-Type": "application/json"}
    last_error: Exception | None = None

    for current_model in models_to_try:
        endpoint = f"{GEMINI_API_BASE_URL}/{current_model}:generateContent?key={api_key}"
        try:
            response = requests.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=timeout,
            )
        except requests.exceptions.Timeout:
            last_error = TimeoutError(f"Tempo limite esgotado com o modelo {current_model}.")
            continue
        except requests.exceptions.RequestException as req_err:
            last_error = ConnectionError(f"Erro de conexão com o modelo {current_model}: {req_err}")
            continue

        if response.status_code == 200:
            data = response.json()
            candidates = data.get("candidates", [])
            if candidates:
                first_part = candidates[0].get("content", {}).get("parts", [{}])[0]
                raw_text = first_part.get("text", "")
                if raw_text:
                    return raw_text
        elif response.status_code in (401, 403):
            raise PermissionError("Chave de API do Gemini inválida ou sem permissão de acesso.")
        elif response.status_code in (404, 503):
            # Modelo não encontrado ou pico de demanda temporária (503): tenta próximo da lista
            last_error = RuntimeError(f"Modelo {current_model} indisponível (HTTP {response.status_code}).")
            continue
        elif response.status_code == 429:
            raise RuntimeError("Limite de requisições da API Gemini excedido (Rate Limit / Quota 429).")
        else:
            last_error = RuntimeError(f"Erro {response.status_code} na API do Gemini: {response.text[:200]}")

    if last_error:
        raise last_error
    raise RuntimeError("Falha ao comunicar com os modelos do Gemini.")



def generate_ai_mock_questions(
    subject_name: str,
    exam_title: str,
    content: str,
    num_questions: int = 3,
) -> list[dict[str, Any]]:
    """
    Gera questões de múltipla escolha contextualizadas utilizando a IA do Gemini.
    Retorna uma lista de questões com opções, gabarito e explicação fundamentada.
    """
    system_instruction = (
        "Você é um professor universitário e especialista em avaliação educacional ativa. "
        "Seu papel é criar questões avaliativas desafiadoras, didáticas e contextualizadas, "
        "com distratores plausíveis e explicações completas. "
        "Sua resposta deve ser ESTRITAMENTE um array JSON contendo os objetos de questão."
    )

    prompt = f"""
Crie {num_questions} questões de múltipla escolha para a avaliação:
Disciplina: {subject_name}
Título da Prova: {exam_title}
Conteúdo Programático / Ementa:
\"\"\"{content}\"\"\"

Para cada questão, retorne um objeto com a seguinte estrutura estrita:
[
  {{
    "topic": "Nome do tópico específico",
    "question_text": "Enunciado contextualizado e claro",
    "options": [
      "Opção A",
      "Opção B",
      "Opção C",
      "Opção D"
    ],
    "correct_option": 0,
    "explanation": "Explicação pedagógica detalhando por que a resposta é correta e refutando os distratores",
    "source_reference": "Trecho ou conceito base informado na ementa"
  }}
]
Importante: O campo correct_option deve ser um número inteiro de 0 a 3 indicando o índice da alternativa correta.
"""

    raw_response = call_gemini_api(prompt, system_instruction=system_instruction)
    cleaned = clean_json_response(raw_response)
    data = json.loads(cleaned)

    if not isinstance(data, list):
        raise ValueError("O formato retornado pela IA não é uma lista de questões.")

    valid_questions = []
    for item in data:
        if (
            isinstance(item, dict)
            and "question_text" in item
            and isinstance(item.get("options"), list)
            and len(item["options"]) >= 2
            and "correct_option" in item
        ):
            corr = int(item["correct_option"])
            if 0 <= corr < len(item["options"]):
                valid_questions.append({
                    "topic": str(item.get("topic", "Geral")).strip(),
                    "question_text": str(item["question_text"]).strip(),
                    "options": [str(opt).strip() for opt in item["options"]],
                    "correct_option": corr,
                    "explanation": str(item.get("explanation", "")).strip(),
                    "source_reference": str(item.get("source_reference", f"Ementa de {subject_name}")).strip(),
                    "status": "approved",
                })

    if not valid_questions:
        raise ValueError("Nenhuma questão válida pôde ser estruturada a partir da resposta da IA.")

    return valid_questions


def generate_ai_study_plan(
    exam_title: str,
    days_remaining: int,
    content: str,
    topics: list[str],
    weak_topics: list[str] | None = None,
) -> list[dict[str, Any]]:
    """
    Gera um plano de estudo diário inteligente adaptado à quantidade de dias
    até a data da avaliação, priorizando os pontos fracos do estudante.
    """
    system_instruction = (
        "Você é um orientador de aprendizagem e neurociência da educação. "
        "Crie cronogramas diários práticos com metas ativas de estudo (Feynman, Active Recall, simulados)."
        "Sua resposta deve ser ESTRITAMENTE um array JSON contendo os dias do plano."
    )

    weak_str = ", ".join(weak_topics) if weak_topics else "Nenhum ponto fraco crítico registrado"
    top_str = ", ".join(topics) if topics else content[:200]

    prompt = f"""
Crie um plano diário de estudos até a prova \"{exam_title}\".
Dias restantes: {days_remaining} dias.
Tópicos abordados: {top_str}
Tópicos prioritários / vulneráveis (Pontos Fracos do Aluno): {weak_str}
Conteúdo base:
\"\"\"{content}\"\"\"

Retorne uma lista JSON com até 7 dias planejados na seguinte estrutura:
[
  {{
    "day": "Dia 1" ou "Hoje",
    "focus": "Foco principal do dia (ex: Reforço de Conceitos Críticos)",
    "topics": ["Tópico 1", "Tópico 2"],
    "tasks": ["Resolver 5 questões de Tópico 1", "Elaborar mapa mental", "Revisar flashcards"],
    "study_technique": "Técnica recomendada (ex: Active Recall, Técnica de Feynman, Pomodoro)"
  }}
]
"""

    raw_response = call_gemini_api(prompt, system_instruction=system_instruction)
    cleaned = clean_json_response(raw_response)
    data = json.loads(cleaned)

    if not isinstance(data, list):
        raise ValueError("O formato do cronograma gerado pela IA não é uma lista.")

    valid_schedule = []
    for item in data:
        if isinstance(item, dict) and "focus" in item and "tasks" in item:
            valid_schedule.append({
                "day": str(item.get("day", f"Dia {len(valid_schedule)+1}")).strip(),
                "focus": str(item.get("focus", "Estudo Ativo")).strip(),
                "topics": [str(t).strip() for t in item.get("topics", []) if str(t).strip()],
                "tasks": [str(t).strip() for t in item.get("tasks", []) if str(t).strip()],
                "study_technique": str(item.get("study_technique", "Active Recall")).strip(),
            })

    if not valid_schedule:
        raise ValueError("Não foi possível processar os dias do cronograma.")

    return valid_schedule


def generate_ai_summary_and_flashcards(
    exam_title: str,
    content: str,
) -> dict[str, Any]:
    """
    Gera um resumo executivo estruturado e pares de flashcards (pergunta e resposta)
    a partir do conteúdo programático da prova.
    """
    system_instruction = (
        "Você é um tutor acadêmico especialista em sintetizar matérias complexas em resumos "
        "executivos e cartões de memorização espaçada (Flashcards). "
        "Sua resposta deve ser ESTRITAMENTE um objeto JSON."
    )

    prompt = f"""
Analise o conteúdo programático da avaliação \"{exam_title}\" e gere um resumo estruturado e flashcards de memorização.
Conteúdo:
\"\"\"{content}\"\"\"

Retorne um objeto JSON na seguinte estrutura exata:
{{
  "summary": "Resumo executivo de 2 a 3 parágrafos condensando a essência da matéria...",
  "key_points": [
    "Ponto-chave essencial 1",
    "Ponto-chave essencial 2",
    "Ponto-chave essencial 3"
  ],
  "flashcards": [
    {{
      "topic": "Nome do tópico",
      "front": "Pergunta provocativa ou conceito para testar memorização ativa?",
      "back": "Resposta clara, objetiva e completa"
    }}
  ]
}}
Gere entre 4 a 6 flashcards de alto impacto.
"""

    raw_response = call_gemini_api(prompt, system_instruction=system_instruction)
    cleaned = clean_json_response(raw_response)
    data = json.loads(cleaned)

    if not isinstance(data, dict):
        raise ValueError("O resumo e flashcards gerados pela IA não possuem estrutura de dicionário.")

    summary_text = str(data.get("summary", "")).strip()
    key_points = [str(k).strip() for k in data.get("key_points", []) if str(k).strip()]
    flashcards_raw = data.get("flashcards", [])

    valid_flashcards = []
    for fc in flashcards_raw:
        if isinstance(fc, dict) and "front" in fc and "back" in fc:
            valid_flashcards.append({
                "topic": str(fc.get("topic", "Geral")).strip(),
                "front": str(fc["front"]).strip(),
                "back": str(fc["back"]).strip(),
            })

    return {
        "summary": summary_text,
        "key_points": key_points,
        "flashcards": valid_flashcards,
    }


def generate_ai_d1_review(
    exam_title: str,
    weak_topics: list[dict[str, Any]],
    content: str,
) -> dict[str, Any]:
    """
    Gera síntese emergencial para a véspera da avaliação (D-1), focando
    estritamente nos pontos onde o estudante apresentou menor domínio.
    """
    system_instruction = (
        "Você é um mentor especialista em reta final de preparação para provas. "
        "Foque exclusivamente nas deficiências do aluno e entregue dicas cirúrgicas, "
        "fórmulas indispensáveis, macetes e avisos contra pegadinhas de banca. "
        "Sua resposta deve ser ESTRITAMENTE um objeto JSON."
    )

    weak_summary = "\n".join([
        f"- {t.get('topic', 'Geral')}: Domínio atual {t.get('mastery', 50)}%"
        for t in weak_topics
    ])

    prompt = f"""
A prova \"{exam_title}\" é amanhã!
O aluno possui baixo domínio nos seguintes tópicos prioritários:
{weak_summary}

Conteúdo original:
\"\"\"{content}\"\"\"

Retorne um objeto JSON com a seguinte estrutura para cada tópico vulnerável:
{{
  "recommendation": "Mensagem motivacional e estratégica de reta final com orientação de descanso cognitivo.",
  "cards": [
    {{
      "topic": "Nome do tópico vulnerável",
      "mastery": 45,
      "alert": "Alerta de Risco Máximo",
      "key_concept": "Definição cirúrgica e o que mais costuma ser cobrado em provas",
      "recommended_action": "O que revisar e qual exercício rápido resolver nas próximas 2 horas",
      "formula_or_mnemonic": "Mnemônico, fórmula ou regra prática para não errar"
    }}
  ]
}}
"""

    raw_response = call_gemini_api(prompt, system_instruction=system_instruction)
    cleaned = clean_json_response(raw_response)
    data = json.loads(cleaned)

    if not isinstance(data, dict):
        raise ValueError("A síntese D-1 retornada pela IA não possui formato de dicionário.")

    cards_raw = data.get("cards", [])
    valid_cards = []
    for c in cards_raw:
        if isinstance(c, dict) and "topic" in c and "key_concept" in c:
            valid_cards.append({
                "topic": str(c["topic"]).strip(),
                "mastery": float(c.get("mastery", 45)),
                "alert": str(c.get("alert", "Revisão Prioritária D-1")).strip(),
                "key_concept": str(c["key_concept"]).strip(),
                "recommended_action": str(c.get("recommended_action", "Revisar resumo rápido")).strip(),
                "formula_or_mnemonic": str(c.get("formula_or_mnemonic", "")).strip(),
            })

    return {
        "recommendation": str(data.get("recommendation", "Foque nos tópicos críticos e priorize uma boa noite de sono.")).strip(),
        "cards": valid_cards,
    }
