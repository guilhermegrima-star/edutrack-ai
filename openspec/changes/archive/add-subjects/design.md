# Design Técnico: Subjects

## Estrutura de Dados
Tabela `subjects` no Xano com os campos:
- `id` (int, pk, auto)
- `name` (string)
- `teacher` (string)
- `hours` (int)
- `user_id` (int, fk -> user.id)

