# Tasks: Modo Prova — Preparação Ativa para Avaliações

## 1. Módulo de Serviços do Modo Prova (`utils/exam_prep_service.py`)

- [x] 1.1 Criar o módulo `utils/exam_prep_service.py` estruturando os esquemas de dados em memória e sessão para provas (`exams`), domínio de tópicos (`topic_mastery`), simulados/questões (`mock_questions`), cronograma diário (`review_schedule`) e histórico de sessões (`study_sessions`), verificando importação e inicialização.
- [x] 1.2 Implementar método de cadastro de prova `create_exam` com validação de campos obrigatórios, bloqueio de datas retroativas e geração automática do cronograma diário com contagem regressiva (`generate_review_plan`), verificando retorno dos dias restantes.
- [x] 1.3 Implementar o gerador de questões e simulados `generate_mock_exam` com suporte a formatos objetivos e discursivos, indicação de fonte/origem e métodos para aprovar, editar ou rejeitar itens (`update_question_status`).
- [x] 1.4 Implementar a função de cálculo do Índice de Preparo `calculate_prep_index` e atualização do mapa de domínio `update_topic_mastery` baseados nas respostas e acurácia do estudante por tópico.
- [x] 1.5 Implementar gerador da Revisão Final D-1 `get_d1_emergency_review` filtrando prioritariamente os tópicos críticos com domínio inferior a 60%.

## 2. Interface do Modo Prova no Streamlit (`app.py`)

- [x] 2.1 Adicionar a opção `"Modo Prova"` no menu de navegação lateral (`opcao_menu`) em `app.py` e estruturar o layout em 4 abas (`st.tabs`): "🎯 Configuração da Prova", "📅 Plano & Cronograma", "📝 Simulado & Quizzes" e "⚡ Revisão D-1".
- [x] 2.2 Construir a interface da aba de Configuração com seleção da disciplina existente, seleção da data da avaliação, seletor de formato e campo de texto para materiais/ementa com botão de "Gerar Plano de Preparação".
- [x] 2.3 Construir a interface da aba de Plano & Cronograma exibindo card de contagem regressiva em dias, checklist diário de revisão e gráfico/cards com o mapa de domínio de tópicos (Fortes vs. Fracos).
- [x] 2.4 Construir a interface da aba de Simulado Interativo com resolução passo a passo de questões, feedback de gabarito e botões de ação do aluno (aprovar, editar enunciado, descartar questão).
- [x] 2.5 Construir a interface da aba de Revisão Final D-1 destacando resumo condensado dos pontos críticos, fórmulas, conceitos fundamentais e questões de maior probabilidade.

## 3. Testes Automatizados e Validação OpenSpec

- [x] 3.1 Criar arquivo de testes unitários `tests/test_exam_prep_service.py` cobrindo validação de datas, cálculo do índice de preparo, planos diários e curadoria de questões, verificando aprovação com `python -m unittest discover tests`.
- [x] 3.2 Executar a validação formal do OpenSpec com `openspec validate modo-prova` e verificar ausência de inconsistências.
