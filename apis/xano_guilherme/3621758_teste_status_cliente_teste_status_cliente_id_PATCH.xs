// Edit teste-status cliente record
query "teste_status_cliente/{teste_status_cliente_id}" verb=PATCH {
  api_group = "XANO_GUILHERME"

  input {
    int teste_status_cliente_id? filters=min:1
    dblink {
      table = "teste-status cliente"
    }
  }

  stack {
    util.get_raw_input {
      encoding = "json"
      exclude_middleware = false
    } as $raw_input
  
    db.patch "teste-status cliente" {
      field_name = "id"
      field_value = $input.teste_status_cliente_id
      data = `$input|pick:($raw_input|keys)`|filter_null|filter_empty_text
    } as $teste_status_cliente
  }

  response = $teste_status_cliente
  guid = "rXbyJU9kO5Lul2ruirGRq9L46qI"
}