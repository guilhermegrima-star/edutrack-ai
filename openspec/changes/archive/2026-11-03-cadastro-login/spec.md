# Especificação: Cadastro, Login e Perfil do Usuário

## Regras de Negócio e Segurança

1. **Configuração e Variáveis de Ambiente**:
   - A URL base dos endpoints de autenticação deve ser lida a partir do arquivo `.env` (variável `XANO_AUTH_BASE_URL`).
   - Se o `.env` não for encontrado ou a variável estiver ausente, a aplicação deve alertar o usuário de forma clara.

2. **Cadastro (Sign Up)**:
   - Coleta os campos: Nome completo (`name`), E-mail (`email`), Senha (`password`) e Confirmação de Senha.
   - Validações client-side:
     - As senhas informadas devem ser idênticas.
     - A senha deve cumprir os requisitos da tabela `user` do Xano: mínimo de 8 caracteres, contendo pelo menos 1 letra e 1 número.
     - O e-mail deve ter formato válido e não estar vazio.
   - Requisição à API:
     - Método: `POST`
     - Endpoint: `{XANO_AUTH_BASE_URL}/auth/signup`
     - Payload: `{"name": "<nome>", "email": "<email>", "password": "<senha>"}`
   - Comportamento de Resposta:
     - Sucesso (200 OK): Recebe `{authToken, user_id}`. Armazena o token na sessão (`st.session_state["auth_token"]`), busca os dados com `auth/me`, exibe notificação de boas-vindas e atualiza a interface para o modo autenticado.
     - Falha (403/400): Exibe aviso explicativo (ex: "Este e-mail já está em uso.").

3. **Login**:
   - Coleta os campos: E-mail (`email`) e Senha (`password`).
   - Requisição à API:
     - Método: `POST`
     - Endpoint: `{XANO_AUTH_BASE_URL}/auth/login`
     - Payload: `{"email": "<email>", "password": "<senha>"}`
   - Comportamento de Resposta:
     - Sucesso (200 OK): Recebe `{authToken, user_id}`. Armazena o token na sessão, dispara a busca do perfil via `auth/me` e recarrega a página.
     - Falha (403/401/400): Exibe mensagem de erro ("Credenciais inválidas. Verifique seu e-mail e senha.").

4. **Consulta de Perfil (auth/me) e Exibição**:
   - Requisição à API:
     - Método: `GET`
     - Endpoint: `{XANO_AUTH_BASE_URL}/auth/me`
     - Header obrigatório: `Authorization: Bearer <authToken>`
   - Retorno esperado: Registro do usuário na tabela `user` contendo `id`, `name`, `email`, `role`, `account_id`, `created_at`.
   - Exibição na página:
     - Oculta os formulários de autenticação.
     - Apresenta card com os dados do usuário conectado.
     - Botão "Sair da Conta" (Logout): Limpa o token e estado da sessão, retornando a aplicação ao estado deslogado com `st.rerun()`.

