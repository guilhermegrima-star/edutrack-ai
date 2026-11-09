"""
pages/3_🔒_Perfil.py
--------------------
Página de Perfil do Usuário no EduTrack AI.
Reformulada de acordo com os padrões visuais de /assets/home principal.png.
Formulários de login e cadastro removidos — autenticação centralizada na página principal (app.py).
"""

from __future__ import annotations
import os
import datetime
from pathlib import Path
import streamlit as st

# -----------------------------------------------------------------------------
# Configuração da Página
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Perfil do Aluno - EduTrack AI",
    page_icon="👤",
    layout="wide"
)

# -----------------------------------------------------------------------------
# Utilitários de Tema e Autenticação
# -----------------------------------------------------------------------------
from utils.theme import (
    apply_dashboard_theme,
    render_sidebar_header,
    render_sidebar_pro_card,
)
from utils.auth import (
    is_authenticated,
    get_current_user,
    xano_get_me,
    perform_logout,
    guard_authenticated_page,
)

# Aplica o tema visual unificado
apply_dashboard_theme()

# Guarda de Acesso: Bloqueia acesso direto deslogado e orienta para app.py
guard_authenticated_page("o Perfil do Usuário")

# Renderização dos componentes da Sidebar
render_sidebar_header()

st.sidebar.markdown("---")
if hasattr(st, "page_link"):
    st.sidebar.page_link("app.py", label="⊞ Ir para o Dashboard", icon="📊")

render_sidebar_pro_card()

st.sidebar.markdown("---")
if st.sidebar.button("🚪 Encerrar Sessão (Logout)", use_container_width=True):
    perform_logout()

# -----------------------------------------------------------------------------
# Carregamento e Atualização dos Dados do Usuário
# -----------------------------------------------------------------------------
auth_token = st.session_state.get("auth_token")
user = get_current_user()

if not user and auth_token:
    with st.spinner("Carregando informações do perfil..."):
        ok, result = xano_get_me(auth_token)
        if ok and isinstance(result, dict):
            st.session_state["user_data"] = result
            user = result


def formatar_data(timestamp_val) -> str:
    """Converte timestamps (ms ou s) para data legível."""
    if not timestamp_val:
        return "N/D"
    try:
        if isinstance(timestamp_val, (int, float)) and timestamp_val > 1e11:
            timestamp_val = timestamp_val / 1000.0
        dt = datetime.datetime.fromtimestamp(float(timestamp_val))
        return dt.strftime("%d/%m/%Y às %H:%M")
    except Exception:
        return str(timestamp_val)


# -----------------------------------------------------------------------------
# Visualização do Perfil (Estilo /assets/home principal.png)
# -----------------------------------------------------------------------------
user_name = user.get("name", "Aluno(a)") if user else "Aluno(a)"
user_email = user.get("email", "aluno@edutrack.ai") if user else "aluno@edutrack.ai"
user_role = (user.get("role") or "member").capitalize() if user else "Estudante"
user_id = user.get("id", "N/D") if user else "N/D"
account_id = user.get("account_id", 0) if user else 0
membro_desde = formatar_data(user.get("created_at")) if user else "N/D"

