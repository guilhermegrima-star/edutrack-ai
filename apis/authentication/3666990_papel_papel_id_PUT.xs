// Update PAPEL record
query "papel/{papel_id}" verb=PUT {
  api_group = "Authentication"

  input {
    int papel_id? filters=min:1
    dblink {
      table = "PAPEL"
    }
  }

  stack {
    db.edit PAPEL {
      field_name = "id"
      field_value = $input.papel_id
      enforce_hidden_fields = false
      data = {PAPEL: $input.PAPEL, CREAED_ID: $input.CREAED_ID}
    } as $model
  }

  response = $model
  guid = "i0MBHSH_icmpv8l6Al0trWRJSf8"
}