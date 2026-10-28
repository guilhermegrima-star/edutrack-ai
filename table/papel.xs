// PAPEL
table PAPEL {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    text PAPEL? filters=trim
    timestamp? CREAED_ID?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["modulo do cadastro"]
  guid = "yTWj6u9wVSKJnVUKu-8fi2UcQ0Y"
}