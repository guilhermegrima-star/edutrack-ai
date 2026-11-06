# Tarefas de Implementação: Lógica de Cálculo de Progresso

- [x] Criar cliente HTTP `EduTrackClient` com suporte a autenticação Bearer JWT
- [x] Implementar método de busca de disciplina (`get_subject`) com tratamento de erro sem exceção
- [x] Implementar método de listagem de tarefas (`list_tasks`) com suporte a filtro `subject_id` e path configurável (`EDUTRACK_TASKS_PATH`)
- [x] Implementar métodos CRUD complementares (`get_task`, `create_task`, `update_task`, `delete_task`)
- [x] Implementar função `calculate_progress` calculando porcentagem `(concluídas / total) * 100`
- [x] Tratar erros HTTP graciosamente retornando estrutura JSON padronizada com campo `error` em vez de interromper o script com `HTTPError`
- [x] Configurar variáveis de ambiente no `.env` (`EDUTRACK_BASE_URL`, `EDUTRACK_TASKS_PATH`)
- [x] Implementar interface CLI (`argparse`) com suporte aos argumentos `--subject-id`, `--token`, `--done-status` e `--tasks-path`
- [x] Validar cenários de sucesso, erro de tarefas (404) e erro de disciplina (404) via testes unitários
