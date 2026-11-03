// Add colaboradores record
query colaboradores verb=POST {
  api_group = "XANO_GUILHERME"

  input {
    dblink {
      table = "colaboradores"
    }
  }

  stack {
    db.add colaboradores {
      enforce_hidden_fields = false
      data = {
        created_at           : "now"
        nome                 : $input.nome
        papel_do_colaborador_: $input.papel_do_colaborador_
        endereco             : $input.endereco
        senha                : $input.senha
      }
    } as $model
  }

  response = $model
  guid = "WdrQK2xIOuDjeZzFdDSbVq4k_wc"
}