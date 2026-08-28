// Update colaboradores record
query "colaboradores/{colaboradores_id}" verb=PUT {
  api_group = "XANO_GUILHERME"

  input {
    int colaboradores_id? filters=min:1
    dblink {
      table = "colaboradores"
    }
  }

  stack {
    db.edit colaboradores {
      field_name = "id"
      field_value = $input.colaboradores_id
      enforce_hidden_fields = false
      data = {
        nome                 : $input.nome
        papel_do_colaborador_: $input.papel_do_colaborador_
        endereco             : $input.endereco
        senha                : $input.senha
      }
    } as $model
  }

  response = $model
}