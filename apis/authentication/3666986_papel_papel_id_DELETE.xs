// Delete PAPEL record
query "papel/{papel_id}" verb=DELETE {
  api_group = "Authentication"

  input {
    int papel_id? filters=min:1
  }

  stack {
    db.del PAPEL {
      field_name = "id"
      field_value = $input.papel_id
    }
  }

  response = null
  guid = "K2plPIxT7pb-BPm97V-a8P4w75c"
}