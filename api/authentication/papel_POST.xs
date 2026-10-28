// Add PAPEL record
query papel verb=POST {
  api_group = "Authentication"

  input {
    dblink {
      table = "PAPEL"
    }
  }

  stack {
    db.add PAPEL {
      enforce_hidden_fields = false
      data = {
        created_at: "now"
        PAPEL     : $input.PAPEL
        CREAED_ID : $input.CREAED_ID
      }
    } as $model
  }

  response = $model
  guid = "kbfrnhMTZXingOGGbo6KqmA2b_Q"
}