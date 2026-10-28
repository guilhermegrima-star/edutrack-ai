// Query all papeis records
query papeis verb=GET {
  api_group = "XANO_GUILHERME"

  input {
  }

  stack {
    db.query papeis {
      return = {type: "list"}
    } as $papeis
  }

  response = $papeis
  guid = "neNCPQ6zF2ca7MFkzJfvV56d2zY"
}