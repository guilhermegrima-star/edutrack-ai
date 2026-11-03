// Query all produtos records
query produtos verb=GET {
  api_group = "XANO_GUILHERME"

  input {
  }

  stack {
    db.query produtos {
      return = {type: "list"}
    } as $produtos
  }

  response = $produtos
  guid = "KsmygdX2WHWykq_uBwOzwBYNLb0"
}