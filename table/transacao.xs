// TRANSAÇÃO
table "TRANSAÇÃO" {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    int transacao_id?
    text clienteassas? filters=trim
    text idpayment? filters=trim
    text tipo? filters=trim
    int valor?
    text datavenc? filters=trim
    text descricao? filters=trim
    int statustransacao_id?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["modulo do cadastro"]
  guid = "fmK35kFw8U9HfWt-ypHJmp2qolU"
}