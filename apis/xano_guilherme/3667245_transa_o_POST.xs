// Add TRANSAÇÃO record
query transa_o verb=POST {
  api_group = "XANO_GUILHERME"

  input {
    dblink {
      table = "TRANSAÇÃO"
    }
  }

  stack {
    db.add "TRANSAÇÃO" {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $transa_o
  }

  response = $transa_o
}