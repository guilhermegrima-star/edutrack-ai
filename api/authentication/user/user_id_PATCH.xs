// Edit User record
query "user/{user_id}" verb=PATCH {
  api_group = "Authentication"

  input {
    int user_id? filters=min:1
    dblink {
      table = "User"
    }
  }

  stack {
    util.get_raw_input {
      encoding = "json"
      exclude_middleware = false
    } as $raw_input
  
    db.patch User {
      field_name = "id"
      field_value = $input.user_id
      data = `$input|pick:($raw_input|keys)`|filter_null|filter_empty_text
    } as $user
  }

  response = $user
  guid = "THPG62ysNGxH2w5DVcUlp8pXbYQ"
}