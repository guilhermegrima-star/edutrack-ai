# Especificação: Subjects

## Regras de Negócio
- A tabela deve guardar matérias do sistema.
- Cada matéria pertence a um utilizador autenticado (`user_id`).

## Campos
- `id`: Identificador único (auto increment).
- `name`: Nome da matéria (texto).
- `teacher`: Nome do professor (texto).
- `hours`: Carga horária (inteiro).
- `user_id`: Chave estrangeira para a tabela de autenticação do Xano (`user`/`users`).

