import os
import re
import datetime
from pathlib import Path
import streamlit as st
import requests

# -----------------------------------------------------------------------------
# Configuração da Página
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Perfil e Autenticação - EduTrack AI",
    page_icon="🔒",
    layout="wide"
)

# -----------------------------------------------------------------------------
# Carregamento da URL Base dos Endpoints (.env)
# -----------------------------------------------------------------------------
def get_auth_base_url() -> str:
    """
    Obtém a URL base dos endpoints de autenticação Xano a partir do .env
    com suporte defensivo a múltiplos locais e fallback seguro.
    """
    # 1. Tenta obter diretamente do os.environ
    url = os.environ.get("XANO_AUTH_BASE_URL")
    if url:
        return url.rstrip("/")

    # 2. Tenta carregar usando python-dotenv se estiver instalado
    try:
        from dotenv import load_dotenv
        load_dotenv()
        url = os.environ.get("XANO_AUTH_BASE_URL")
        if url:
            return url.rstrip("/")
    except ImportError:
        pass

    # 3. Varredura manual de caminhos comuns para arquivos .env
    candidatos_env = [
        Path(".env"),
        Path(__file__).resolve().parent / ".env",
        Path(__file__).resolve().parent.parent / ".env",
        Path(__file__).resolve().parent.parent.parent / ".env",
    ]

    for env_path in candidatos_env:
        if env_path.is_file():
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("XANO_AUTH_BASE_URL="):
                            parsed_url = line.split("=", 1)[1].strip().strip('"').strip("'")
                            if parsed_url:
                                return parsed_url.rstrip("/")
            except Exception:
                continue

    # Fallback canônico do projeto Xano
    return "https://x8ki-letl-twmt.n7.xano.io/api:6Tn0YgRn"

AUTH_BASE_URL = get_auth_base_url()

# -----------------------------------------------------------------------------
# Funções de Comunicação com a API Xano (auth/login, auth/signup, auth/me)
# -----------------------------------------------------------------------------
def xano_login(email: str, password: str) -> tuple[bool, dict | str]:
    """
    Executa POST /auth/login
    Retorna (True, data) ou (False, mensagem_erro)
    """
    url = f"{AUTH_BASE_URL}/auth/login"
    payload = {
        "email": email.strip().lower(),
        "password": password
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=12)
        if response.status_code == 200:
            return True, response.json()
        
        # Trata erros retornados pelo Xano
        try:
            error_data = response.json()
            message = error_data.get("message") or error_data.get("error") or "Credenciais inválidas."
        except Exception:
            message = f"Erro no servidor ({response.status_code}): {response.text}"
        return False, message

    except requests.exceptions.RequestException as e:
        return False, f"Falha de conexão com a API de autenticação: {str(e)}"

def xano_signup(name: str, email: str, password: str) -> tuple[bool, dict | str]:
    """
    Executa POST /auth/signup salvando dados na tabela user
    Retorna (True, data) ou (False, mensagem_erro)
    """
    url = f"{AUTH_BASE_URL}/auth/signup"
    payload = {
        "name": name.strip(),
        "email": email.strip().lower(),
        "password": password
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=12)
        if response.status_code in (200, 201):
            return True, response.json()
        
        try:
            error_data = response.json()
            message = error_data.get("message") or error_data.get("error") or "Erro ao realizar cadastro."
        except Exception:
            message = f"Erro no servidor ({response.status_code}): {response.text}"
        return False, message

    except requests.exceptions.RequestException as e:
        return False, f"Falha de conexão com a API de autenticação: {str(e)}"

