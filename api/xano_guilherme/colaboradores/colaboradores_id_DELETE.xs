// Delete colaboradores record
query "colaboradores/{colaboradores_id}" verb=DELETE {
  api_group = "XANO_GUILHERME"

  input {
    int colaboradores_id? filters=min:1
  }

  stack {
    db.del colaboradores {
      field_name = "id"
      field_value = $input.colaboradores_id
    }
  }

  response = null
  guid = "DxgJBHBKFia-a5Kc6FLFHv1f3ZE"
}