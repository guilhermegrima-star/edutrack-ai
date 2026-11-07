# Design Técnico: Migração para Streamlit Secrets

## Visão Geral da Arquitetura
A arquitetura substitui o parsing ad-hoc de arquivos `.env` na camada de interface por um padrão centralizado e unificado através do Streamlit Secrets (`st.secrets`), mantendo compatibilidade transparente com scripts CLI independentes.

```
                           +--------------------------------+
                           |   Chamada da Aplicação / UI    |
                           |  (pages/3_🔒_Perfil.py / app)  |
                           +--------------------------------+
                                           |
                                           v
                           +--------------------------------+
                           |     utils.config.get_setting   |
                           +--------------------------------+
                                  /        |        \
                   (1ª Opção)   /          |          \   (3ª Opção)
                              v            |            v
                     +------------+        |      +-------------+
                     | st.secrets |        |      | .env / os.  |
                     | (.streamlit|        |      |   environ   |
                     |/secrets.   |        |      +-------------+
                     |  toml)     |        |            |
                     +------------+        v            v
                                    (2ª Opção:    (Fallback:
                                     os.environ)   default)
```

## Componentes

### 1. Diretório e Arquivos `.streamlit/`
- **`.streamlit/secrets.toml`**: Arquivo local com as chaves reais de configuração da aplicação.
- **`.streamlit/secrets.toml.example`**: Arquivo versionado no Git contendo modelo/esqueleto documentado para novos desenvolvedores e deploys.

### 2. Módulo Centralizado `utils/config.py`
Funções utilitárias seguras:
- `get_setting(key: str, default: str = "") -> str`:
  1. Verifica se o Streamlit está em execução e se a chave existe em `st.secrets` (nível superior ou seções toml).
  2. Verifica `os.environ.get(key)`.
  3. Tenta carregar `.env` via `python-dotenv` se ainda não carregado.
  4. Retorna o valor default seguro caso nenhuma fonte defina a chave.
- `get_xano_auth_url() -> str`: URL canônica do serviço de autenticação (`XANO_AUTH_BASE_URL`).
- `get_edutrack_base_url() -> str`: URL base do grupo acadêmico (`EDUTRACK_BASE_URL`).
- `get_tasks_path() -> str`: Segmento de rota de tarefas (`EDUTRACK_TASKS_PATH`).

### 3. Refatoração em `pages/3_🔒_Perfil.py`
- Substituição da função legada `get_auth_base_url()` pelo consumo direto de `get_xano_auth_url()` de `utils.config` (ou leitura prioritária de `st.secrets["XANO_AUTH_BASE_URL"]`).

### 4. Segurança com `.gitignore`
- Proteção explícita de `.streamlit/secrets.toml` e `.env` para evitar vazamento acidental em repositórios remotos.

