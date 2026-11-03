// Add CLIENTE record
query cliente verb=POST {
  api_group = "XANO_GUILHERME"

  input {
    dblink {
      table = "CLIENTE"
    }
  }

  stack {
    db.add CLIENTE {
      enforce_hidden_fields = false
      data = {
        created_at       : "now"
        User_id          : $input.User_id
        celular          : $input.celular
        CPF              : $input.CPF
        status_cliente_id: $input.status_cliente_id
        id_user          : $input.id_user
      }
    } as $model
  }

  response = $model
  guid = "24S6uXP2TSXalSnY0s-CLg6IcZw"
}