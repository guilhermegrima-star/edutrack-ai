// Delete CLIENTE record
query "cliente/{cliente_id}" verb=DELETE {
  api_group = "XANO_GUILHERME"

  input {
    int cliente_id? filters=min:1
  }

  stack {
    db.del CLIENTE {
      field_name = "id"
      field_value = $input.cliente_id
    }
  }

  response = null
  guid = "DbBFaj-PS09TLkq42wEqgVJnwDU"
}