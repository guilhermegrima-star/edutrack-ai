# Proposta: Registro e Gestão de Obrigações Acadêmicas em "My Courses"

## Motivação
Permitir que os estudantes registrem e gerenciem diretamente na plataforma EduTrack AI suas obrigações acadêmicas (lições, provas, trabalhos e projetos) vinculadas a cada disciplina curricular matriculada.
Com essa funcionalidade, a aba **"My Courses"** transforma-se em uma central ativa de produtividade acadêmica, onde o aluno acompanha prazos, atualiza o status de suas entregas e visualiza seu progresso por disciplina.

Adicionalmente, simplificar o menu de navegação lateral (`opcao_menu`), removendo as opções não essenciais (`Schedule`, `Messages`, `Accomplishments`, `Community` e `Settings`) e focando a experiência exclusivamente em **"Dashboard"** e **"My Courses"** (além do acesso direto ao Perfil).

## Escopo
- **Simplificação da Navegação (`app.py`)**:
  - Ajustar `opcao_menu` para conter apenas `["Dashboard", "My Courses"]`.
  - Remover as seções `Schedule`, `Messages`, `Accomplishments`, `Community` e `Settings` do fluxo principal.
- **Definição de Esquema de Tarefas Acadêmicas**:
  - `title` (text): Título identificador da obrigação acadêmica.
  - `description` (text): Detalhes, instruções e critérios de entrega.
  - `due_date` (date): Data limite para entrega ou realização.
  - `status` (text): Situação da tarefa (ex: "Pendente", "Em Andamento", "Concluído" / "pending", "in_progress", "done").
  - `subject_id` (int/referência): Vínculo com a disciplina correspondente na tabela `subjects`.
- **Interface e Funcionalidades em "My Courses"**:
  - Formulário para registrar nova obrigação acadêmica vinculada a uma matéria selecionada.
  - Visualização de obrigações agrupadas ou filtradas por disciplina.
  - Atualização interativa de status (ex: marcar como concluída) e exclusão.
  - Cálculo e exibição do percentual de progresso por matéria em tempo real.
  - Integração com a API Xano (`GET /academic_tasks`, `POST /academic_tasks`, `PATCH/DELETE`) com sincronização e fallback transparente em `st.session_state`.

## Não-Escopo (Non-goals)
- Modificação das regras da API de autenticação ou da página de perfil.
- Submissão de arquivos binários pesados de trabalhos (o foco é a gestão e acompanhamento de obrigações e prazos).
