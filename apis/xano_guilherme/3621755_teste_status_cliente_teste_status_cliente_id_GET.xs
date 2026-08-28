// Get teste-status cliente record
query "teste_status_cliente/{teste_status_cliente_id}" verb=GET {
  api_group = "XANO_GUILHERME"

  input {
    int teste_status_cliente_id? filters=min:1
  }

  stack {
    db.get "teste-status cliente" {
      field_name = "id"
      field_value = $input.teste_status_cliente_id
    } as $teste_status_cliente
  
    precondition ($teste_status_cliente != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $teste_status_cliente
}