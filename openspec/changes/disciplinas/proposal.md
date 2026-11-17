# Proposal: Criação e Gestão de Matérias Acadêmicas

## Why
Atualmente, a plataforma EduTrack AI permite que o estudante cadastre e gerencie suas obrigações acadêmicas (tarefas, lições e trabalhos) na aba "My Courses", porém a lista de disciplinas ainda depende de valores pré-definidos caso não haja matérias cadastradas no backend. 
Para proporcionar uma experiência acadêmica completa e personalizada, é necessário que o aluno possa registrar suas próprias matérias/disciplinas, informando nome da matéria, professor responsável, carga horária e cor de destaque, com persistência na tabela `subjects` da API Xano.

## What Changes
- **Interface de Criação de Matérias em "My Courses" (`app.py`)**:
  - Adicionar formulário interativo (expander/modal) para registrar uma nova matéria com os seguintes campos:
    - **Nome da Disciplina** (`name`): texto obrigatório (ex: "Estruturas de Dados").
    - **Professor Responsável** (`teacher`): texto obrigatório (ex: "Prof. Marcos Oliveira").
    - **Carga Horária** (`hours`): numérico inteiro positivo representando horas totais (ex: 80).
    - **Cor / Identidade Visual** (`color`): seleção ou atribuição automática de cor temática da paleta do EduTrack AI para os cards.
  - Botão de submissão com validação defensiva e recarregamento reativo (`st.rerun()`).
  - Atualização imediata do seletor de disciplinas no formulário de novas tarefas/atividades para incluir a nova matéria criada.
- **Camada de Serviço e Integração com Xano (`utils/tasks_service.py`)**:
  - Aperfeiçoar o método `create_subject(name, teacher, hours, color, token)` para sincronizar com `POST /subjects` na API Xano e manter persistência no estado local da sessão (`st.session_state["subjects_store"]`).
  - Garantir tratamento resiliente de erros com fallback local seguro caso a API do Xano esteja temporariamente indisponível.
  - Garantir que `get_subjects(token)` carregue tanto do Xano quanto do cache local atualizado.
- **Validações e Testes Unitários**:
  - Testes em `tests/test_tasks_service.py` validando os fluxos de criação de disciplinas, validação de entradas inválidas, resposta do Xano e comportamento com fallback.

## Capabilities

### New Capabilities
- `subject-management`: Criação e gerenciamento de disciplinas acadêmicas vinculadas ao usuário autenticado, com atributos de nome, professor, carga horária e estilo visual, integradas aos endpoints `/subjects` do Xano.

### Modified Capabilities
<!-- Nenhuma especificação existente modificada -->

## Impact
- **Interface Streamlit (`app.py`)**: Aba "My Courses" ganha botão e formulário dedicado de "Nova Disciplina", e os seletores de matérias são atualizados dinamicamente.
- **Serviço de Dados (`utils/tasks_service.py`)**: Expansão de `create_subject` e `get_subjects` com suporte a metadados e persistência consistente.
- **Suíte de Testes (`tests/test_tasks_service.py`)**: Expansão da cobertura com testes para validação e criação de matérias.
