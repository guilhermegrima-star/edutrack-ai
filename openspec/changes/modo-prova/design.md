# Design: Modo Prova — Arquitetura e Engenharia de Preparação Ativa

## Context
Ver `proposal.md` para motivação e `specs/exam-prep/spec.md` para os requisitos funcionais e cenários comportamentais.
O EduTrack AI já possui um ecossistema consolidado de autenticação, dashboard de métricas, gestão de disciplinas (`subjects`) e tarefas acadêmicas (`academic_tasks`), com persistência híbrida (API Xano + `st.session_state`). O **Modo Prova** alavanca essa fundação para transformar o estudo em um processo ativo orientado a objetivos com data marcada.

## Goals / Non-Goals

**Goals:**
- Prover um módulo desacoplado e reutilizável (`utils/exam_prep_service.py`) para gerenciar provas, planos de estudo, simulados e métricas de domínio.
- Entregar interface intuitiva e unificada no Streamlit com navegação em 4 abas estruturadas:
  1. **Configuração da Prova**: disciplina, data, formato e ementa/conteúdo.
  2. **Plano de Revisão & Cronograma**: contagem regressiva e checklist diário por prioridade.
  3. **Simulado & Quizzes Interativos**: questões adaptativas com feedback imediato e curadoria humana (aprovar/editar/rejeitar).
  4. **Revisão Final (D-1)**: síntese emergencial focada nos tópicos com maior vulnerabilidade.
- Modelar o cálculo do **Índice de Preparo (0-100%)** e o mapa de domínio de tópicos (Fortes vs. Fracos).
- Respeitar governança, explicabilidade (indicação de origem) e limites de créditos de IA.

**Non-Goals:**
- Aplicação de provas formais com bloqueio de navegador (lockdown browser/proctoring invasivo).
- Processamento massivo de arquivos binários de vídeo ou áudio (foco em conteúdo textual, tópicos e notas de aula).

## Decisions

### 1. Modelo de Dados e Integração Híbrida (Xano & Sessão Local)
- **Decisão:** Reutilizar a entidade `subjects` como chave estrangeira (`subject_id`) e modelar as seguintes estruturas na camada de serviços (`exam_prep_service`):
  - `exams`: `id`, `subject_id`, `user_id`, `exam_date`, `exam_type`, `topics_content`, `created_at`.
  - `topic_mastery`: `id`, `exam_id`, `topic_name`, `mastery_score` (0-100), `accuracy_rate`, `questions_answered`.
  - `mock_questions`: `id`, `exam_id`, `topic_name`, `question_text`, `options` (list), `correct_option`, `explanation`, `source_reference`, `status` ('approved', 'rejected', 'edited').
  - `review_schedule`: `id`, `exam_id`, `day_offset`, `target_date`, `priority_topics` (list), `is_completed`.
  - `study_sessions`: `id`, `exam_id`, `session_date`, `score_obtained`, `total_questions`, `prep_index_snapshot`.
- **Justificativa:** Compatível com os padrões de tabelas relacionais do Xano e serializável diretamente no `st.session_state` para garantir operação offline ou em fallback sem quebras.

### 2. Algoritmo de Cálculo do Índice de Preparo e Domínio
- **Decisão:** O Índice de Preparo é uma média ponderada composta por:
  $$\text{Índice de Preparo} = (0.45 \times \text{Acurácia nos Simulados}) + (0.25 \times \text{Cobertura de Tópicos}) + (0.20 \times \text{Pontuação dos Tópicos Críticos}) + (0.10 \times \text{Cadência/Frequência de Estudos})$$
  - Tópicos com `mastery_score < 60%` são classificados como **"Pontos a Reforçar / Críticos"**.
  - Tópicos com `mastery_score >= 60%` são classificados como **"Pontos Fortes / Dominados"**.
- **Justificativa:** Evita que o aluno sinta uma falsa sensação de segurança acertando apenas questões de assuntos fáceis; penaliza a negligência de tópicos vulneráveis.

### 3. Geração Adaptativa e Transparência da IA (Sem "Caixa Preta")
- **Decisão:** O gerador de simulado extrai os tópicos a partir do texto do aluno ou materiais fornecidos, dividindo-os em conceitos e criando questões objetivas contextualizadas.
  - Cada questão exibe um badge `Fonte: [Trecho/Origem]` e botões de `✏️ Editar` e `❌ Rejeitar`.
  - Se o conteúdo fornecido for muito curto, um fallback inteligente orienta o aluno a detalhar os tópicos ou sugere temas comuns da matéria.
- **Justificativa:** O aluno mantém total agência sobre o que estuda, validando o material gerado e aumentando a confiança na IA.

### 4. Experiência de Usuário no Streamlit (`app.py`)
- **Decisão:** Implementar a aba `"Modo Prova"` no menu lateral com subseções bem delimitadas por `st.tabs`:
  - `st.tabs(["🎯 Configurar Prova", "📅 Plano & Cronograma", "📝 Simulado & Quizzes", "⚡ Revisão D-1"])`.
  - Uso de badges coloridos harmoniosos com a paleta do EduTrack AI (`#6C5CE7`, `#10B981`, `#F6C768`, `#EF4444`).
- **Justificativa:** Reduz a sobrecarga cognitiva do aluno e permite transitar entre fazer simulados e checar o cronograma em um único clique.

## Risks / Trade-offs

- **[Conteúdo de entrada muito vago pelo aluno]** → O sistema analisa o tamanho do texto e oferece exemplos predefinidos ou orienta a inserção de tópicos pontuais.
- **[Proximidade extrema da data da prova (ex: prova amanhã)]** → O sistema adapta o plano diário automaticamente, acionando diretamente a Revisão Final D-1 sem gerar um cronograma longo.
- **[Custos de tokens e abuso de requisições de IA]** → Cache local das questões geradas por prova e limite de simulados por dia para contas gratuitas.

## Test Strategy
1. Teste de geração e validação de datas e dados da prova em `test_exam_prep_service.py`.
2. Teste do algoritmo matemático do Índice de Preparo e redistribuição de pesos de tópicos.
3. Teste de aprovação, edição e rejeição de questões do simulado.
4. Teste da seleção de tópicos críticos para a Revisão Final D-1.
5. Teste de fallback quando a API Xano estiver sem conexão.
