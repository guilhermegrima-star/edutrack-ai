# Tasks: Integração com IA (Google Gemini) no Modo Prova

## 1. Módulo de Configuração de Chaves e Credenciais (`utils/config.py`)

- [x] 1.1 Implementar a função `get_gemini_api_key()` em `utils/config.py` com resolução hierárquica (`st.secrets["GEMINI_API_KEY"]` -> `os.environ["GEMINI_API_KEY"]` -> `.streamlit/secrets.toml` -> `.env`), retornando a string limpa ou `None` caso não esteja definida.
- [x] 1.2 Atualizar o arquivo `.streamlit/secrets.toml.example` e a documentação `STREAMLIT_SECRETS.md` incluindo o parâmetro `GEMINI_API_KEY = "sua_chave_gemini_aqui"` e orientações de segurança sobre armazenamento da chave.

## 2. Criação do Módulo de IA Gemini (`utils/gemini_service.py`)

- [x] 2.1 Criar o módulo `utils/gemini_service.py` estruturando o cliente REST para o endpoint `models/gemini-1.5-flash:generateContent`, timeout de 10s, cabeçalhos de requisição e função auxiliar de parsing robusto de JSON com remoção de marcações de markdown (`json_cleaner`).
- [x] 2.2 Implementar `generate_ai_mock_questions(subject_name, title, content, num_questions=3)` com prompt pedagógico demandando retorno estritamente em JSON com enunciado, opções, gabarito e explicação didática fundamentada.
- [x] 2.3 Implementar `generate_ai_study_plan(title, days_remaining, content, weak_topics)` para produzir cronograma diário inteligente distribuindo metas de estudo ativo e técnicas de estudo (Active Recall, Feynman).
- [x] 2.4 Implementar `generate_ai_summary_and_flashcards(title, content)` gerando resumo executivo estruturado e pares de flashcards (pergunta e resposta conceitual).
- [x] 2.5 Implementar `generate_ai_d1_review(title, weak_topics, content)` para sintetizar tópicos de baixo domínio histórico em карточки de revisão relâmpago para a véspera da avaliação.

## 3. Integração com a Camada de Serviços do Modo Prova (`utils/exam_prep_service.py`)

- [x] 3.1 Integrar chamadas da IA em `create_exam` e `_generate_initial_questions_for_exam`, tentando gerar questões contextualizadas via Gemini e recorrendo ao gerador heurístico em caso de ausência de chave ou falha de rede.
- [x] 3.2 Integrar chamadas da IA em `generate_review_plan` e `get_d1_emergency_review`, populando metas personalizadas e resumo D-1 detalhado com inteligência contextual.
- [x] 3.3 Implementar função de conveniência `generate_additional_questions_with_ai(exam_id)` e `get_exam_ai_summary_and_flashcards(exam_id)` para carregar e persistir resumos e flashcards no store da avaliação.

## 4. Atualização da Interface do Usuário Streamlit (`app.py`)

- [x] 4.1 Adicionar badge indicativo do status da IA ("✨ IA Gemini Conectada" vs "⚙️ Modo Heurístico Local") no cabeçalho do Modo Prova, com popover instrutivo de como configurar a chave de API em `.streamlit/secrets.toml`.
- [x] 4.2 Adicionar botão de "🔄 Gerar Mais Questões com IA" na aba de "📝 Simulado & Quizzes", com indicador de carregamento (`st.spinner`).
- [x] 4.3 Adicionar nova seção ou aba "📚 Resumos & Flashcards" exibindo o resumo conceitual da matéria e flashcards interativos com revelação de resposta.
- [x] 4.4 Enriquecer a aba "⚡ Revisão D-1" com os карточки gerados pela IA focados especificamente nos tópicos críticos identificados.

## 5. Testes Automatizados e Validação

- [x] 5.1 Criar suíte de testes unitários `tests/test_gemini_service.py` cobrindo resolução da chave, extração e sanitização de JSON, chamadas mockadas à API do Gemini e fallback seguro contra erros de rede/HTTP 429.
- [x] 5.2 Executar a suíte de testes completa do repositório (`python -m unittest discover tests`) assegurando 100% de aprovação e ausência de regressões no `test_exam_prep_service.py` e `test_streamlit_secrets_config.py`.

