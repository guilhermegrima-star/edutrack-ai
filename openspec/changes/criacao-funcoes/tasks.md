# Tarefas de Implementação: Registro e Gestão de Obrigações Acadêmicas

- [x] 1. Ajuste do Menu de Navegação (`app.py`)
  - [x] 1.1 Remover do `opcao_menu = st.sidebar.radio(...)` as opções: Schedule, Messages, Accomplishments, Community, Settings
  - [x] 1.2 Manter apenas `["Dashboard", "My Courses"]` no rádio da sidebar
  - [x] 1.3 Limpar os blocos condicionais das opções removidas em `app.py`

- [x] 2. Módulo de Serviços de Tarefas e Disciplinas (`utils/tasks_service.py`)
  - [x] 2.1 Definir esquema estruturado com campos `title`, `description`, `due_date`, `status` e `subject_id`
  - [x] 2.2 Implementar métodos para carregar disciplinas e tarefas (com sincronização de API Xano e fallback de sessão)
  - [x] 2.3 Implementar criação, atualização de status e remoção de tarefas acadêmicas
  - [x] 2.4 Implementar cálculo de progresso por disciplina `(concluidas / total) * 100`

- [x] 3. Interface de Gestão em "My Courses" (`app.py`)
  - [x] 3.1 Construir painel de resumo por disciplina com barra de progresso visual
  - [x] 3.2 Construir formulário estilizado de registro de nova obrigação acadêmica
  - [x] 3.3 Construir listagem interativa de tarefas com badges de status e prazos
  - [x] 3.4 Implementar botões de ação para concluir e excluir obrigações com recarregamento reativo (`st.rerun`)

- [x] 4. Validação e Testes
  - [x] 4.1 Testar criação de nova tarefa com os campos especificados
  - [x] 4.2 Testar alteração de status e reflexo no progresso da disciplina
  - [x] 4.3 Testar remoção de tarefas
  - [x] 4.4 Garantir harmonia com o tema visual Smart Education (/assets/home principal.png)
