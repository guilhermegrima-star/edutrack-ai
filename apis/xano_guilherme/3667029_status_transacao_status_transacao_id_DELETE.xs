// Delete STATUS _TRANSACAO record.
query "status_transacao/{status_transacao_id}" verb=DELETE {
  api_group = "XANO_GUILHERME"

  input {
    int status_transacao_id? filters=min:1
  }

  stack {
    db.del "STATUS _TRANSACAO" {
      field_name = "id"
      field_value = $input.status_transacao_id
    }
  }

  response = null
  guid = "2mOG63bz_hWI1O3d860Et47tFPU"
}