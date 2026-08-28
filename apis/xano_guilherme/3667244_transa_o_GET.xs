// Query all TRANSAÇÃO records
query transa_o verb=GET {
  api_group = "XANO_GUILHERME"

  input {
  }

  stack {
    db.query "TRANSAÇÃO" {
      return = {type: "list"}
    } as $transa_o
  }

  response = $transa_o
}