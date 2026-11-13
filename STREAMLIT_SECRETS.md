# Configuração de Secrets do Streamlit

Este projeto usa `st.secrets` como fonte principal de configuração sensível para a aplicação Streamlit.

## Objetivo

Centralizar URLs, tokens e demais valores privados em um único arquivo de segredos, evitando o uso de `.env` em produção e mantendo a aplicação compatível com deploys do Streamlit.

## Arquivo de configuração

O arquivo real de segredos fica em:

- `.streamlit/secrets.toml`

O template de exemplo, versionado no repositório, fica em:

- `.streamlit/secrets.toml.example`

## Estrutura esperada

```toml
XANO_AUTH_BASE_URL = "https://x8ki-letl-twmt.n7.xano.io/api:6Tn0YgRn"
EDUTRACK_BASE_URL = "https://x8ki-letl-twmt.n7.xano.io/api:gTfD518O"
EDUTRACK_TASKS_PATH = "task"
# EDUTRACK_TOKEN = "seu_jwt_token_aqui"
```

## Regras de uso

- O arquivo `.streamlit/secrets.toml` não deve ser commitado.
- O arquivo `.streamlit/secrets.toml.example` deve ser usado como referência.
- O projeto lê primeiro `st.secrets`, depois pode continuar usando variáveis do ambiente como fallback não prioritário.
- O diretório `.streamlit/` está protegido no `.gitignore`.

## Importante

A leitura da aplicação prioriza:

1. `st.secrets`
2. `os.environ`
3. fallback local

Esse comportamento está centralizado em `utils/config.py`.

## Exemplo de uso em deploy

No Streamlit Cloud ou em qualquer ambiente de produção, configure os segredos através da interface do painel de secrets do projeto ou do arquivo `secrets.toml` localmente durante desenvolvimento.

## Segurança

- Nunca commitar valores reais de credenciais.
- Não compartilhar tokens ou URLs privadas em issues, mensagens ou logs.
- Manter `.streamlit/secrets.toml` fora do controle de versão.
