# Especificação: Configurações via Streamlit Secrets

## 1. Chaves de Configuração
As seguintes chaves devem ser suportadas tanto em `.streamlit/secrets.toml` quanto como variáveis de ambiente:

| Chave | Descrição | Valor Padrão / Canônico |
|---|---|---|
| `XANO_AUTH_BASE_URL` | URL base do grupo de autenticação Xano | `https://x8ki-letl-twmt.n7.xano.io/api:6Tn0YgRn` |
| `EDUTRACK_BASE_URL` | URL base do grupo de dados acadêmicos | `https://x8ki-letl-twmt.n7.xano.io/api:gTfD518O` |
| `EDUTRACK_TASKS_PATH` | Segmento de path para o endpoint de tarefas | `task` |
| `EDUTRACK_TOKEN` | Token JWT opcional para automações | `""` |

## 2. Formato do `.streamlit/secrets.toml`
```toml
# ==============================================================================
# EduTrack AI - Streamlit Secrets Configuration
# ==============================================================================

# API de Autenticação Xano (login, signup, me)
XANO_AUTH_BASE_URL = "https://x8ki-letl-twmt.n7.xano.io/api:6Tn0YgRn"

# API Principal de Gestão Acadêmica (subjects, tasks, reports)
EDUTRACK_BASE_URL = "https://x8ki-letl-twmt.n7.xano.io/api:gTfD518O"

# Path do recurso de tarefas acadêmicas
EDUTRACK_TASKS_PATH = "task"
```

## 3. Ordem de Precedência de Resolução
Para qualquer chave solicitada via `get_setting(key, default)`:
1. `st.secrets[key]` (quando executado no contexto Streamlit e chave presente).
2. `os.environ.get(key)` (variáveis de ambiente do sistema operacional ou container).
3. Arquivo `.env` carregado via `python-dotenv` (para compatibilidade legada e CLI).
4. `default` fornecido na chamada.

## 4. Diretrizes de Segurança
- O arquivo `.streamlit/secrets.toml` NÃO DEVE ser rastreado no controle de versão Git.
- O arquivo `.streamlit/secrets.toml.example` DEVE ser commitado com valores de exemplo seguros.
- O `.gitignore` na raiz do projeto e/ou pasta `edutrack-ai` deve conter:
  ```gitignore
  .streamlit/secrets.toml
  .env
  .env.*
  ```

