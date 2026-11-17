# Proposal: Modo Prova — Preparação Ativa e Personalizada para Avaliações

## Why
O EduTrack AI já organiza a rotina acadêmica dos estudantes por meio de autenticação, dashboard de métricas, gestão de disciplinas e tarefas, progresso do semestre e relatórios. No entanto, diante de avaliações com data marcada, os alunos enfrentam ansiedade e falta de direcionamento prático: estudam de forma passiva, têm dificuldade em identificar lacunas conceituais e não possuem um plano estruturado até o dia do exame.
O **Modo Prova** transforma o EduTrack AI em uma central ativa de preparação: combina planejamento diário com contagem regressiva, geração de simulados adaptativos baseados no conteúdo do aluno, mapeamento de domínio por tópicos e um índice dinâmico de preparo, culminando em uma revisão condensada no dia anterior à prova focada exclusivamente nos pontos fracos.

## What Changes
- **Nova Seção "Modo Prova" na Navegação Principal (`app.py`)**:
  - Adição da opção `"Modo Prova"` no menu de navegação da sidebar.
  - Painel com abas organizadas: **Configuração da Prova**, **Plano de Revisão & Cronograma**, **Simulado Ativo (Quizzes & Flashcards)** e **Revisão Final (D-1)**.
- **Configuração de Avaliação com Data Marcada**:
  - Seleção da disciplina vinculada (reutilizando a tabela `subjects`).
  - Definição da data da avaliação, peso/formato (múltipla escolha, discursiva, mista, prática) e inserção do conteúdo programático / materiais de estudo / tópicos centrais.
  - Geração automática e transparente do plano de preparação.
- **Plano de Revisão Diário & Contagem Regressiva**:
  - Contagem regressiva visual dinâmica até o dia da prova.
  - Cronograma de metas diárias de estudo com checklist inteligente priorizando tópicos com menor domínio e maior relevância.
- **Simulados Adaptativos, Flashcards e Repetição Espaçada**:
  - Geração de simulados estruturados a partir do conteúdo inserido pelo aluno com referência clara da origem do item (sem caixa preta).
  - Permissão para o estudante aprovar, editar ou rejeitar questões e flashcards gerados.
  - Sessões de estudo ativas com correção e feedback explicativo imediato por questão.
- **Diagnóstico de Domínio e Índice de Preparo (0 a 100%)**:
  - Mapeamento granular do domínio da matéria dividido por tópicos (Pontos Fortes vs. Pontos a Reforçar).
  - Cálculo contínuo do **Índice de Preparo (%)** ponderando:
    1. Acurácia em simulados e quizzes.
    2. Retenção e revisão de flashcards com repetição espaçada.
    3. Frequência/cadência de sessões de estudo.
    4. Cobertura dos tópicos prioritários.
- **Revisão Final Condensada (D-1)**:
  - Ativação ou destaque especial na véspera da prova.
  - Resumo executivo ultrarrápido contendo somente os pontos de maior vulnerabilidade, fórmulas-chave, conceitos vitais e questões de alta probabilidade.
- **Módulo de Serviços e Persistência (`utils/exam_prep_service.py`)**:
  - Estrutura de dados para provas (`exams`), tópicos de domínio (`topic_mastery`), simulados/questões (`mock_questions`), planos diários (`review_schedule`) e sessões de estudo (`study_sessions`).
  - Sincronização compatível com endpoints do Xano e fallback local persistente em `st.session_state`.
- **Governança de IA e Custos**:
  - Controle de limites de créditos/tokens por sessão para planos gratuitos, respeitando privacidade e LGPD.

## Capabilities

### New Capabilities
- `exam-prep`: Central de preparação para avaliações com data marcada no EduTrack AI ("Modo Prova"), integrando agendamento de prova, cronograma diário com contagem regressiva, simulados adaptativos, repetição espaçada, mapa de domínio por tópicos, índice de preparo evolutivo e revisão emergencial D-1.

### Modified Capabilities
<!-- Nenhuma especificação existente modificada diretamente -->

## Impact
- **Interface Streamlit (`app.py`)**: Inclusão de `"Modo Prova"` no menu lateral e orquestração das visualizações de configuração, cronograma, simulado e revisão final.
- **Novo Módulo de Negócios (`utils/exam_prep_service.py`)**: Lógica de cálculo do índice de preparo, repetição espaçada, mapa de tópicos e persistência.
- **Módulo de Configurações (`utils/config.py`)**: Suporte a parâmetros e endpoints para provas e simulados.
- **Suíte de Testes (`tests/test_exam_prep_service.py`)**: Testes unitários para cálculos de índice, geração de plano diário, validação de regras de negócio e fallbacks.
