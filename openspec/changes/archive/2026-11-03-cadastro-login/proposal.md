# Proposta: Autenticação de Usuário (Cadastro e Login) na Página de Perfil

## Motivação
Permitir que os utilizadores do EduTrack AI realizem cadastro e autenticação (login) diretamente pela aplicação Streamlit, criando a página `pages/3_🔒_Perfil.py`. O sistema consumirá a API de autenticação Xano já configurada (`auth/login`, `auth/signup`, `auth/me`) e salvará as informações na tabela `user`, mantendo o token de autenticação e os dados do usuário no estado da sessão (`st.session_state`).

## Escopo
- Configuração de arquivo `.env` na raiz do projeto com a URL base dos endpoints Xano (`XANO_AUTH_BASE_URL`).
- Criação e estruturação da página `pages/3_🔒_Perfil.py` no Streamlit.
- Implementação de formulário de cadastro conectado ao endpoint `POST /auth/signup` que persiste o usuário na tabela `user`.
- Implementação de formulário de login conectado ao endpoint `POST /auth/login` que obtém o token JWT (`authToken`).
- Consulta das informações do usuário autenticado via endpoint `GET /auth/me` utilizando o token Bearer.
- Exibição dos dados do perfil quando o usuário estiver autenticado (Nome, E-mail, Papel/Role, ID da conta, data de criação).
- Mecanismo de Logout para limpar a sessão e retornar ao estado deslogado.

## Não-Escopo (Non-goals)
- Modificações no schema do backend Xano ou alteração dos endpoints existentes (os endpoints e tabelas já estão prontos no Xano).
- Implementação do fluxo de recuperação de senha (`reset/*`) nesta fase (foco inicial em cadastro e login).
- Integração com OAuth ou provedores externos (Google, GitHub, etc.).

