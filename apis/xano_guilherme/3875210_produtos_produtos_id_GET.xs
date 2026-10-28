// Get produtos record
query "produtos/{produtos_id}" verb=GET {
  api_group = "XANO_GUILHERME"

  input {
    int produtos_id? filters=min:1
  }

  stack {
    db.get produtos {
      field_name = "id"
      field_value = $input.produtos_id
    } as $produtos
  
    precondition ($produtos != null) {
      error_type = "notfound"
      error = "Not Found."
    }
  }

  response = $produtos
  guid = "XkzI5FgIaw-LldYydTvASU9xpN0"
}