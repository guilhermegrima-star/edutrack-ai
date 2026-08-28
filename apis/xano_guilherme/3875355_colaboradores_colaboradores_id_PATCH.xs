// Edit colaboradores record
query "colaboradores/{colaboradores_id}" verb=PATCH {
  api_group = "XANO_GUILHERME"

  input {
    int colaboradores_id? filters=min:1
    dblink {
      table = "colaboradores"
    }
  }

  stack {
    util.get_raw_input {
      encoding = "json"
      exclude_middleware = false
    } as $raw_input
  
    db.patch colaboradores {
      field_name = "id"
      field_value = $input.colaboradores_id
      data = `$input|pick:($raw_input|keys)`|filter_null|filter_empty_text
    } as $model
  }

  response = $model
}