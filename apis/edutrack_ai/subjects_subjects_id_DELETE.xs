// Exclui uma matéria (subject) garantindo que o usuário só exclua seus próprios dados
query "subjects/{subjects_id}" verb=DELETE {
  api_group = "edutrack.ai"
  auth = "user"

  input {
    int subjects_id? filters=min:1
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

    // Garante que o usuário só exclua seus próprios dados
    precondition ($subject.user_id == $auth.id) {
      error_type = "accessdenied"
      error = "Acesso negado: você só pode excluir suas próprias matérias"
    }

    // Exclui a matéria
    db.del subjects {
      field_name = "id"
      field_value = $input.subjects_id
    }
  }

  response = null
  tags = ["subjects"]
}

