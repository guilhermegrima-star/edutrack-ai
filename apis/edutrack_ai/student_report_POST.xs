// Registra e realiza o upload de um relatório acadêmico em PDF para o usuário autenticado
query student_report verb=POST {
  api_group = "edutrack.ai"
  auth = "user"

  input {
    attachment report_file
    decimal summary_progress?
    text checksum?
  }

  stack {
    db.add student_reports {
      enforce_hidden_fields = false
      data = {
        created_at       : "now"
        user_id          : $auth.id
        report_file      : $input.report_file
        summary_progress : $input.summary_progress
        checksum         : $input.checksum
      }
    } as $model
  }

  response = $model
  tags = ["student_reports"]
}

