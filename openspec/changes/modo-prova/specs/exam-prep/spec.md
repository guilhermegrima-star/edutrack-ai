# Spec Delta

## Purpose
Disponibiliza a funcionalidade Modo Prova no EduTrack AI para preparação ativa para avaliações, incluindo planejamento diário com contagem regressiva, simulados adaptativos, mapeamento de domínio por tópicos, índice de preparo e revisão focada na véspera.

## ADDED Requirements

### Requirement: Exam Configuration and Assessment Profile
O sistema DEVE / SHALL permitir que o estudante configure uma avaliação indicando a disciplina curricular vinculada, a data da prova, o formato avaliativo (múltipla escolha, discursiva, mista ou prática) e o conteúdo programático ou materiais de estudo.

#### Scenario: Successful exam setup
- **WHEN** o aluno seleciona uma disciplina existente, define uma data futura e insere o conteúdo programático de estudo
- **THEN** o sistema salva o registro da avaliação e gera automaticamente o perfil preparatório com plano inicial

#### Scenario: Rejection of invalid exam date
- **WHEN** o aluno tenta cadastrar uma avaliação com data no passado
- **THEN** o sistema bloqueia o cadastro e exige a seleção de uma data válida igual ou posterior ao dia atual

#### Scenario: Handling insufficient study content
- **WHEN** o aluno cadastra uma prova com conteúdo textual vazio ou insuficiente (menos de 15 caracteres)
- **THEN** o sistema alerta o aluno e solicita detalhes adicionais ou tópicos mínimos para viabilizar a geração do simulado

### Requirement: Study Plan and Countdown Schedule
O sistema DEVE / SHALL gerar um cronograma diário estruturado com contagem regressiva em dias até a data da avaliação, distribuindo metas diárias e priorizando tópicos com menor domínio do estudante.

#### Scenario: Daily study plan generation
- **WHEN** uma avaliação é configurada com sucesso
- **THEN** o sistema calcula a diferença em dias até a prova e apresenta um checklist de revisão diário ordenado por relevância e urgência

#### Scenario: Countdown updates dynamically
- **WHEN** o aluno acessa o Modo Prova em dias subsequentes
- **THEN** o sistema atualiza automaticamente o contador regressivo e destaca as metas correspondentes ao dia atual

### Requirement: Adaptive Mock Quizzes and Flashcard Sessions
O sistema DEVE / SHALL gerar simulados interativos e flashcards com base no conteúdo informado pelo estudante, exibindo a origem do material e permitindo ao aluno responder, revisar, aprovar, editar ou rejeitar itens.

#### Scenario: Taking an interactive quiz session
- **WHEN** o aluno inicia uma sessão de simulado e responde a uma questão de múltipla escolha
- **THEN** o sistema valida a resposta, exibe feedback explicativo imediato e computa o acerto/erro para recalcular o domínio do tópico

#### Scenario: Student rejects or adjusts generated question
- **WHEN** o aluno revisa as questões geradas e decide rejeitar ou editar o enunciado de uma questão de baixa aderência
- **THEN** o sistema remove ou atualiza a questão da lista ativa e reflete a alteração no banco de questões do simulado

### Requirement: Preparation Index and Topic Mastery Mapping
O sistema DEVE / SHALL mensurar e exibir o Índice de Preparo (percentual de 0% a 100%) e o mapa visual de domínio por tópico, identificando claramente pontos fortes e pontos fracos do aluno.

#### Scenario: Preparation index evolution after study session
- **WHEN** o aluno conclui uma rodada de simulado ou revisão de flashcards com taxa de acertos superior à anterior
- **THEN** o sistema recalcula o Índice de Preparo para cima e atualiza a categorização dos tópicos entre dominados e a reforçar

#### Scenario: Identifying critical vulnerable topics
- **WHEN** o aluno erra repetidamente questões de um tópico específico
- **THEN** o sistema classifica o tópico como "Ponto Crítico / Baixo Domínio" e o eleva ao topo da prioridade do plano de estudos

### Requirement: Final Countdown Review (D-1)
O sistema DEVE / SHALL fornecer na véspera da avaliação (D-1) uma revisão condensada ultrarrápida, concentrando exclusivamente os pontos de maior vulnerabilidade, fórmulas vitais, conceitos-chave e questões de alta probabilidade.

#### Scenario: Displaying D-1 emergency review
- **WHEN** faltar 1 dia ou menos para a realização da prova
- **THEN** o sistema ativa o módulo de Revisão Final D-1 com карточки de foco máximo contendo apenas os tópicos com menor domínio histórico
