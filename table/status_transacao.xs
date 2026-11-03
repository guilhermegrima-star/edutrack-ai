// STATUS TRANSACAO
table "STATUS _TRANSACAO" {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    int statustransacao_id?
    text Status? filters=trim
    timestamp? status_created_at?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["modulo do cadastro"]
  guid = "pWvT1ygohP9dq6SUV024A2YNwnk"
}