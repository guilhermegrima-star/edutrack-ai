table student_reports {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
    int user_id
    attachment report_file?
    decimal summary_progress?
    text checksum?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "user_id"}]}
  ]
}

