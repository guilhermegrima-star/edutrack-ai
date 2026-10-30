# Especificação: CRUD e Segurança para Subjects e Academic Tasks

## Regras de Negócio e Segurança
1. **Autenticação Obrigatória**: Todos os endpoints de `subjects` e `academic_tasks` exigem autenticação do usuário (`auth = "user"`).
2. **Isolamento de Dados (Multitenancy)**:
   - Na criação (`POST`), o campo `user_id` é obrigatoriamente preenchido com `$auth.id`.
   - Na listagem (`GET`), os registros retornados são filtrados por `$db.<table>.user_id == $auth.id`.
   - Na leitura individual (`GET /{id}`), é validado se o registro pertence ao usuário autenticado antes de retornar (`precondition ($record.user_id == $auth.id)`).
   - Na atualização (`PATCH /{id}`), é validado se o registro pertence ao usuário autenticado (`precondition ($record.user_id == $auth.id)`) antes de aplicar as mudanças. O `user_id` não pode ser transferido para outro usuário.
   - Na exclusão (`DELETE /{id}`), é validado se o registro pertence ao usuário autenticado antes de deletar (`precondition ($record.user_id == $auth.id)`).
3. **Consistência Relacional**:
   - Para `academic_tasks`, ao criar ou associar uma matéria (`subject_id`), o sistema valida se a matéria especificada existe e pertence ao mesmo usuário autenticado.

## Endpoints

### Subjects
- `GET /subjects`: Lista matérias do usuário autenticado.
- `GET /subjects/{subjects_id}`: Detalhes de uma matéria do usuário.
- `POST /subjects`: Cadastra nova matéria para o usuário autenticado.
- `PATCH /subjects/{subjects_id}`: Atualiza matéria do usuário autenticado.
- `DELETE /subjects/{subjects_id}`: Remove matéria do usuário autenticado.

### Academic Tasks
- `GET /academic_tasks`: Lista tarefas do usuário autenticado (filtro opcional `subject_id`).
- `GET /academic_tasks/{academic_tasks_id}`: Detalhes de uma tarefa do usuário.
- `POST /academic_tasks`: Cadastra nova tarefa associada a uma matéria do usuário.
- `PATCH /academic_tasks/{academic_tasks_id}`: Atualiza tarefa do usuário autenticado.
- `DELETE /academic_tasks/{academic_tasks_id}`: Remove tarefa do usuário autenticado.

