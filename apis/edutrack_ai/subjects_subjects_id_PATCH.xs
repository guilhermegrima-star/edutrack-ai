// Atualiza uma matéria (subject) garantindo que o usuário só altere seus próprios dados
query "subjects/{subjects_id}" verb=PATCH {
  api_group = "edutrack.ai"
  auth = "user"

  input {
    int subjects_id? filters=min:1
    dblink {
      table = "subjects"
    }
  }

  stack {
    // Busca a matéria para verificar existência e pertencimento
    db.get subjects {
      field_name = "id"
      field_value = $input.subjects_id
    } as $subject

    // Verifica se a matéria existe
    precondition ($subject != null) {
      error_type = "notfound"
      error = "Matéria não encontrada"
    }

    // Garante que o usuário só acesse e altere seus próprios dados
    precondition ($subject.user_id == $auth.id) {
      error_type = "accessdenied"
      error = "Acesso negado: você só pode alterar suas próprias matérias"
    }

    util.get_raw_input {
      encoding = "json"
      exclude_middleware = false
    } as $raw_input

    // Atualiza os dados da matéria mantendo o user_id do usuário autenticado
    db.patch subjects {
      field_name = "id"
      field_value = $input.subjects_id
      data = (`$input|pick:($raw_input|keys)`|filter_null|filter_empty_text)|set:"user_id":$auth.id
    } as $model
  }

  response = $model
  tags = ["subjects"]
}

