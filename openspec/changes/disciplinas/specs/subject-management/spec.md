# Spec Delta

## Purpose
Permite aos estudantes cadastrar e gerenciar disciplinas acadêmicas (matérias), professores responsáveis e carga horária na plataforma EduTrack AI, com integração aos endpoints da tabela subjects do Xano.

## ADDED Requirements

### Requirement: Subject Creation Form
O sistema DEVE / SHALL disponibilizar na aba "My Courses" um formulário intuitivo para cadastro de novas disciplinas acadêmicas contendo Nome da Matéria, Nome do Professor, Carga Horária em horas e Cor de Identificação.

#### Scenario: Successful subject creation
- **WHEN** o usuário preenche nome da matéria, professor e carga horária positiva e submete o formulário
- **THEN** o sistema cadastra a disciplina no backend Xano (ou fallback local seguro), exibe confirmação de sucesso e atualiza a interface reativamente

#### Scenario: Validation of required fields
- **WHEN** o usuário tenta submeter o formulário sem preencher o nome da matéria ou o nome do professor
- **THEN** o sistema bloqueia o envio e exibe mensagem de alerta informando que os campos são obrigatórios

#### Scenario: Validation of invalid hours
- **WHEN** o usuário informa carga horária menor ou igual a zero
- **THEN** o sistema recusa a criação com indicação de que a carga horária deve ser um número positivo maior que zero

### Requirement: Integration with Academic Tasks
O sistema DEVE / SHALL integrar as matérias cadastradas ao seletor de disciplinas no formulário de registro de novas obrigações acadêmicas e na listagem do painel.

#### Scenario: Newly created subject appears in task selector
- **WHEN** uma nova disciplina é cadastrada com êxito
- **THEN** o seletor de matérias no cadastro de novas tarefas passa a incluir imediatamente a nova disciplina como opção vinculável

### Requirement: Visual Feedback and Theme Consistency
O sistema DEVE / SHALL atribuir uma cor da paleta visual oficial a cada disciplina cadastrada e renderizar os cards com nome, professor e métricas de progresso.

#### Scenario: Displaying subject card in courses panel
- **WHEN** as matérias ativas são renderizadas na aba "My Courses"
- **THEN** cada matéria é exibida com seu nome, professor responsável, carga horária formatada e indicador visual de progresso
