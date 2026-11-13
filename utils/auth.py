"""
utils/auth.py
-------------
Módulo centralizado de autenticação do EduTrack AI com a API Xano.
Centraliza as funções de login, signup, verificação de sessão e guarda de páginas.
"""

from __future__ import annotations
import re
from typing import Any
import requests
import streamlit as st

try:
    from utils.config import get_xano_auth_url
except ImportError:
    AUTH_BASE_URL = "https://x8ki-letl-twmt.n7.xano.io/api:6Tn0YgRn"
else:
    AUTH_BASE_URL = get_xano_auth_url()


def xano_login(email: str, password: str) -> tuple[bool, dict | str]:
    """
    Executa POST /auth/login na API Xano.
    Retorna (True, data) ou (False, mensagem_erro).
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
        
        try:
            error_data = response.json()
            message = error_data.get("message") or error_data.get("error") or "Credenciais inválidas. Verifique seu e-mail e senha."
        except Exception:
            message = f"Erro no servidor ({response.status_code}): {response.text}"
        return False, message

    except requests.exceptions.RequestException as e:
        return False, f"Falha de conexão com a API de autenticação: {str(e)}"


def xano_signup(name: str, email: str, password: str) -> tuple[bool, dict | str]:
    """
    Executa POST /auth/signup na API Xano salvando dados na tabela user.
    Retorna (True, data) ou (False, mensagem_erro).
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
    Executa GET /auth/me usando o token Bearer.
    Retorna (True, user_data) ou (False, mensagem_erro).
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
    Valida as regras de senha do Xano (mínimo 8 caracteres, 1 letra e 1 dígito).
    """
    if len(senha) < 8:
        return False, "A senha deve conter no mínimo 8 caracteres."
    if not re.search(r"[a-zA-Z]", senha):
        return False, "A senha deve conter pelo menos uma letra."
    if not re.search(r"\d", senha):
        return False, "A senha deve conter pelo menos um número."
    return True, ""


def init_session_state():
    """Inicializa as variáveis de sessão essenciais para autenticação."""
    if "auth_token" not in st.session_state:
        st.session_state["auth_token"] = None
    if "user_data" not in st.session_state:
        st.session_state["user_data"] = None


def is_authenticated() -> bool:
    """Verifica se há um usuário autenticado na sessão."""
    init_session_state()
    return bool(st.session_state.get("auth_token"))


def get_current_user() -> dict | None:
    """Retorna os dados do usuário atual na sessão."""
    init_session_state()
    return st.session_state.get("user_data")


def perform_logout():
    """Limpa as variáveis de sessão e recarrega a página para o estado deslogado."""
    st.session_state["auth_token"] = None
    st.session_state["user_data"] = None
    st.session_state.pop("cached_pdf_bytes", None)
    st.session_state.pop("cached_pdf_name", None)
    st.session_state.pop("pdf_aluno_bytes", None)
    st.session_state.pop("pdf_aluno_nome", None)
    st.rerun()


def guard_authenticated_page(page_name: str = "esta página"):
    """
    Bloqueia o acesso direto a páginas secundárias para usuários deslogados.
    Exibe orientação amigável sem formulários de login/cadastro locais.
    """
    if not is_authenticated():
        st.markdown(
            f"""
            <div style="
                background: #FFFFFF;
                border-radius: 18px;
                padding: 40px 32px;
                text-align: center;
                max-width: 600px;
                margin: 60px auto;
                border: 1px solid #E2E8F0;
                box-shadow: 0 10px 25px rgba(0,0,0,0.05);
            ">
                <div style="font-size: 48px; margin-bottom: 16px;">🔒</div>
                <h2 style="color: #38337A; font-weight: 800; margin-bottom: 8px;">Acesso Restrito</h2>
                <p style="color: #64748B; font-size: 15px; line-height: 1.6; margin-bottom: 24px;">
                    Para acessar {page_name}, você precisa estar autenticado na plataforma.
                    O login e cadastro são realizados exclusivamente através da <b>Página Principal</b>.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("⬅️ Ir para a Página Principal de Login", type="primary", use_container_width=True):
                if hasattr(st, "switch_page"):
                    try:
                        st.switch_page("app.py")
                    except Exception:
                        pass
        st.stop()
