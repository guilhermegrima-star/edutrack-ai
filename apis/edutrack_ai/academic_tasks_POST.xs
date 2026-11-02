// Cria uma nova tarefa acadêmica vinculada automaticamente ao usuário autenticado
query academic_tasks verb=POST {
  api_group = "edutrack.ai"
  auth = "user"

  input {
    dblink {
      table = "academic_tasks"
    }
  }

  stack {
    // Garante que a matéria informada pertence ao usuário autenticado
    db.get subjects {
      field_name = "id"
      field_value = $input.subject_id
    } as $subject

    precondition ($subject != null) {
      error_type = "notfound"
      error = "Matéria associada não encontrada"
    }

    precondition ($subject.user_id == $auth.id) {
      error_type = "accessdenied"
      error = "Acesso negado: a matéria informada não pertence a você"
    }

    // Insere a tarefa garantindo que o user_id seja o do usuário autenticado
    db.add academic_tasks {
      enforce_hidden_fields = false
      data = {
        created_at  : "now"
        user_id     : $auth.id
        subject_id  : $input.subject_id
        title       : $input.title
        description : $input.description
        due_date    : $input.due_date
        status      : $input.status
      }
    } as $model
  }

  response = $model
  tags = ["academic_tasks"]
}

