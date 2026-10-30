// Obtém uma tarefa acadêmica específica garantindo acesso somente aos próprios dados
query "academic_tasks/{academic_tasks_id}" verb=GET {
  api_group = "edutrack.ai"
  auth = "user"

  input {
    int academic_tasks_id? filters=min:1
  }

  stack {
    db.get academic_tasks {
      field_name = "id"
      field_value = $input.academic_tasks_id
    } as $task

    precondition ($task != null) {
      error_type = "notfound"
      error = "Tarefa acadêmica não encontrada"
    }

    precondition ($task.user_id == $auth.id) {
      error_type = "accessdenied"
      error = "Acesso negado: você só pode visualizar suas próprias tarefas acadêmicas"
    }
  }

  response = $task
  tags = ["academic_tasks"]
}

