// Cria uma nova matéria (subject) vinculada automaticamente ao usuário autenticado
query subjects verb=POST {
  api_group = "edutrack.ai"
  auth = "user"

  input {
    dblink {
      table = "subjects"
    }
  }

  stack {
    // Insere a matéria garantindo que o user_id seja o usuário autenticado
    db.add subjects {
      enforce_hidden_fields = false
      data = {
        name    : $input.name
        teacher : $input.teacher
        hours   : $input.hours
        user_id : $auth.id
      }
    } as $model
  }

  response = $model
  tags = ["subjects"]
}

