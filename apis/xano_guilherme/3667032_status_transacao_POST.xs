// Add STATUS _TRANSACAO record
query status_transacao verb=POST {
  api_group = "XANO_GUILHERME"

  input {
    dblink {
      table = "STATUS _TRANSACAO"
    }
  }

  stack {
    db.add "STATUS _TRANSACAO" {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $status_transacao
  }

  response = $status_transacao
}