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
  guid = "1WI1jlRU5b0e2A-LCQufabGgW4o"
}