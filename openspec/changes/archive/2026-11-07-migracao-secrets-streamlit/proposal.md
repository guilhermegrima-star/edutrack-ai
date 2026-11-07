# Proposta: Migração de Variáveis de Ambiente (.env) para Streamlit Secrets

## Motivação
Atualmente, a aplicação Streamlit do EduTrack AI (`pages/3_🔒_Perfil.py`) depende da leitura manual de arquivos `.env` e de variáveis em `os.environ` para obter as URLs da API Xano (`XANO_AUTH_BASE_URL`, `EDUTRACK_BASE_URL`). 

O ecossistema Streamlit adota como padrão seguro e nativo o gerenciamento via **`st.secrets`** (`.streamlit/secrets.toml`). O uso de `st.secrets`:
1. Facilita o deploy contínuo (Streamlit Community Cloud, Docker, Kubernetes) sem necessidade de carregar bibliotecas externas de `.env` em tempo de execução na interface.
2. Centraliza o gerenciamento de credenciais e chaves de API da aplicação em um local padronizado.
3. Permite uma arquitetura defensiva com hierarquia de precedência (`st.secrets` -> `os.environ` -> fallback padrão).

## Escopo
- Criação da pasta `.streamlit/` e do arquivo `secrets.toml` com as configurações do Xano (`XANO_AUTH_BASE_URL`, `EDUTRACK_BASE_URL`, `EDUTRACK_TASKS_PATH`).
- Criação do arquivo de modelo `secrets.toml.example` para documentar as chaves exigidas pela aplicação.
- Criação/atualização do `.gitignore` para proteger `.streamlit/secrets.toml` e arquivos `.env` contra versionamento acidental de credenciais.
- Implementação de um módulo utilitário centralizado (`utils/config.py`) para recuperação segura de chaves com precedência: `st.secrets` -> `os.environ` -> `.env` -> valor padrão.
- Refatoração de `pages/3_🔒_Perfil.py` para obter as URLs da API Xano via `st.secrets`.
- Compatibilidade contínua com os scripts Python de CLI (`scripts/calculate_progress.py` e `scripts/generate_report.py`).

## Não-Escopo (Non-goals)
- Remoção do suporte a execução por linha de comando dos scripts da pasta `scripts/` (eles manterão suporte a `os.getenv` / `.env` quando executados fora do Streamlit).

