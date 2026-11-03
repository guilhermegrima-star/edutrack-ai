// Delete User record.
query "user/{user_id}" verb=DELETE {
  api_group = "Authentication"

  input {
    int user_id? filters=min:1
  }

  stack {
    db.del User {
      field_name = "id"
      field_value = $input.user_id
    }
  }

  response = null
  guid = "dZHKsBdimHmt5UVT5Y9cumAGH0o"
}