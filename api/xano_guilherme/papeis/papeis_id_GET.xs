// Get papeis record
query "papeis/{papeis_id}" verb=GET {
  api_group = "XANO_GUILHERME"

  input {
    int papeis_id? filters=min:1
  }

  stack {
    db.get papeis {
      field_name = "id"
      field_value = $input.papeis_id
    } as $papeis
  
    precondition ($papeis != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $papeis
  guid = "4T5Hc2eSdAxCLE6WvbaP0FHiSL8"
}