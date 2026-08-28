// Add produtos record
query produtos verb=POST {
  api_group = "XANO_GUILHERME"

  input {
    dblink {
      table = "produtos"
    }
  }

  stack {
    db.add produtos {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $produtos
  }

  response = $produtos
}