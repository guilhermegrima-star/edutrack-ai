// Obtém uma matéria específica (subject) garantindo acesso somente aos próprios dados
query "subjects/{subjects_id}" verb=GET {
  api_group = "edutrack.ai"
  auth = "user"

  input {
    int subjects_id? filters=min:1
  }

  stack {
    db.get subjects {
      field_name = "id"
      field_value = $input.subjects_id
    } as $subject

    precondition ($subject != null) {
      error_type = "notfound"
      error = "Matéria não encontrada"
    }

    precondition ($subject.user_id == $auth.id) {
      error_type = "accessdenied"
      error = "Acesso negado: você só pode visualizar suas próprias matérias"
    }
  }

  response = $subject
  tags = ["subjects"]
}

