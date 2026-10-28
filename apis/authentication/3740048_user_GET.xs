// Query all User records
query user verb=GET {
  api_group = "Authentication"

  input {
  }

  stack {
    db.query User {
      return = {type: "list"}
    } as $user
  }

  response = $user
  guid = "7TOvdx8RZtiI4iDL-aElflZpmho"
}