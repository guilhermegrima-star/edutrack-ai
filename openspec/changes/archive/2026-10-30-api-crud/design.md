# Design Técnico: API CRUD e Controle de Acesso

## Estrutura das Tabelas

### `tables/subjects.xs`
- `id` (int, pk)
- `name` (text)
- `teacher` (text)
- `hours` (int)
- `user_id` (int)

### `tables/academic_tasks.xs`
- `id` (int, pk)
- `created_at` (timestamp, private)
- `user_id` (int, fk -> user.id)
- `subject_id` (int, fk -> subjects.id)
- `title` (text)
- `description` (text, opcional)
- `due_date` (timestamp, opcional)
- `status` (text, opcional)

## Padrão de Segurança e Preconditions no XanoScript

Para operações pontuais (`GET /{id}`, `PATCH /{id}`, `DELETE /{id}`):
```xs
db.get <table> {
  field_name = "id"
  field_value = $input.<id>
} as $record

precondition ($record != null) {
  error_type = "notfound"
  error = "Registro não encontrado"
}

precondition ($record.user_id == $auth.id) {
  error_type = "accessdenied"
  error = "Acesso negado: você só pode acessar seus próprios dados"
}
```

Para listagens (`GET`):
```xs
db.query <table> {
  where = $db.<table>.user_id == $auth.id
  return = {type: "list"}
} as $model
```

