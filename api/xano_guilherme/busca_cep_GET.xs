// dado um novo CEP, exemplo 04048000, verificar se ele ja está presente na tabela CEP
query buscaCEP verb=GET {
  api_group = "XANO_GUILHERME"

  input {
    // CEP a ser pesquisado 
    text cep? filters=trim
  }

  stack {
    db.query CEP {
      where = $db.CEP.cep_id == $input.cep
      return = {type: "list"}
    } as $CEP1
  }

  response = $CEP1
  tags = ["modulo do cadastro"]
  guid = "bSB8ibfiy0e-KGk1rPGab_0Hhyg"
}