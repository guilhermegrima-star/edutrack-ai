// Delete papeis record.
query "papeis/{papeis_id}" verb=DELETE {
  api_group = "XANO_GUILHERME"

  input {
    int papeis_id? filters=min:1
  }

  stack {
    db.del papeis {
      field_name = "id"
      field_value = $input.papeis_id
    }
  }

  response = null
}