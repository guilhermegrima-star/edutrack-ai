// Consulta e disponibiliza o relatório acadêmico em PDF do usuário autenticado
query student_report verb=GET {
  api_group = "edutrack.ai"
  auth = "user"

  input {
    int report_id?
  }

  stack {
    conditional {
      if ($input.report_id != null) {
        db.get student_reports {
          field_name = "id"
          field_value = $input.report_id
        } as $report

        precondition ($report != null) {
          error_type = "notfound"
          error = "Relatório acadêmico não encontrado"
        }

        precondition ($report.user_id == $auth.id) {
          error_type = "accessdenied"
          error = "Acesso negado: o relatório informado não pertence a você"
        }

        var $model {
          value = $report
        }
      }
      else {
        db.query student_reports {
          where = $db.student_reports.user_id == $auth.id
          sort = {created_at: "desc"}
          return = {type: "single"}
        } as $model

        precondition ($model != null) {
          error_type = "notfound"
          error = "Nenhum relatório acadêmico encontrado para este aluno"
        }
      }
    }
  }

  response = $model
  tags = ["student_reports"]
}

