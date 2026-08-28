// Get colaboradores record
query "colaboradores/{colaboradores_id}" verb=GET {
  api_group = "XANO_GUILHERME"

  input {
    int colaboradores_id? filters=min:1
  }

  stack {
    db.get colaboradores {
      field_name = "id"
      field_value = $input.colaboradores_id
    } as $model
  
    precondition ($model != null) {
      error_type = "notfound"
      error = "Not Found"
    }
  }

  response = $model
}