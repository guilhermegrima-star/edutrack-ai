table CEP {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    int cep_id?
    text CEP? filters=trim
    text UF? filters=trim
    text cidade? filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["modulo do cadastro"]
  guid = "6EvYLlnbnOwdVSU8suZb7-mFXss"
}