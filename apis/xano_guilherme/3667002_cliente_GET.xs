// Query all CLIENTE records
query cliente verb=GET {
  api_group = "XANO_GUILHERME"

  input {
  }

  stack {
    db.query CLIENTE {
      return = {type: "list"}
    } as $model
  }

  response = $model
}