# Design Técnico: Lógica de Cálculo de Progresso por Disciplina

## Localização

```
scripts/
└── calculate_progress.py   ← arquivo principal
.env                        ← variáveis EDUTRACK_BASE_URL e EDUTRACK_TOKEN
```

## Arquitetura do Módulo

```
EduTrackClient (dataclass)
├── token: str
├── base_url: str  ← lido de EDUTRACK_BASE_URL (.env)
├── _session: requests.Session  (Bearer token injetado em __post_init__)
│
├── Subjects
│   └── get_subject(subject_id) → GET /subjects/{id}
│
└── Academic Tasks (CRUD completo)
    ├── list_tasks(subject_id?)  → GET /academic_tasks[?subject_id=X]
    ├── get_task(task_id)        → GET /academic_tasks/{id}
    ├── create_task(payload)     → POST /academic_tasks
    ├── update_task(id, payload) → PATCH /academic_tasks/{id}
    └── delete_task(task_id)     → DELETE /academic_tasks/{id}

calculate_progress(client, subject_id, done_status="done") → dict
progress_to_json(result, indent=2) → str
```

## Fluxo de `calculate_progress`

```
1. GET /subjects/{subject_id}
   ├── OK  → extrai subject_name
   └── 404 → subject_name = "Disciplina não encontrada"

2. GET /academic_tasks?subject_id={subject_id}
   └── retorna lista (vazia ou não)

3. Calcula métricas
   total      = len(tasks)
   completed  = count(t.status.lower() == done_status.lower())
   pending    = total - completed
   progress   = round((completed / total) * 100, 2)  if total > 0 else 0.0

4. Monta tasks_detail
   [{ id, title, status, due_date, is_done }]

5. Retorna dict com todos os campos especificados
```

## Tratamento de Resposta da API

A listagem `GET /academic_tasks` pode retornar dois formatos; o cliente normaliza ambos:

```python
# formato lista direta
[{ "id": 1, ... }, { "id": 2, ... }]

# formato envelope
{ "items": [...] }   ou   { "result": [...] }
```

## Uso via CLI

```bash
# com argumento direto
python scripts/calculate_progress.py --subject-id 1 --token <JWT>

# com variável de ambiente
set EDUTRACK_TOKEN=<JWT>
python scripts/calculate_progress.py --subject-id 1

# sobrescrevendo o critério de conclusão
python scripts/calculate_progress.py --subject-id 1 --token <JWT> --done-status "concluída"
```

## Dependências

Já declaradas em `requirements.txt`:
- `requests==2.34.2`
- `python-dotenv`
