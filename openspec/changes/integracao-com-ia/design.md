# Design: Integração com IA (Google Gemini) no Modo Prova

## Context
O EduTrack AI possui o "Modo Prova" implementado em `utils/exam_prep_service.py` e apresentado na navegação principal do Streamlit (`app.py`). Essa funcionalidade já cobre:
- Cadastro de avaliações com validação de datas e ementa mínima.
- Contagem regressiva em dias.
- Cálculo de Índice de Preparo (0 a 100%) e mapa de domínio por tópicos.
- Simulado interativo com aprovação, edição e descarte de questões.
- Revisão emergencial D-1 focada em pontos vulneráveis.

Atualmente, toda a geração de tópicos, questões e cronogramas é estática ou baseada em templates e heurísticas simples. Para que o Modo Prova se torne um assistente de estudos dinâmico e personalizado, é necessária a integração com um modelo de linguagem de ponta: o **Google Gemini** (usando preferencialmente `gemini-1.5-flash` devido ao equilíbrio entre velocidade, inteligência de raciocínio pedagógico e custos/cotas).

## Goals / Non-Goals

**Goals:**
- **Módulo Dedicado (`utils/gemini_service.py`)**: Centralizar todas as interações com a API do Google Gemini, evitando espalhar prompts ou lógica de requisição HTTP pelo código.
- **Formato Estruturado (JSON)**: Garantir que a IA retorne dados diretamente serializáveis em dicionários Python (questões, cronogramas, resumos, flashcards e revisão D-1).
- **Fallback Transparente e Resiliente**: Garantir que a ausência da chave `GEMINI_API_KEY` ou qualquer instabilidade na API (timeout, quota 429, payload inválido) nunca quebre o fluxo da aplicação; o sistema deve recorrer silenciosamente aos geradores locais.
- **Configuração Segura e Padrão Streamlit**: Centralizar a leitura da chave de API em `utils/config.py`, priorizando `st.secrets["GEMINI_API_KEY"]` conforme as diretrizes do projeto (`STREAMLIT_SECRETS.md`).
- **Aprimoramento da Interface Streamlit (`app.py`)**: Exibir indicador visual do estado da IA, botão para regenerar questões via IA, nova aba ou bloco para **Resumos & Flashcards**, e orientações claras sobre como cadastrar a chave.

**Non-Goals:**
- Suporte a upload e processamento de arquivos multimídia pesados (vídeos/áudios) ou modelos locais pesados (Ollama/Llama local) nesta iteração.
- Substituir o controle humano do estudante (o estudante continua podendo aprovar, editar ou rejeitar o que a IA produzir).

## Architecture & Data Flow

```
┌────────────────────────────────────────────────────────┐
│                   Streamlit UI (app.py)                │
│   - Indicador de Status Gemini (Ativo / Offline)       │
│   - Botões de Geração / Regeneração com IA             │
│   - Exibição de Simulados, Flashcards, D-1 e Resumos   │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│             utils/exam_prep_service.py                 │
│   - Orquestrador de Provas, Domínio e Sessões          │
│   - Fallback Heurístico Local Garantido                │
└──────────────┬───────────────────────────┬─────────────┘
               │                           │
               ▼ (Chave ativa)             ▼ (Sem chave ou erro)
┌──────────────────────────────┐  ┌───────────────────────┐
│   utils/gemini_service.py    │  │  Geradores Locais     │
│   - Prompts Pedagógicos      │  │  - Templates Padrão   │
│   - REST API v1beta Gemini   │  │  - Cálculo Heurístico │
│   - Parser JSON Defensivo    │  └───────────────────────┘
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│       utils/config.py        │
│   - get_gemini_api_key()     │
│   - st.secrets / env var     │
└──────────────────────────────┘
```

## Decisions

### 1. Cliente HTTP REST vs SDK Externo
- **Decisão:** Utilizar chamadas HTTP REST diretas via biblioteca `requests` para o endpoint oficial da Google Gemini API (`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=...`), com suporte opcional a `google-genai` se instalado.
- **Justificativa:** A biblioteca `requests==2.34.2` já é dependência principal e testada no projeto. O uso de chamadas REST elimina conflitos de dependências adicionais no ambiente do Streamlit e garante controle absoluto sobre timeouts (ex: 10 segundos) e tratamento de códigos de erro HTTP (ex: 400, 401, 403, 429).

