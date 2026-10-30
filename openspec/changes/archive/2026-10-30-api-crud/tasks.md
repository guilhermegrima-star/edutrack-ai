# Tarefas de Implementação: API CRUD

- [x] Criar definição da tabela `academic_tasks` em `tables/academic_tasks.xs`
- [x] Garantir definição da tabela `subjects` em `tables/subjects.xs`
- [x] Implementar endpoint `PATCH /subjects/{subjects_id}` com validação de `user_id == $auth.id`
- [x] Implementar endpoint `DELETE /subjects/{subjects_id}` com validação de `user_id == $auth.id`
- [x] Implementar endpoints complementares de `subjects` (`POST`, `GET`, `GET /{id}`) com isolamento de usuário
- [x] Implementar endpoint `PATCH /academic_tasks/{academic_tasks_id}` com validação de `user_id == $auth.id`
- [x] Implementar endpoint `DELETE /academic_tasks/{academic_tasks_id}` com validação de `user_id == $auth.id`
- [x] Implementar endpoints complementares de `academic_tasks` (`POST`, `GET`, `GET /{id}`) com validação relacional e isolamento de usuário

