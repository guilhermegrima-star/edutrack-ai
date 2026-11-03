// Stores student obligations associated with a subject.
table academic_tasks {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    text title filters=trim
    text description? filters=trim
    date due_date
    text status filters=trim
    int subject_id {
      table = "subjects"
    }
  
    int user_id {
      table = "user"
      visibility = "private"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {type: "btree", field: [{name: "user_id", op: "asc"}]}
    {type: "btree", field: [{name: "subject_id", op: "asc"}]}
  ]

  guid = "icY1au38QJyzw0o05cbmLUuOPdM"
}