def xano_get_me(auth_token: str) -> tuple[bool, dict | str]:
    """
    Executa GET /auth/me usando o token Bearer
    Retorna (True, user_data) ou (False, mensagem_erro)
    """
    url = f"{AUTH_BASE_URL}/auth/me"
    headers = {
        "Authorization": f"Bearer {auth_token}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=12)
        if response.status_code == 200:
            return True, response.json()
        
        try:
            error_data = response.json()
            message = error_data.get("message") or error_data.get("error") or "Sessão inválida ou expirada."
        except Exception:
            message = f"Erro na requisição ({response.status_code}): {response.text}"
        return False, message

    except requests.exceptions.RequestException as e:
        return False, f"Falha ao conectar com o serviço de perfil: {str(e)}"

def validar_requisitos_senha(senha: str) -> tuple[bool, str]:
    """
    Valida as regras da tabela user do Xano (filters: min:8|minAlpha:1|minDigit:1).
    """
    if len(senha) < 8:
        return False, "A senha deve conter no mínimo 8 caracteres."
    if not re.search(r"[a-zA-Z]", senha):
        return False, "A senha deve conter pelo menos uma letra."
    if not re.search(r"\d", senha):
        return False, "A senha deve conter pelo menos um número."
    return True, ""

def formatar_data(timestamp_val) -> str:
    """Converte timestamps (ms ou s) para data legível."""
    if not timestamp_val:
        return "N/D"
    try:
        # Se timestamp em milissegundos
        if isinstance(timestamp_val, (int, float)) and timestamp_val > 1e11:
            timestamp_val = timestamp_val / 1000.0
        dt = datetime.datetime.fromtimestamp(float(timestamp_val))
        return dt.strftime("%d/%m/%Y às %H:%M")
    except Exception:
        return str(timestamp_val)

# -----------------------------------------------------------------------------
# Inicialização do Estado da Sessão (st.session_state)
# -----------------------------------------------------------------------------
if "auth_token" not in st.session_state:
    st.session_state["auth_token"] = None

if "user_data" not in st.session_state:
    st.session_state["user_data"] = None

# -----------------------------------------------------------------------------
# Interface do Usuário (Streamlit)
# -----------------------------------------------------------------------------
st.title("🔒 Perfil do Usuário & Autenticação")
st.caption(f"Integração com Xano API (`{AUTH_BASE_URL}`)")

# Se o usuário já possui token, exibe a tela de Perfil
if st.session_state["auth_token"]:
    user = st.session_state.get("user_data")

    # Se ainda não temos os dados do usuário, busca via /auth/me
    if not user:
        with st.spinner("Carregando informações do perfil..."):
            ok, result = xano_get_me(st.session_state["auth_token"])
            if ok:
                st.session_state["user_data"] = result
                user = result
            else:
                st.error(f"Não foi possível validar sua sessão: {result}")
                if st.button("Tentar novamente"):
                    st.session_state["auth_token"] = None
                    st.session_state["user_data"] = None
                    st.rerun()

    if user:
        st.success(f"Sessão iniciada como **{user.get('name', 'Usuário')}**")
        
        # Painel de Informações do Perfil
        st.markdown("### 👤 Dados Cadastrais")
        col1, col2 = st.columns(2)

        with col1:
            st.metric("Nome", user.get("name", "N/D"))
            st.metric("E-mail", user.get("email", "N/D"))
            st.metric("Papel / Função (Role)", (user.get("role") or "member").capitalize())

        with col2:
            st.metric("ID de Usuário", user.get("id", "N/D"))
            st.metric("ID da Conta (Workspace)", user.get("account_id") if user.get("account_id") is not None else 0)
            st.metric("Membro desde", formatar_data(user.get("created_at")))

        st.markdown("---")
        
        col_btn1, col_btn2, _ = st.columns([1, 1, 3])
        with col_btn1:
            if st.button("🔄 Atualizar Perfil", use_container_width=True):
                with st.spinner("Atualizando dados..."):
                    ok, result = xano_get_me(st.session_state["auth_token"])
                    if ok:
                        st.session_state["user_data"] = result
                        st.success("Dados atualizados!")
                        st.rerun()
                    else:
                        st.error(f"Erro ao atualizar: {result}")

        with col_btn2:
            if st.button("🚪 Sair da Conta (Logout)", type="secondary", use_container_width=True):
                st.session_state["auth_token"] = None
                st.session_state["user_data"] = None
                st.info("Você saiu da conta.")
                st.rerun()

else:
    # Fluxo Deslogado: Abas de Login e Cadastro
    st.info("Faça login com suas credenciais ou crie uma conta para acessar os recursos personalizados.")

    tab_login, tab_signup = st.tabs(["🔑 Acessar Conta (Login)", "📝 Criar Nova Conta (Cadastro)"])

    # -------------------------------------------------------------------------
    # ABA 1: LOGIN
    # -------------------------------------------------------------------------
    with tab_login:
        st.subheader("Login na Plataforma")
        with st.form("form_login"):
            email_login = st.text_input("E-mail", placeholder="seu.email@exemplo.com")
            senha_login = st.text_input("Senha", type="password", placeholder="Digite sua senha")
            botao_login = st.form_submit_button("Entrar", type="primary", use_container_width=True)

        if botao_login:
            if not email_login or not senha_login:
                st.warning("Por favor, preencha o e-mail e a senha.")
            else:
                with st.spinner("Autenticando..."):
                    sucesso, resultado = xano_login(email_login, senha_login)
                    if sucesso:
                        token = resultado.get("authToken")
                        st.session_state["auth_token"] = token
                        
                        # Imediatamente busca os dados do usuário autenticado via auth/me
                        ok_me, dados_usuario = xano_get_me(token)
                        if ok_me:
                            st.session_state["user_data"] = dados_usuario
                        
                        st.success("Login realizado com sucesso!")
                        st.rerun()
                    else:
                        st.error(f"Erro no login: {resultado}")

    # -------------------------------------------------------------------------
    # ABA 2: CADASTRO
    # -------------------------------------------------------------------------
    with tab_signup:
        st.subheader("Cadastro de Novo Usuário")
        st.markdown(
            "> **Requisitos da senha:** Mínimo de 8 caracteres, contendo pelo menos 1 letra e 1 dígito."
        )

        with st.form("form_signup"):
            nome_signup = st.text_input("Nome Completo", placeholder="Seu nome")
            email_signup = st.text_input("E-mail", placeholder="seu.email@exemplo.com")
            senha_signup = st.text_input("Senha", type="password", placeholder="Crie uma senha forte")
            confirma_senha = st.text_input("Confirme a Senha", type="password", placeholder="Repita a senha")
            botao_signup = st.form_submit_button("Cadastrar e Entrar", type="primary", use_container_width=True)

        if botao_signup:
            # Validações client-side
            if not nome_signup.strip():
                st.warning("O nome é obrigatório.")
            elif not email_signup.strip() or "@" not in email_signup:
                st.warning("Insira um endereço de e-mail válido.")
            elif senha_signup != confirma_senha:
                st.error("As senhas informadas não coincidem.")
            else:
                valida, msg_validacao = validar_requisitos_senha(senha_signup)
                if not valida:
                    st.error(msg_validacao)
                else:
                    with st.spinner("Criando conta no sistema..."):
                        sucesso, resultado = xano_signup(nome_signup, email_signup, senha_signup)
                        if sucesso:
                            token = resultado.get("authToken")
                            st.session_state["auth_token"] = token
                            
                            # Carrega perfil recém-criado
                            ok_me, dados_usuario = xano_get_me(token)
                            if ok_me:
                                st.session_state["user_data"] = dados_usuario

                            st.success("Conta criada com sucesso! Você já está autenticado.")
                            st.rerun()
                        else:
                            st.error(f"Erro no cadastro: {resultado}")

