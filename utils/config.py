"""
utils/config.py
---------------
Gerenciador centralizado de configurações e segredos do EduTrack AI.

Hierarquia de resolução:
1. Streamlit Secrets (st.secrets)
2. Variáveis de ambiente do sistema operacional (os.environ)
3. Arquivo .env local (via python-dotenv ou varredura de diretórios)
4. Valores de fallback pré-definidos do projeto
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

# Tenta carregar dotenv para garantir disponibilidade em scripts CLI
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


def _get_from_streamlit_secrets(key: str) -> str | None:
    """Tenta obter uma chave a partir de st.secrets de forma defensiva."""
    try:
        import streamlit as st

        # Verifica se st.secrets está acessível sem levantar exceção
        if hasattr(st, "secrets") and st.secrets is not None:
            # Busca direta no nível superior
            if key in st.secrets:
                val = st.secrets[key]
                if val is not None:
                    return str(val).strip()

            # Busca insensível a maiúsculas/minúsculas
            key_lower = key.lower()
            for s_key in st.secrets:
                if str(s_key).lower() == key_lower:
                    val = st.secrets[s_key]
                    if val is not None:
                        return str(val).strip()

            # Busca em possíveis subseções (ex: st.secrets.xano[key])
            for s_key in st.secrets:
                section = st.secrets[s_key]
                if isinstance(section, dict):
                    if key in section and section[key] is not None:
                        return str(section[key]).strip()
                    for sub_k in section:
                        if str(sub_k).lower() == key_lower and section[sub_k] is not None:
                            return str(section[sub_k]).strip()
    except Exception:
        # st.secrets pode lançar FileNotFoundError ou StreamlitAPIException se executado fora do Streamlit
        pass
    return None


def _get_from_env_file(key: str) -> str | None:
    """Varre arquivos .env comuns no projeto caso python-dotenv não tenha sido carregado."""
    candidate_paths = [
        Path(".env"),
        Path("edutrack-ai/.env"),
        Path(__file__).resolve().parent.parent / ".env",
        Path(__file__).resolve().parent.parent.parent / ".env",
    ]
    for env_file in candidate_paths:
        if env_file.is_file():
            try:
                with open(env_file, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith(f"{key}="):
                            parsed = line.split("=", 1)[1].strip().strip('"').strip("'")
                            if parsed:
                                return parsed
            except Exception:
                continue
    return None


def get_setting(key: str, default: str = "") -> str:
    """
    Retorna o valor da configuração com base na hierarquia:
    st.secrets -> os.environ -> .env -> default.
    """
    # 1. Streamlit Secrets
    secret_val = _get_from_streamlit_secrets(key)
    if secret_val:
        return secret_val

    # 2. os.environ
    env_val = os.environ.get(key)
    if env_val:
        return env_val.strip()

    # 3. Varredura de arquivos .env
    file_val = _get_from_env_file(key)
    if file_val:
        return file_val.strip()

    # 4. Fallback padrão
    return default


# ---------------------------------------------------------------------------
# Funções de Conveniência para o EduTrack AI
# ---------------------------------------------------------------------------


def get_xano_auth_url() -> str:
    """Retorna a URL base dos endpoints de autenticação Xano."""
    return get_setting(
        "XANO_AUTH_BASE_URL",
        default="https://x8ki-letl-twmt.n7.xano.io/api:6Tn0YgRn",
    ).rstrip("/")


def get_edutrack_base_url() -> str:
    """Retorna a URL base do grupo edutrack.ai."""
    return get_setting(
        "EDUTRACK_BASE_URL",
        default="https://x8ki-letl-twmt.n7.xano.io/api:gTfD518O",
    ).rstrip("/")


def get_tasks_path() -> str:
    """Retorna o segmento de rota para o endpoint de tarefas acadêmicas."""
    return get_setting("EDUTRACK_TASKS_PATH", default="task").strip("/")


def get_auth_token() -> str:
    """Retorna o token JWT pré-configurado, se houver."""
    return get_setting("EDUTRACK_TOKEN", default="").strip()

