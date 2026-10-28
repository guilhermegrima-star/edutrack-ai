// Query all colaboradores records
query colaboradores verb=GET {
  api_group = "XANO_GUILHERME"

  input {
  }

  stack {
    db.query colaboradores {
      return = {type: "list"}
    } as $model
  }

  response = $model
  guid = "dpGHgyKNjaKZzKz52-oUwnLL9k4"
}