# Banner Superior de Perfil
st.markdown(
    f"""
    <div class="welcome-banner">
        <div>
            <h2>Perfil Acadêmico de {user_name} 👤</h2>
            <p>
                Gerencie seus dados de acesso, verifique sua matrícula e faça download do seu relatório oficial de desempenho individual.
            </p>
        </div>
        <div class="welcome-avatar-container">
            🧑‍🎓
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Cartões de Informações Cadastrais
st.markdown("### 📋 Informações Cadastrais")

col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
with col_kpi1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon-wrap" style="background: #EEF2FF; color: #4F46E5;">
                👤
            </div>
            <div>
                <div class="kpi-label">Nome Completo</div>
                <div class="kpi-val" style="font-size: 20px; color: #1E293B;">{user_name}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_kpi2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon-wrap" style="background: #F0FDF4; color: #16A34A;">
                ✉️
            </div>
            <div>
                <div class="kpi-label">E-mail Cadastrado</div>
                <div class="kpi-val" style="font-size: 16px; color: #1E293B; word-break: break-all;">{user_email}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_kpi3:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon-wrap" style="background: #FEF3C7; color: #D97706;">
                🏷️
            </div>
            <div>
                <div class="kpi-label">Tipo de Conta</div>
                <div class="kpi-val" style="font-size: 20px; color: #1E293B;">{user_role}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

col_det1, col_det2, col_det3 = st.columns(3)
with col_det1:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon-wrap" style="background: #F8FAFC; color: #64748B;">
                🆔
            </div>
            <div>
                <div class="kpi-label">ID de Registro</div>
                <div class="kpi-val" style="font-size: 20px; color: #475569;">#{user_id}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_det2:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon-wrap" style="background: #F8FAFC; color: #64748B;">
                🏢
            </div>
            <div>
                <div class="kpi-label">Workspace / Turma</div>
                <div class="kpi-val" style="font-size: 20px; color: #475569;">Conta #{account_id}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_det3:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-icon-wrap" style="background: #F8FAFC; color: #64748B;">
                📅
            </div>
            <div>
                <div class="kpi-label">Membro Desde</div>
                <div class="kpi-val" style="font-size: 16px; color: #475569;">{membro_desde}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Seção de Relatório Individual em PDF
# -----------------------------------------------------------------------------
st.markdown("### 📄 Emissão do Relatório Acadêmico Individual")
st.markdown(
    """
    <div class="activity-card">
        <div class="activity-header">
            <div>
                <div class="activity-title">Boletim Consolidado do Aluno (PDF)</div>
                <div style="font-size: 13px; color: #64748B; margin-top: 4px;">
                    Compilação automática com notas por disciplina, assiduidade global e parecer pedagógico.
                </div>
            </div>
            <span class="badge-pill-success">Disponível</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

col_pdf_act1, col_pdf_act2 = st.columns([1, 2])

with col_pdf_act1:
    gerar_relatorio = st.button("📊 Compilar Relatório PDF", type="primary", use_container_width=True)

with col_pdf_act2:
    if "cached_pdf_bytes" in st.session_state and st.session_state["cached_pdf_bytes"]:
        st.download_button(
            label="⬇️ Baixar Arquivo PDF Gerado",
            data=st.session_state["cached_pdf_bytes"],
            file_name=st.session_state.get("cached_pdf_name", "relatorio_desempenho.pdf"),
            mime="application/pdf",
            type="primary",
            use_container_width=True,
        )

if gerar_relatorio:
    with st.spinner("Compilando dados acadêmicos e gerando PDF..."):
        try:
            from scripts.generate_report import generate_student_report
            meta = generate_student_report(token=auth_token, upload=False)
            pdf_path = meta.get("pdf_path")
            if pdf_path and Path(pdf_path).is_file():
                with open(pdf_path, "rb") as f_pdf:
                    st.session_state["cached_pdf_bytes"] = f_pdf.read()
                    st.session_state["cached_pdf_name"] = Path(pdf_path).name
                st.session_state["cached_pdf_prog"] = meta.get("global_progress_percent", 0.0)
                st.success(f"Relatório gerado com sucesso! Progresso geral apurado: **{meta.get('global_progress_percent')}%**")
                st.rerun()
        except Exception as err:
            st.error(f"Erro ao gerar relatório em PDF: {err}")

st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Ações Rápidas de Conta
# -----------------------------------------------------------------------------
col_action1, col_action2, _ = st.columns([1, 1, 2])

with col_action1:
    if st.button("🔄 Atualizar Informações", use_container_width=True):
        if auth_token:
            with st.spinner("Atualizando perfil..."):
                ok, result = xano_get_me(auth_token)
                if ok and isinstance(result, dict):
                    st.session_state["user_data"] = result
                    st.success("Dados sincronizados com o servidor!")
                    st.rerun()
                else:
                    st.error(f"Erro ao atualizar: {result}")

with col_action2:
    if st.button("🚪 Encerrar Sessão", type="secondary", use_container_width=True):
        perform_logout()
