# Tasks: Criação e Gestão de Matérias Acadêmicas

## 1. Módulo de Serviços de Disciplinas (`utils/tasks_service.py`)

- [x] 1.1 Atualizar a função `create_subject` em `utils/tasks_service.py` para receber parâmetro opcional de cor (`color`), validar campos obrigatórios (`name`, `teacher`, `hours > 0`), realizar chamada `POST /subjects` ao Xano com token autenticado e aplicar fallback em `st.session_state["subjects_store"]`, verificando via testes unitários.
- [x] 1.2 Garantir que `get_subjects` sincronize com a API Xano e mantenha a atribuição consistente de cores temáticas (`SUBJECT_PALETTE`) para qualquer nova disciplina registrada.

## 2. Interface de Criação de Matérias em "My Courses" (`app.py`)

- [x] 2.1 Construir formulário expansível estilizado ("➕ Cadastrar Nova Matéria / Disciplina") na aba "My Courses" em `app.py` com campos de texto para Nome da Matéria, Professor Responsável, Carga Horária e seletor de Cor Temática, verificando renderização visual consistente.
- [x] 2.2 Implementar a ação de submissão do formulário chamando `create_subject` com o token ativo, exibindo feedback visual de confirmação/erro e executando `st.rerun()` para recarregamento reativo.
- [x] 2.3 Garantir que a matéria recém-criada apareça imediatamente no `st.selectbox` de matérias no formulário de novas tarefas acadêmicas e na lista de cards de resumo de disciplinas.

## 3. Testes e Validação

- [x] 3.1 Adicionar testes unitários em `tests/test_tasks_service.py` cobrindo criação com cor personalizada, rejeição de dados inválidos e fallback local, verificando aprovação total com `python -m unittest discover tests`.
- [x] 3.2 Executar validação de conformidade do OpenSpec com `openspec validate disciplinas` e verificar que a proposta está 100% válida.
