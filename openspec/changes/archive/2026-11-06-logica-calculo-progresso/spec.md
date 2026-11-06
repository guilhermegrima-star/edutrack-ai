# Especificação: Lógica de Cálculo de Progresso por Disciplina

## Comportamento Observável

### Entrada
- `subject_id` (int): ID da disciplina cujo progresso será calculado.
- `token` (str): JWT Bearer do usuário autenticado no grupo `edutrack.ai`.
- `done_status` (str, opcional): critério de conclusão (padrão: `"done"`).
- `tasks_path` (str, opcional): segmento de rota das tarefas no Xano (padrão: lido de `EDUTRACK_TASKS_PATH` ou `"academic_tasks"`).

### Saída de Sucesso (JSON)
```json
{
  "subject_id": 1,
  "subject_name": "Matemática",
  "total_tasks": 4,
  "completed_tasks": 2,
  "pending_tasks": 2,
  "progress_percent": 50.0,
  "has_tasks": true,
  "tasks_detail": [
    { "id": 10, "title": "Lista 1", "status": "done", "due_date": "2026-11-10", "is_done": true },
    { "id": 12, "title": "Lista 2", "status": "pending", "due_date": "2026-11-20", "is_done": false }
  ]
}
```

### Saída de Erro / Indisponibilidade (JSON)
Quando um endpoint retorna código de erro HTTP (ex: 404, 401, 500), o script não lança exceção: retorna a estrutura completa zerada com o detalhe do erro:
```json
{
  "subject_id": 1,
  "subject_name": "Matemática",
  "total_tasks": 0,
  "completed_tasks": 0,
  "pending_tasks": 0,
  "progress_percent": 0.0,
  "has_tasks": false,
  "tasks_detail": [],
  "error": {
    "code": "HTTP_404",
    "message": "GET /academic_tasks retornou 404: Not Found"
  }
}
```

## Regras de Negócio

1. **Critério de conclusão**: uma tarefa é considerada concluída quando `status == "done"` (comparação case-insensitive). O valor padrão é configurável via argumento `--done-status`.
2. **Progresso zero**: se `total_tasks == 0`, `progress_percent` retorna `0.0` e `has_tasks` retorna `false` (sem divisão por zero).
3. **Resiliência a erros HTTP**: erros HTTP em requisições à API Xano são tratados graciosamente. Em vez de interromper o script com `HTTPError`, a função retorna um JSON estruturado com métricas zeradas e os detalhes em `error`.
4. **Isolamento de dados**: as chamadas usam o grupo `edutrack.ai` com token Bearer, respeitando a regra de isolamento `user_id == $auth.id` do backend.
5. **Precisão**: `progress_percent` é arredondado para 2 casas decimais.
6. **Path configurável**: o endpoint de tarefas é definido dinamicamente por `EDUTRACK_TASKS_PATH` ou `--tasks-path`, suportando nomes alternativos como `task` ou `tasks` caso o endpoint seja publicado com outro padrão no Xano.

## Endpoints Consumidos

| Método | Path | Finalidade |
|--------|------|-----------|
| GET | `/subjects/{subjects_id}` | Obter nome da disciplina |
| GET | `/{tasks_path}?subject_id=X` | Listar tarefas da disciplina |
| GET | `/{tasks_path}/{id}` | Detalhes de tarefa individual |
| POST | `/{tasks_path}` | Criar tarefa |
| PATCH | `/{tasks_path}/{id}` | Atualizar tarefa |
| DELETE | `/{tasks_path}/{id}` | Remover tarefa |

## Configuração (.env)

| Variável | Valor Padrão | Descrição |
|---|---|---|
| `EDUTRACK_BASE_URL` | `https://x8ki-letl-twmt.n7.xano.io/api:gTfD518O` | URL base do grupo `edutrack.ai` |
| `EDUTRACK_TASKS_PATH` | `academic_tasks` | Rota das tarefas no Xano (`academic_tasks`, `task`, `tasks`) |
| `EDUTRACK_TOKEN` | — | JWT de autenticação |
