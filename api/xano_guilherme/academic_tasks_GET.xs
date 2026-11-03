// Query all academic_tasks records
query academic_tasks verb=GET {
  api_group = "XANO_GUILHERME"

  input {
  }

  stack {
    db.query academic_tasks {
      return = {type: "list"}
    } as $model
  }

  response = $model
  guid = "qs0_ndNIh6Qg6rihmd1Gs2Q3iiM"
}