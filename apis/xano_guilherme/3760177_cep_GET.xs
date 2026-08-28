// Query all CEP records
query cep verb=GET {
  api_group = "XANO_GUILHERME"

  input {
  }

  stack {
    db.query CEP {
      return = {type: "list"}
    } as $cep
  }

  response = $cep
}