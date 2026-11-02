// Lista todas as matérias (subjects) pertencentes ao usuário autenticado
query subjects verb=GET {
  api_group = "edutrack.ai"
  auth = "user"

  input {
  }

  stack {
    // Consulta apenas matérias do usuário autenticado
    db.query subjects {
      where = $db.subjects.user_id == $auth.id
      return = {type: "list"}
    } as $model
  }

  response = $model
  tags = ["subjects"]
}

