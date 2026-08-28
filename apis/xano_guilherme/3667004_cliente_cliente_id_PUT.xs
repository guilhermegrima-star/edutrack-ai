// Update CLIENTE record
query "cliente/{cliente_id}" verb=PUT {
  api_group = "XANO_GUILHERME"

  input {
    int cliente_id? filters=min:1
    dblink {
      table = "CLIENTE"
    }
  }

  stack {
    db.edit CLIENTE {
      field_name = "id"
      field_value = $input.cliente_id
      enforce_hidden_fields = false
      data = {
        User_id          : $input.User_id
        celular          : $input.celular
        CPF              : $input.CPF
        status_cliente_id: $input.status_cliente_id
        id_user          : $input.id_user
      }
    } as $model
  }

  response = $model
}