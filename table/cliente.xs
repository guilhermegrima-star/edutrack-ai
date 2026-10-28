// CADASTRO DO CLIENTE
table CLIENTE {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    int User_id?
    text celular? filters=trim
    text CPF? filters=trim
    int status_cliente_id? {
      table = "teste-status cliente"
    }
  
    int id_user? {
      table = "user"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]

  tags = ["modulo do cadastro"]
  guid = "e9TN0r1zXA-3ZKqoN6js4Zz6-TE"
}