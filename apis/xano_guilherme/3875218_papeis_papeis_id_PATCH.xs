// Edit papeis record
query "papeis/{papeis_id}" verb=PATCH {
  api_group = "XANO_GUILHERME"

  input {
    int papeis_id? filters=min:1
    dblink {
      table = "papeis"
    }
  }

  stack {
    util.get_raw_input {
      encoding = "json"
      exclude_middleware = false
    } as $raw_input
  
    db.patch papeis {
      field_name = "id"
      field_value = $input.papeis_id
      data = `$input|pick:($raw_input|keys)`|filter_null|filter_empty_text
    } as $papeis
  }

  response = $papeis
}