// Delete CEP record.
query "cep/{cep_id}" verb=DELETE {
  api_group = "XANO_GUILHERME"

  input {
    int cep_id? filters=min:1
  }

  stack {
    db.del CEP {
      field_name = "id"
      field_value = $input.cep_id
    }
  }

  response = null
  guid = "2TU4mfUv41jfx32UEw8gT2dMZOg"
}