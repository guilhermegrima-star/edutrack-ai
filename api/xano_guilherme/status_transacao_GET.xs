// Query all STATUS _TRANSACAO records
query status_transacao verb=GET {
  api_group = "XANO_GUILHERME"

  input {
  }

  stack {
    db.query "STATUS _TRANSACAO" {
      return = {type: "list"}
    } as $status_transacao
  }

  response = $status_transacao
  guid = "HVZ3uufIJwRmk_xfB7EqAiY8ztQ"
}