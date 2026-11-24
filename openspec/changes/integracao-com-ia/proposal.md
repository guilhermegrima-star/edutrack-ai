# Proposal: Integração com IA (Google Gemini) no Modo Prova

## Why
O **Modo Prova** do EduTrack AI consolidou uma estrutura robusta de preparação ativa para avaliações, incluindo contagem regressiva, planos diários de estudo, simulados com aprovação/edição/rejeição de questões, índice de preparo (0-100%) e revisão emergencial D-1.

No entanto, atualmente a geração de simulados, cronogramas e sínteses depende de geradores heurísticos e templates pré-definidos (`utils/exam_prep_service.py`), o que limita a profundidade, a variedade e a personalização dos materiais de estudo gerados a partir do conteúdo programático inserido pelo estudante.

A integração com a **API do Google Gemini** eleva o Modo Prova a um novo patamar pedagógico:
1. **Geração Realista de Questões e Simulados**: Produção de itens contextualizados, com distratores plausíveis, explicações detalhadas por alternativa e indicação da fundamentação no material.
2. **Cronogramas Dinâmicos Inteligentes**: Criação de planos de estudos adaptados ao número real de dias restantes até a prova, distribuindo tópicos por relevância e complexidade com técnicas ativas de estudo (Active Recall, Feynman, Pomodoro).
3. **Resumos e Flashcards Automatizados**: Extração automática de sínteses conceituais, conceitos-chave e карточки de repetição espaçada.
4. **Síntese Emergencial D-1 com IA**: Produção de um resumo direcionado exclusivamente para os pontos de menor domínio histórico do aluno (< 60%), com macetes de prova, fórmulas indispensáveis e alertas contra armadilhas conceituais.
5. **Resiliência e Fallback Transparente**: Arquitetura desacoplada onde a aplicação continua plenamente funcional mesmo na ausência de conexão ou caso a chave de API não esteja configurada, recorrendo aos geradores heurísticos locais.

## What Changes
- **Novo Módulo de Integração com IA (`utils/gemini_service.py`)**:
  - Implementação de cliente para a API do Google Gemini utilizando chamadas estruturadas (REST ou SDK oficial) com suporte a JSON Schema/formato estruturado.
  - Funções especializadas:
    - `generate_ai_mock_questions(exam_title, subject_name, content, num_questions=3)`: gera questões de múltipla escolha com enunciado, 4 opções, gabarito e justificativa pedagógica.
    - `generate_ai_study_plan(exam_title, days_remaining, topics, weak_topics)`: gera o cronograma diário detalhado e metas prioritárias.
    - `generate_ai_summary_and_flashcards(content, topics)`: gera resumos executivos e pares de flashcards.
    - `generate_ai_d1_review(exam_title, weak_topics, content)`: sintetiza os tópicos de maior vulnerabilidade em карточки de revisão relâmpago.
  - Sistema de cache e proteção contra estouro de taxa (rate limits) e tratamento elegante de erros.
- **Evolução de `utils/exam_prep_service.py`**:
  - Incorporação do `gemini_service` nos fluxos de `create_exam`, `generate_review_plan` e `get_d1_emergency_review`.
  - Fallback automático: caso a API Key não esteja configurada ou ocorra timeout, o sistema ativa imediatamente os algoritmos heurísticos existentes sem interromper a experiência do aluno.
- **Centralização de Configuração e Secrets (`utils/config.py` e `.streamlit/secrets.toml`)**:
  - Criação da função utilitária `get_gemini_api_key()` com resolução em cascata (`st.secrets["GEMINI_API_KEY"]` -> `os.environ["GEMINI_API_KEY"]` -> `.env`).
  - Atualização do template `.streamlit/secrets.toml.example` e do guia `STREAMLIT_SECRETS.md`.
- **Evolução da Interface Streamlit (`app.py`)**:
  - Indicador visual discreto de status da IA ("✨ IA Gemini Ativa" vs "⚙️ Modo Heurístico Local").
  - Botão de "🔄 Regenerar com IA" nas abas de Simulado e Revisão D-1.
  - Exibição de flashcards interativos e resumos gerados pela IA.
  - Feedback visual e mensagens informativas sobre configuração da chave caso o usuário queira habilitar a IA.
- **Suíte de Testes Automatizados (`tests/test_gemini_service.py`)**:
  - Testes unitários cobrindo requisições mockadas, parsing de JSON robusto, tratamento de erros e fallback para modo heurístico.

## Capabilities

### New Capabilities
- `gemini-ai-integration`: Serviço centralizado para conexão com a API Google Gemini, orquestração de prompts pedagógicos, validação de esquemas JSON estruturados, cache de chamadas e fallback offline.

### Modified Capabilities
- `exam-prep`: O Modo Prova passa a suportar opcionalmente o motor de IA generativa para criação de questões adaptativas, cronogramas inteligentes, resumos conceituais e revisão D-1, mantendo total retrocompatibilidade com o armazenamento em sessão/Xano.

## Impact
- **`utils/gemini_service.py`**: Novo módulo contendo as chamadas e prompts direcionados à API Gemini.
- **`utils/exam_prep_service.py`**: Orquestrador das rotinas de prova com integração do serviço de IA e fallback.
- **`utils/config.py`**: Adição do método de leitura segura de `GEMINI_API_KEY`.
- **`app.py`**: Adição de feedback visual de IA, novos botões de regeneração com IA e renderização de resumos/flashcards.
- **`.streamlit/secrets.toml.example` & `STREAMLIT_SECRETS.md`**: Instruções documentadas para inclusão de `GEMINI_API_KEY`.
- **`tests/test_gemini_service.py`**: Novos testes unitários sem dependência externa (mock).
