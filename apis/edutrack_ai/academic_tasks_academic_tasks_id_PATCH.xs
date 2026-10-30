// Atualiza uma tarefa acadêmica garantindo que o usuário só altere seus próprios dados
query "academic_tasks/{academic_tasks_id}" verb=PATCH {
  api_group = "edutrack.ai"
  auth = "user"

  input {
    int academic_tasks_id? filters=min:1
    dblink {
      table = "academic_tasks"
    }
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

    // Garante que o usuário só acesse e altere seus próprios dados
    precondition ($task.user_id == $auth.id) {
      error_type = "accessdenied"
      error = "Acesso negado: você só pode alterar suas próprias tarefas acadêmicas"
    }

    // Se houver alteração de subject_id, garante que a nova matéria também pertence ao usuário
    conditional {
      if ($input.subject_id != null) {
        db.get subjects {
          field_name = "id"
          field_value = $input.subject_id
        } as $target_subject

        precondition ($target_subject != null && $target_subject.user_id == $auth.id) {
          error_type = "accessdenied"
          error = "A matéria associada não existe ou não pertence a você"
        }
      }
    }

    util.get_raw_input {
      encoding = "json"
      exclude_middleware = false
    } as $raw_input

    // Atualiza os dados da tarefa mantendo o user_id do usuário autenticado
    db.patch academic_tasks {
      field_name = "id"
      field_value = $input.academic_tasks_id
      data = (`$input|pick:($raw_input|keys)`|filter_null|filter_empty_text)|set:"user_id":$auth.id
    } as $model
  }

  response = $model
  tags = ["academic_tasks"]
}

