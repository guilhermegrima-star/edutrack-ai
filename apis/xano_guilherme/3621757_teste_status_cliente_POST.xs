// Add teste-status cliente record
query teste_status_cliente verb=POST {
  api_group = "XANO_GUILHERME"

  input {
    dblink {
      table = "teste-status cliente"
    }
  }

  stack {
    db.add "teste-status cliente" {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $teste_status_cliente
  }

  response = $teste_status_cliente
  guid = "Ssp5Eu1acgHZK98Wo0ccyhqQqbY"
}