// Dado um AuthToken, devolve dados do cliente 
query buscaCliente verb=GET {
  api_group = "XANO_GUILHERME"

  input {
    // Token de Autenticação 
    text AuthToken? filters=trim
  }

  stack {
    api.request {
      url = "https://x8ki-letl-twmt.n7.xano.io/api:bnkH1BQp/auth/me"
      method = "GET"
      params = $input.AuthToken
      headers = []["Authorization: Bearer " ~ $input.authtoken,"Content-Type: application/json"]
    } as $api1
  
    conditional {
      if () {
        db.get CLIENTE {
          field_name = "id"
          field_value = "$var.api1.response.result.id"
        } as $CLIENTE1
      }
    
      else {
        var $CLIENTE1 {
          value = {}
        }
      }
    }
  }

  response = {result1: $api1, CL: $CLIENTE1}
  tags = ["modulo do cadastro"]
}