// Add papeis record
query papeis verb=POST {
  api_group = "XANO_GUILHERME"

  input {
    dblink {
      table = "papeis"
    }
  }

  stack {
    db.add papeis {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $papeis
  }

  response = $papeis
  guid = "MpTALYJvwLXIix-o8gTeXll8JOE"
}