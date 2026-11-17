# Design: Criação e Gestão de Matérias Acadêmicas

## Context
Ver `proposal.md` para contexto e motivação, e `specs/subject-management/spec.md` para os requisitos de comportamento.
O sistema possui a aba "My Courses" em `app.py` com o resumo das disciplinas e o formulário de cadastro de tarefas acadêmicas. O backend Xano possui a especificação da tabela `subjects` com os campos `name`, `teacher`, `hours` e `user_id`. O módulo `utils/tasks_service.py` já possui as bases de dados locais e comunicação HTTP, mas necessita de aperfeiçoamento para criação de matérias com paleta visual e interface direta no Streamlit.

## Goals / Non-Goals

**Goals:**
- Prover interface visual elegante em `app.py` para criar novas disciplinas com `name`, `teacher`, `hours` e `color`.
- Sincronizar criação via `POST /subjects` no Xano com token do usuário ou fallback em `st.session_state["subjects_store"]`.
- Atualizar imediatamente a lista de disciplinas e o `st.selectbox` de matérias no cadastro de novas obrigações acadêmicas.
- Manter harmonia estética com o tema visual Smart Education (`utils/theme.py`).

**Non-Goals:**
- Exclusão em cascata de tarefas vinculadas a uma matéria removida.
- Gerenciamento avançado de permissões de professores ou upload de ementas em PDF.

## Decisions

### 1. Componente de Criação na Interface ("My Courses")
- **Decisão:** Utilizar um componente retrátil estilizado (`st.expander("➕ Cadastrar Nova Matéria / Disciplina")`) posicionado no topo da seção de cursos.
- **Alternativas consideradas:** `st.dialog` (modal flutuante).
- **Justificativa:** O expander mantém compatibilidade ampla com todas as versões do Streamlit e permite que o usuário veja os cursos existentes enquanto cadastra uma nova matéria.

### 2. Atribuição de Identidade Visual e Cores
- **Decisão:** Permitir que o usuário escolha a cor tema da matéria a partir de uma paleta pré-selecionada (`SUBJECT_PALETTE`: Roxo, Ouro, Índigo, Verde Esmeralda, Azul, Rosa, Violeta) com sugestão automática cíclica.
- **Alternativas consideradas:** Color picker livre sem restrições (`st.color_picker`).
- **Justificativa:** Manter a paleta temática padronizada preserva o contraste e a harmonia visual dos cards no dashboard.

### 3. Persistência Híbrida e Resiliência
- **Decisão:** `utils/tasks_service.py` tenta enviar a nova matéria para `POST /subjects` no Xano usando o token JWT ativo. Caso a requisição retorne erro ou o endpoint não esteja acessível, a disciplina é persistida com segurança no cache local de sessão (`subjects_store`) com um ID local único.
- **Alternativas consideradas:** Bloquear a criação se a API Xano estiver inacessível.
- **Justificativa:** Garante alta disponibilidade e continuidade da experiência de uso do aluno em qualquer ambiente.

## Risks / Trade-offs

- **[Endpoint /subjects indisponível no Xano]** → Mitigado pelo fallback resiliente em `session_state`, permitindo cadastrar a matéria localmente sem crash da aplicação.
- **[Duplicidade de nomes de disciplinas]** → Mitigado por validação prévia que alerta o usuário se uma matéria com o mesmo nome já estiver cadastrada para evitar confusão no seletor de tarefas.
- **[Matéria nova sem tarefas associadas]** → Mitigado exibindo o progresso inicial como `0%` e permitindo adicionar imediatamente tarefas vinculadas a ela.
