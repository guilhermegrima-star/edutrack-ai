// Update academic_tasks record
query "academic_tasks/{academic_tasks_id}" verb=PUT {
  api_group = "XANO_GUILHERME"

  input {
    int academic_tasks_id? filters=min:1
    dblink {
      table = "academic_tasks"
    }
  }

  stack {
    db.edit academic_tasks {
      field_name = "id"
      field_value = $input.academic_tasks_id
      enforce_hidden_fields = false
      data = {
        title      : $input.title
        description: $input.description
        due_date   : $input.due_date
        status     : $input.status
        subject_id : $input.subject_id
      }
    } as $model
  }

  response = $model
  guid = "fWhYqi6Jy67sJphUmW3HQdidi-M"
}