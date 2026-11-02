table subjects {
  auth = false

  schema {
    int id
    text name
    text teacher
    int hours
    int user_id
  }

  index = [{type: "primary", field: [{name: "id"}]}]
}

