// Exclui uma tarefa acadêmica garantindo que o usuário só exclua seus próprios dados
query "academic_tasks/{academic_tasks_id}" verb=DELETE {
  api_group = "edutrack.ai"
  auth = "user"

  input {
    int academic_tasks_id? filters=min:1
  }

  stack {
    // Busca a tarefa para verificar existência e pertencimento
    db.get academic_tasks {
      field_name = "id"
      field_value = $input.academic_tasks_id
    } as $task

    // Verifica se a tarefa existe
    precondition ($task != null) {
      error_type = "notfound"
      error = "Tarefa acadêmica não encontrada"
    }

    // Garante que o usuário só exclua seus próprios dados
    precondition ($task.user_id == $auth.id) {
      error_type = "accessdenied"
      error = "Acesso negado: você só pode excluir suas próprias tarefas acadêmicas"
    }

    // Exclui a tarefa
    db.del academic_tasks {
      field_name = "id"
      field_value = $input.academic_tasks_id
    }
  }

  response = null
  tags = ["academic_tasks"]
}

