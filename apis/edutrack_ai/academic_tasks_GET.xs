// Lista as tarefas acadêmicas pertencentes ao usuário autenticado (com filtro opcional por subject_id)
query academic_tasks verb=GET {
  api_group = "edutrack.ai"
  auth = "user"

  input {
    int subject_id?
  }

  stack {
    // Consulta tarefas filtrando estritamente pelo user_id do usuário autenticado
    conditional {
      if ($input.subject_id != null) {
        db.query academic_tasks {
          where = ($db.academic_tasks.user_id == $auth.id && $db.academic_tasks.subject_id == $input.subject_id)
          return = {type: "list"}
        } as $model
      }
      else {
        db.query academic_tasks {
          where = $db.academic_tasks.user_id == $auth.id
          return = {type: "list"}
        } as $model
      }
    }
  }

  response = $model
  tags = ["academic_tasks"]
}

