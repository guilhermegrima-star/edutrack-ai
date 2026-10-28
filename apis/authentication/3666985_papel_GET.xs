// Query all PAPEL records
query papel verb=GET {
  api_group = "Authentication"

  input {
  }

  stack {
    db.query PAPEL {
      return = {type: "list"}
    } as $model
  }

  response = $model
  guid = "UxsgMb30Ya4XCJpXclG-LB9eOeE"
}