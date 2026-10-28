table colaboradores {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    text nome? filters=trim
    text papel_do_colaborador_? filters=trim
    text endereco? filters=trim
    text senha? filters=trim
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]
  guid = "gnSHTA4KxCO6Af8ilmrBUy3y8k0"
}