### 2. Formato de Resposta Estruturado via Prompts de Sistema
- **Decisão:** Os prompts instruirão o modelo a responder estritamente no formato JSON (incluindo diretiva `generationConfig: {"response_mime_type": "application/json"}`).
- Adicionalmente, o parser em `utils/gemini_service.py` conterá um extrator defensivo de blocos de código (ex: removendo marcações de markdown ```json ... ``` se o modelo as incluir) e tratamento com `json.loads`.

### 3. Estratégia de Fallback e Degradação Graciosa
- **Decisão:** Cada função do `gemini_service` retorna `None` ou levanta uma exceção tratada caso a chave não esteja disponível ou a requisição falhe.
- O serviço `exam_prep_service.py` envolve as chamadas à IA em blocos `try/except`:
  - Se a IA responder com sucesso, os dados estruturados ricos são injetados no store.
  - Se a IA falhar ou a chave estiver ausente, os métodos heurísticos locais (`_generate_initial_topics_for_exam`, `_generate_initial_questions_for_exam`, etc.) entram em ação instantaneamente.

### 4. Resolução da Chave da API Gemini
- **Decisão:** A chave da API é recuperada por meio de `utils/config.get_gemini_api_key()`, seguindo rigorosamente a ordem:
  1. `st.secrets["GEMINI_API_KEY"]`
  2. `st.secrets.get("gemini", {}).get("api_key")`
  3. `os.environ.get("GEMINI_API_KEY")`
  4. Leitura direta de `.streamlit/secrets.toml`
  5. Leitura de `.env`
- O template `.streamlit/secrets.toml.example` conterá a entrada comentada:
  ```toml
  # Chave da API do Google Gemini para recursos de IA no Modo Prova
  GEMINI_API_KEY = "sua_chave_gemini_aqui"
  ```

### 5. Apresentação Visual no Streamlit (`app.py`)
- Na aba "Minhas Matérias" e "Modo Prova", um badge superior exibe:
  - 🟢 `✨ IA Gemini Conectada (gemini-1.5-flash)` quando a chave for válida.
  - ⚪ `⚙️ Modo Local (Cadastre GEMINI_API_KEY em secrets.toml para ativar a IA)` quando ausente.
- Na aba de simulados: botão "🔄 Gerar mais questões com IA".
- Nova subseção ou aba na visualização da prova: **"📚 Resumos & Flashcards com IA"**.

## Risks / Trade-offs

| Risco | Impacto | Mitigação |
|---|---|---|
| Chave não informada pelo usuário | Nenhuma questão ou cronograma gerado | Fallback automático para os geradores locais existentes; a aplicação continua 100% funcional. |
| Rate Limit (HTTP 429) do tier gratuito da Gemini API | Erro durante a geração | Detecção de status 429 com aviso amigável ao aluno e ativação automática do plano heurístico. |
| Modelo retornar texto em formato JSON malformado | Erro de decodificação (`JSONDecodeError`) | Pré-processamento com regex para extração do objeto JSON e fallback limpo em caso de parsing inválido. |
| Latência na chamada da IA no Streamlit | Sensação de lentidão no app | Uso de `st.spinner(...)` com mensagens interativas e timeout de 10s nas requisições. |

## Test Strategy
1. **Testes Unitários sem Rede (`tests/test_gemini_service.py`)**:
   - Teste de resolução de chave via variáveis e secrets.
   - Teste com mock de `requests.post` simulando retorno bem-sucedido de questões em JSON.
   - Teste com mock simulando erro 429 e 401, garantindo que o serviço trate adequadamente.
   - Teste do extrator de JSON defensivo contra respostas com tags markdown.
2. **Testes de Integração e Regressão (`tests/test_exam_prep_service.py`)**:
   - Garantir que todas as rotinas existentes de `create_exam`, `generate_review_plan`, `calculate_prep_index` e `get_d1_emergency_review` continuem funcionando sem falhas, tanto com IA ativada (mockada) quanto sem chave de IA.
