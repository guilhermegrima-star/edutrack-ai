// Query all teste-status cliente records
query teste_status_cliente verb=GET {
  api_group = "XANO_GUILHERME"

  input {
  }

  stack {
    db.query "teste-status cliente" {
      return = {type: "list"}
    } as $teste_status_cliente
  }

  response = $teste_status_cliente
}