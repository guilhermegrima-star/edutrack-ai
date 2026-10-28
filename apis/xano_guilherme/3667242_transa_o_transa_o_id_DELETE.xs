// Delete TRANSAÇÃO record.
query "transa_o/{transa_o_id}" verb=DELETE {
  api_group = "XANO_GUILHERME"

  input {
    int transa_o_id? filters=min:1
  }

  stack {
    db.del "TRANSAÇÃO" {
      field_name = "id"
      field_value = $input.transa_o_id
    }
  }

  response = null
  guid = "vDuq4AEdcJRPkCR0puwykngjFkE"
}