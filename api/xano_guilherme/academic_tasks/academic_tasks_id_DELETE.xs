// Delete academic_tasks record
query "academic_tasks/{academic_tasks_id}" verb=DELETE {
  api_group = "XANO_GUILHERME"

  input {
    int academic_tasks_id? filters=min:1
  }

  stack {
    db.del academic_tasks {
      field_name = "id"
      field_value = $input.academic_tasks_id
    }
  }

  response = null
  guid = "5JRajbx089h6ofBXYtiQ0E7PB8U"
}