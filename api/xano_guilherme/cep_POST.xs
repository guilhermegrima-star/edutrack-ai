// Add CEP record
query cep verb=POST {
  api_group = "XANO_GUILHERME"

  input {
    dblink {
      table = "CEP"
    }
  }

  stack {
    db.add CEP {
      enforce_hidden_fields = false
      data = {created_at: "now"}
    } as $cep
  }

  response = $cep
  guid = "KI7oPXVwUCXm1YvpnfmvaZPUOQc"
}