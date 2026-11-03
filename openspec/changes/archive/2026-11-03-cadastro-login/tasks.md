# Tarefas de Implementação: Cadastro e Login

- [x] 1. Configurar variáveis de ambiente e dependências
  - [x] 1.1 Criar arquivo `.env` na raiz com `XANO_AUTH_BASE_URL=https://x8ki-letl-twmt.n7.xano.io/api:6Tn0YgRn`
  - [x] 1.2 Atualizar `requirements.txt` se necessário para incluir `python-dotenv` (e manter `requests` e `streamlit`)

- [x] 2. Desenvolver módulo de comunicação com a API de Autenticação
  - [x] 2.1 Implementar carregamento seguro de variáveis com fallback via `dotenv` / `os.getenv`
  - [x] 2.2 Implementar método para chamada ao endpoint `POST /auth/login`
  - [x] 2.3 Implementar método para chamada ao endpoint `POST /auth/signup`
  - [x] 2.4 Implementar método para chamada ao endpoint `GET /auth/me` com cabeçalho de autorização Bearer

- [x] 3. Implementar a página Streamlit `pages/3_🔒_Perfil.py`
  - [x] 3.1 Criar o diretório `pages/` (caso não exista) e o arquivo `3_🔒_Perfil.py`
  - [x] 3.2 Inicializar variáveis no `st.session_state` (`auth_token`, `user`, `authenticated`)
  - [x] 3.3 Construir a interface de login com validações de entrada e tratamento de resposta
  - [x] 3.4 Construir a interface de cadastro com validação de senha (mínimo 8 caracteres, letra e número) e tratamento de resposta
  - [x] 3.5 Construir a visualização do perfil para o usuário conectado com os dados retornados de `auth/me`
  - [x] 3.6 Implementar ação de Logout com limpeza de sessão e recarregamento (`st.rerun`)

- [x] 4. Validação e Testes Integrados
  - [x] 4.1 Estrutura e rotas da página preparadas para `streamlit run app.py`
  - [x] 4.2 Lógica de cadastro vinculada a `POST /auth/signup` e tabela `user`
  - [x] 4.3 Lógica de login vinculada a `POST /auth/login` e consulta subsequente a `GET /auth/me`
  - [x] 4.4 Tratamento amigável de erros e validações de integridade de senha implementadas
  - [x] 4.5 Mecanismo de logout com limpeza de estado da sessão
