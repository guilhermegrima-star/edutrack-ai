# Especificação: Registro e Gestão de Obrigações Acadêmicas

## 1. Ajuste do Menu de Navegação (`app.py`)
- O menu `opcao_menu` da barra lateral deve conter **única e exclusivamente**:
  1. `Dashboard`
  2. `My Courses`
- Os itens `Schedule`, `Messages`, `Accomplishments`, `Community` e `Settings` devem ser removidos da lista e seus blocos condicionais eliminados ou redirecionados para manter o código enxuto e direto.

## 2. Esquema de Dados da Obrigação Acadêmica
- Toda obrigação acadêmica registrada no sistema deve conter obrigatoriamente os seguintes campos:
  - `title`: Texto não vazio representando o título da tarefa/prova/trabalho.
  - `description`: Texto opcional com orientações, referências ou anotações.
  - `due_date`: Data válida de entrega no formato ISO/date.
  - `status`: Texto representando o estado atual (`Pendente`, `Em Andamento`, `Concluído` / `pending`, `in_progress`, `done`).
  - `subject_id`: Identificador numérico inteiro vinculando a tarefa a uma disciplina existente na tabela `subjects`.

## 3. Comportamento e Funcionalidades em "My Courses"
- **Seleção e Listagem de Disciplinas**:
  - Exibir as disciplinas ativas do aluno (`UI UX Fundamentals`, `UI Colours theories`, `Algoritmos e Programação`, `Inteligência Artificial & Lab`, `Bases de Dados Relacionais`).
- **Registro de Novas Obrigações (Create)**:
  - O aluno deve ser capaz de preencher um formulário com Título, Disciplina (`subject_id`), Data de Entrega (`due_date`), Status (`status`) e Descrição (`description`).
  - Ao submeter, a tarefa é registrada e imediatamente refletida na listagem.
- **Gestão de Obrigações (Read, Update, Delete)**:
  - Listar as tarefas de cada disciplina com indicação visual de status e prazo.
  - Permitir alternar o status de uma tarefa entre Pendente, Em Andamento e Concluído.
  - Permitir exclusão de obrigações já finalizadas ou canceladas.
- **Feedback de Progresso**:
  - Atualização dinâmica da taxa percentual de tarefas concluídas por disciplina e no geral.
