// Delete teste-status cliente record.
query "teste_status_cliente/{teste_status_cliente_id}" verb=DELETE {
  api_group = "XANO_GUILHERME"

  input {
    int teste_status_cliente_id? filters=min:1
  }

  stack {
    db.del "teste-status cliente" {
      field_name = "id"
      field_value = $input.teste_status_cliente_id
    }
  }

  response = null
}