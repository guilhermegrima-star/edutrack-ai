"""
app.py
------
Página Principal e Ponto de Entrada do EduTrack AI.
- Modo Deslogado: Landing Page & Central Exclusiva de Login (inspirada em /assets/login.png)
- Modo Autenticado: Dashboard Smart Education (inspirado em /assets/home principal.png)
  - Menu simplificado: Dashboard e My Courses (com gestão completa de obrigações acadêmicas)
"""

from __future__ import annotations
import os
import io
import datetime
import hashlib
import numpy as np
import pandas as pd
import streamlit as st
import altair as alt

# -----------------------------------------------------------------------------
# Configuração da Aplicação Streamlit
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="EduTrack AI - Smart Education",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# Módulos de Tema, Autenticação e Tarefas Acadêmicas
# -----------------------------------------------------------------------------
from utils.theme import (
    apply_login_landing_theme,
    apply_dashboard_theme,
    render_landing_navbar,
    render_sidebar_header,
    render_sidebar_pro_card,
    render_welcome_banner,
    render_kpi_cards,
)
from utils.auth import (
    is_authenticated,
    get_current_user,
    xano_login,
    xano_signup,
    xano_get_me,
    validar_requisitos_senha,
    perform_logout,
)
from utils.tasks_service import (
    get_subjects,
    get_tasks_by_subject,
    create_task,
    update_task_status,
    delete_task,
    calculate_subject_progress,
)

# -----------------------------------------------------------------------------
# Dados de Exemplo para Gestão Acadêmica da Turma
# -----------------------------------------------------------------------------
@st.cache_data
def carregar_dados_alunos():
    dados = {
        "ID": [101, 102, 103, 104, 105, 106, 107, 108],
        "Nome": [
            "Ana Silva", "Bruno Santos", "Carla Costa", "Diogo Rocha",
            "Elena Martins", "Fábio Lima", "Gonçalo Alves", "Helena Ribeiro"
        ],
        "Turma": ["A", "B", "A", "C", "B", "A", "C", "B"],
        "Nota Média": [16.5, 9.2, 14.0, 8.5, 18.2, 11.0, 7.8, 15.4],
        "Frequência (%)": [95, 70, 88, 65, 98, 82, 60, 91],
        "Estado": [
            "Aprovado", "Em Risco", "Aprovado", "Em Risco",
            "Aprovado", "Aprovado", "Em Risco", "Aprovado"
        ]
    }
    return pd.DataFrame(dados)


# =============================================================================
# FLUXO 1: USUÁRIO NÃO AUTENTICADO -> LANDING PAGE & LOGIN (/assets/login.png)
# =============================================================================
if not is_authenticated():
    apply_login_landing_theme()
    render_landing_navbar()

    # Seção Hero com a frase principal e subtítulo obrigatórios
    st.markdown(
        """
        <div class="hero-wrapper">
            <div class="hero-pill">
                <span class="hero-pill-dot"></span>
                <span>✦ Inteligência Acadêmica Desenvolvida para Estudantes</span>
            </div>
            <h1 class="hero-title">
                Aprenda mais. Organize melhor. <span class="hero-title-highlight">Vá além.</span>
            </h1>
            <p class="hero-subtitle">
                Reúna seus conteúdos, planeje suas atividades e tenha tudo o que precisa para evoluir nos estudos.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Card Centralizado e Exclusivo de Autenticação (Login / Cadastro)
    col_l1, col_center, col_l3 = st.columns([1, 1.6, 1])

    with col_center:
        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 20px;">
                <div style="font-size: 20px; font-weight: 700; color: #0F172A;">Acesse sua Área do Aluno</div>
                <div style="font-size: 13px; color: #64748B; margin-top: 4px;">
                    Faça login com suas credenciais ou crie sua conta para começar.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tab_login, tab_signup = st.tabs(["🔑 Entrar na Conta", "📝 Criar Conta Gratuita"])

        # ---------------------------------------------------------------------
        # ABA 1: LOGIN EXCLUSIVO
        # ---------------------------------------------------------------------
        with tab_login:
            with st.form("form_login_main"):
                email_input = st.text_input("E-mail institucional ou pessoal", placeholder="seu.email@exemplo.com")
                senha_input = st.text_input("Senha de acesso", type="password", placeholder="••••••••")
                submit_login = st.form_submit_button("Entrar no EduTrack AI", type="primary", use_container_width=True)

            if submit_login:
                if not email_input.strip() or not senha_input:
                    st.warning("Por favor, preencha o e-mail e a senha.")
                else:
                    with st.spinner("Autenticando..."):
                        sucesso, resposta = xano_login(email_input, senha_input)
                        if sucesso and isinstance(resposta, dict):
                            token = resposta.get("authToken")
                            st.session_state["auth_token"] = token
                            
                            ok_me, user_info = xano_get_me(token)
                            if ok_me and isinstance(user_info, dict):
                                st.session_state["user_data"] = user_info
                            
                            st.success("Autenticado com sucesso! Carregando painel...")
                            st.rerun()
                        else:
                            st.error(f"Erro no login: {resposta}")

        # ---------------------------------------------------------------------
        # ABA 2: CADASTRO EXCLUSIVO
        # ---------------------------------------------------------------------
        with tab_signup:
            st.caption("Requisitos: Mínimo 8 caracteres com pelo menos 1 letra e 1 número.")
            with st.form("form_signup_main"):
                nome_signup = st.text_input("Nome Completo", placeholder="Seu nome completo")
                email_signup = st.text_input("E-mail", placeholder="seu.email@exemplo.com")
                senha_signup = st.text_input("Criar Senha", type="password", placeholder="Crie uma senha forte")
                confirma_senha = st.text_input("Confirmar Senha", type="password", placeholder="Repita a senha")
                submit_signup = st.form_submit_button("Começar Gratuitamente", type="primary", use_container_width=True)

            if submit_signup:
                if not nome_signup.strip():
                    st.warning("O nome completo é obrigatório.")
                elif not email_signup.strip() or "@" not in email_signup:
                    st.warning("Informe um e-mail válido.")
                elif senha_signup != confirma_senha:
                    st.error("As senhas não coincidem.")
                else:
                    valido, msg_erro = validar_requisitos_senha(senha_signup)
                    if not valido:
                        st.error(msg_erro)
                    else:
                        with st.spinner("Criando sua conta..."):
                            sucesso, resposta = xano_signup(nome_signup, email_signup, senha_signup)
                            if sucesso and isinstance(resposta, dict):
                                token = resposta.get("authToken")
                                st.session_state["auth_token"] = token
                                
                                ok_me, user_info = xano_get_me(token)
                                if ok_me and isinstance(user_info, dict):
                                    st.session_state["user_data"] = user_info
                                
                                st.success("Conta criada com sucesso! Acessando painel...")
                                st.rerun()
                            else:
                                st.error(f"Erro no cadastro: {resposta}")

    # Mockup da Janela do App (Notion preview card)
    st.markdown(
        """
        <div class="mockup-window">
            <div class="mockup-header">
                <span class="mockup-dot dot-red"></span>
                <span class="mockup-dot dot-yellow"></span>
                <span class="mockup-dot dot-green"></span>
                <span style="font-size: 12px; font-weight: 600; color: #64748B; margin-left: 8px;">
                    EduTrack AI — Smart Education Dashboard Preview
                </span>
            </div>
            <div class="mockup-body">
                <div style="background: linear-gradient(135deg, #F5EDFF 0%, #EDE5FC 100%); border-radius: 14px; padding: 20px; margin-bottom: 16px; border: 1px solid #E4D7F7;">
                    <div style="font-weight: 800; color: #38337A; font-size: 18px;">Welcome back, Poojitha! 🎓</div>
                    <div style="font-size: 13px; color: #5A539B; margin-top: 4px;">
                        This week you have been studying for 4 consecutive days! Keep it up and improve!
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px;">
                    <div style="background: #FFFFFF; padding: 14px; border-radius: 12px; border: 1px solid #ECEFF7;">
                        <div style="font-size: 11px; color: #64748B; font-weight: 600;">Certificates Earned</div>
                        <div style="font-size: 24px; font-weight: 800; color: #38337A;">18</div>
                    </div>
                    <div style="background: #FFFFFF; padding: 14px; border-radius: 12px; border: 1px solid #ECEFF7;">
                        <div style="font-size: 11px; color: #64748B; font-weight: 600;">On Going Courses</div>
                        <div style="font-size: 24px; font-weight: 800; color: #2563EB;">5</div>
                    </div>
                    <div style="background: #FFFFFF; padding: 14px; border-radius: 12px; border: 1px solid #ECEFF7;">
                        <div style="font-size: 11px; color: #64748B; font-weight: 600;">Completed Courses</div>
                        <div style="font-size: 24px; font-weight: 800; color: #16A34A;">21</div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 3 Pilares no rodapé da Landing Page
    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        st.markdown(
            """
            <div style="background: #FAFAFA; border: 1px solid #E5E7EB; border-radius: 16px; padding: 22px; height: 100%;">
                <div style="font-size: 24px; margin-bottom: 8px;">📚</div>
                <div style="font-size: 16px; font-weight: 700; color: #0F172A; margin-bottom: 6px;">Gestão Centralizada</div>
                <div style="font-size: 13px; color: #475569; line-height: 1.5;">
                    Todas as suas disciplinas, ementas e entregas em um ambiente integrado, visual e sem distrações.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_f2:
        st.markdown(
            """
            <div style="background: #FAFAFA; border: 1px solid #E5E7EB; border-radius: 16px; padding: 22px; height: 100%;">
                <div style="font-size: 24px; margin-bottom: 8px;">🤖</div>
                <div style="font-size: 16px; font-weight: 700; color: #0F172A; margin-bottom: 6px;">Tutor Inteligente com IA</div>
                <div style="font-size: 13px; color: #475569; line-height: 1.5;">
                    Esclareça dúvidas acadêmicas, resuma aulas complexas e receba planos de estudo personalizados.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_f3:
        st.markdown(
            """
            <div style="background: #FAFAFA; border: 1px solid #E5E7EB; border-radius: 16px; padding: 22px; height: 100%;">
                <div style="font-size: 24px; margin-bottom: 8px;">📊</div>
                <div style="font-size: 16px; font-weight: 700; color: #0F172A; margin-bottom: 6px;">Métricas e Relatórios</div>
                <div style="font-size: 13px; color: #475569; line-height: 1.5;">
                    Acompanhe suas horas semanais de dedicação e emita boletins oficiais em PDF autenticados.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height: 40px;'></div>", unsafe_allow_html=True)
    st.markdown(
        """
        <div style="text-align: center; font-size: 12px; color: #94A3B8; padding-bottom: 30px;">
            EduTrack AI © 2026 • Inspirado no design Notion & Smart Education Dashboard
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.stop()


# =============================================================================
# FLUXO 2: USUÁRIO AUTENTICADO -> DASHBOARD SMART EDUCATION (/assets/home principal.png)
# =============================================================================
apply_dashboard_theme()

# Dados do usuário logado
current_user = get_current_user() or {}
nome_usuario = current_user.get("name") or "Poojitha"
auth_token = st.session_state.get("auth_token")

# Carrega disciplinas e tarefas ativas
todas_disciplinas = get_subjects(token=auth_token)
todas_tarefas = get_tasks_by_subject(token=auth_token)
tarefas_pendentes_total = sum(1 for t in todas_tarefas if str(t.get("status", "")).strip().lower() not in ("concluído", "concluido", "done"))

# -----------------------------------------------------------------------------
# SIDEBAR EM TOM ÍNDIGO/ROXO (#38337A) COM LOGO SMART EDUCATION
# -----------------------------------------------------------------------------
render_sidebar_header()

# Menu de navegação simplificado conforme solicitado pelo usuário:
# Mantém apenas "Dashboard" e "My Courses"
opcao_menu = st.sidebar.radio(
    "Navegação:",
    [
        "Dashboard",
        "My Courses",
    ],
    index=0,
    label_visibility="collapsed",
)

st.sidebar.markdown("---")

# Link para a página de perfil no Streamlit
if hasattr(st, "page_link"):
    st.sidebar.page_link("pages/3_🔒_Perfil.py", label="🔒 Meu Perfil & Relatórios", icon="👤")

# Card Pro na Sidebar
render_sidebar_pro_card()

st.sidebar.markdown("---")

# Perfil resumido no rodapé da Sidebar com botão de logout
st.sidebar.markdown(
    f"""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
        <div style="
            width: 38px;
            height: 38px;
            background: #FFFFFF;
            color: #38337A;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 16px;
        ">
            {nome_usuario[0].upper() if nome_usuario else "U"}
        </div>
        <div style="overflow: hidden;">
            <div style="font-weight: 700; color: #FFFFFF; font-size: 14px; white-space: nowrap; text-overflow: ellipsis; overflow: hidden;">
                {nome_usuario}
            </div>
            <div style="font-size: 11px; color: #C7D2FE;">Aluno Ativo</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if st.sidebar.button("🚪 Sair da Conta (Logout)", use_container_width=True):
    perform_logout()


# -----------------------------------------------------------------------------
# BARRA SUPERIOR DE PESQUISA (Estilo /assets/home principal.png)
# -----------------------------------------------------------------------------
col_busca, col_status = st.columns([4, 1])
with col_busca:
    termo_busca = st.text_input(
        "Pesquisar",
        placeholder="🔍 Try to find...",
        label_visibility="collapsed",
    )
with col_status:
    st.markdown(
        """
        <div style="display: flex; align-items: center; justify-content: flex-end; gap: 10px; height: 100%;">
            <span class="badge-pill-success">● Conectado</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


# -----------------------------------------------------------------------------
# ABA 1: DASHBOARD PRINCIPAL
# -----------------------------------------------------------------------------
if opcao_menu == "Dashboard":
    col_main_dash, col_upcoming = st.columns([2.7, 1.1])

    with col_main_dash:
        # 1. Banner de Boas-Vindas Lilás com Ilustração
        render_welcome_banner(user_name=nome_usuario, days_streak=4)

        # 2. Cartões Rápidos de KPI (3 colunas exatamente como em home principal.png)
        render_kpi_cards(certificados=18, em_andamento=len(todas_disciplinas), concluidos=21)

        st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

        # 3. Card "Hours Activity" (Gráfico de Barras Duplas Amarelo/Roxo + Métricas Laterais)
        st.markdown(
            """
            <div class="activity-card">
                <div class="activity-header">
                    <div>
                        <h3 class="activity-title">Hours Activity</h3>
                        <div style="margin-top: 6px; display: flex; align-items: center; gap: 14px;">
                            <span class="badge-pill-success">✓ +2 More than last week</span>
                            <span style="font-size: 12px; color: #64748B; display: inline-flex; align-items: center; gap: 4px;">
                                <span style="color: #F6C768; font-size: 14px;">●</span> UI UX Fundamentals..
                            </span>
                            <span style="font-size: 12px; color: #64748B; display: inline-flex; align-items: center; gap: 4px;">
                                <span style="color: #6C5CE7; font-size: 14px;">●</span> UI Colours theories..
                            </span>
                        </div>
                    </div>
                    <div style="font-size: 13px; font-weight: 700; color: #4E44B4; background: #EEF2FF; padding: 6px 14px; border-radius: 10px;">
                        Weekly ▾
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_chart, col_side_metrics = st.columns([2.6, 1.4])

        with col_chart:
            # Dados de atividade semanal dos dias 08 a 14 de home principal.png
            dados_atividade = [
                {"day": "08", "category": "UI UX Fundamentals", "hours": 1.2, "color": "#F6C768"},
                {"day": "08", "category": "UI Colours theories", "hours": 3.4, "color": "#6C5CE7"},
                {"day": "09", "category": "UI UX Fundamentals", "hours": 2.8, "color": "#F6C768"},
                {"day": "09", "category": "UI Colours theories", "hours": 2.5, "color": "#6C5CE7"},
                {"day": "10", "category": "UI UX Fundamentals", "hours": 3.5, "color": "#F6C768"},
                {"day": "10", "category": "UI Colours theories", "hours": 1.9, "color": "#6C5CE7"},
                {"day": "11", "category": "UI UX Fundamentals", "hours": 2.1, "color": "#F6C768"},
                {"day": "11", "category": "UI Colours theories", "hours": 4.5, "color": "#6C5CE7"},
                {"day": "12", "category": "UI UX Fundamentals", "hours": 3.8, "color": "#F6C768"},
                {"day": "12", "category": "UI Colours theories", "hours": 5.1, "color": "#6C5CE7"},
                {"day": "13", "category": "UI UX Fundamentals", "hours": 4.2, "color": "#F6C768"},
                {"day": "13", "category": "UI Colours theories", "hours": 0.8, "color": "#6C5CE7"},
                {"day": "14", "category": "UI UX Fundamentals", "hours": 4.9, "color": "#F6C768"},
                {"day": "14", "category": "UI Colours theories", "hours": 3.3, "color": "#6C5CE7"},
            ]
            df_chart = pd.DataFrame(dados_atividade)

            chart = (
                alt.Chart(df_chart)
                .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
                .encode(
                    x=alt.X("category:N", title=None, axis=None),
                    y=alt.Y("hours:Q", title=None, scale=alt.Scale(domain=[0, 6])),
                    color=alt.Color(
                        "category:N",
                        scale=alt.Scale(
                            domain=["UI UX Fundamentals", "UI Colours theories"],
                            range=["#F6C768", "#6C5CE7"]
                        ),
                        legend=None
                    ),
                    column=alt.Column("day:N", title=None, header=alt.Header(labelOrient="bottom", labelFontWeight="bold"))
                )
                .properties(height=250)
                .configure_view(strokeWidth=0)
                .configure_axis(grid=True, gridColor="#F1F5F9")
            )
            st.altair_chart(chart, use_container_width=True)

        with col_side_metrics:
            st.markdown(
                f"""
                <div class="metric-summary-box">
                    <div class="metric-summary-label">Hours Spent</div>
                    <div class="metric-summary-row">
                        <span class="metric-summary-value">12</span>
                        <span class="badge-pill-success">▲ 10%</span>
                    </div>
                </div>

                <div class="metric-summary-box">
                    <div class="metric-summary-label">Average Score</div>
                    <div class="metric-summary-row">
                        <span class="metric-summary-value">86</span>
                        <span class="badge-pill-danger">▼ 10%</span>
                    </div>
                </div>

                <div class="metric-summary-box">
                    <div class="metric-summary-label">Assignments</div>
                    <div class="metric-summary-row">
                        <span class="metric-summary-value">{tarefas_pendentes_total}</span>
                        <span class="badge-pill-warning">Pendentes</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

        # 4. Seção "Browse Courses" (Inspirada no rodapé de home principal.png)
        st.markdown("### 📚 Browse Courses")
        col_c1, col_c2 = st.columns(2)

        if termo_busca:
            cursos_filtrados = [
                c for c in todas_disciplinas
                if termo_busca.lower() in str(c.get("name", "")).lower() or termo_busca.lower() in str(c.get("teacher", "")).lower()
            ]
        else:
            cursos_filtrados = todas_disciplinas

        for i, curso in enumerate(cursos_filtrados):
            col_target = col_c1 if i % 2 == 0 else col_c2
            # Calcula o progresso dinâmico das tarefas vinculadas à matéria
            t_curso = [t for t in todas_tarefas if int(t.get("subject_id", 0)) == int(curso.get("id", 0))]
            stats = calculate_subject_progress(t_curso)
            cor_curso = curso.get("color", "#4E44B4")

            with col_target:
                st.markdown(
                    f"""
                    <div class="course-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                            <span style="font-size: 11px; font-weight: 700; color: {cor_curso}; background: #F8F9FD; padding: 2px 8px; border-radius: 6px;">
                                {curso.get('hours', 60)}h • {stats['completed']}/{stats['total']} concluídas
                            </span>
                            <span style="font-size: 12px; font-weight: 700; color: #1E293B;">{stats['percent']}%</span>
                        </div>
                        <h4>{curso.get('name')}</h4>
                        <p>{curso.get('teacher', 'Docente EduTrack')}</p>
                        <div style="background: #E2E8F0; border-radius: 6px; height: 6px; width: 100%; overflow: hidden;">
                            <div style="background: {cor_curso}; height: 100%; width: {stats['percent']}%;"></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # Painel Lateral de Atividades Futuras (Coluna da Direita)
    with col_upcoming:
        st.markdown(
            """
            <div style="background: #FFFFFF; border-radius: 18px; padding: 20px; border: 1px solid #ECEFF7; box-shadow: 0 4px 16px rgba(0,0,0,0.02); margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                    <div style="font-weight: 800; font-size: 16px; color: #1E293B;">Upcoming Schedule</div>
                    <span style="font-size: 12px; color: #4E44B4; font-weight: 700;">Próximos Prazos</span>
                </div>

                <div style="border-left: 3px solid #6C5CE7; padding-left: 12px; margin-bottom: 16px;">
                    <div style="font-size: 11px; font-weight: 700; color: #6C5CE7;">HOJE • 14:00</div>
                    <div style="font-size: 13px; font-weight: 700; color: #1E293B;">UI UX Design Critique</div>
                    <div style="font-size: 12px; color: #64748B;">Apresentação do protótipo com a turma</div>
                </div>

                <div style="border-left: 3px solid #F6C768; padding-left: 12px; margin-bottom: 16px;">
                    <div style="font-size: 11px; font-weight: 700; color: #D97706;">AMANHÃ • 23:59</div>
                    <div style="font-size: 13px; font-weight: 700; color: #1E293B;">Entrega: Color Theories</div>
                    <div style="font-size: 12px; color: #64748B;">Envio da paleta com contraste WCAG</div>
                </div>

                <div style="border-left: 3px solid #10B981; padding-left: 12px;">
                    <div style="font-size: 11px; font-weight: 700; color: #059669;">SEXTA • 10:00</div>
                    <div style="font-size: 13px; font-weight: 700; color: #1E293B;">Mentoria com Tutor IA</div>
                    <div style="font-size: 12px; color: #64748B;">Revisão das métricas acadêmicas</div>
                </div>
            </div>

            <div style="background: linear-gradient(135deg, #EEF2FF 0%, #E0E7FF 100%); border-radius: 18px; padding: 20px; border: 1px solid #C7D2FE;">
                <div style="font-weight: 800; color: #38337A; font-size: 15px; margin-bottom: 6px;">💡 Dica de Estudo com IA</div>
                <div style="font-size: 12px; color: #4338CA; line-height: 1.5;">
                    Estudar 30 minutos em blocos focados (Pomodoro) melhora a retenção e reduz a sobrecarga antes das avaliações.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # 5. Gestão Acadêmica da Turma e Emissão de Relatório Oficial Individual (PDF)
    st.markdown("### 👥 Gestão Acadêmica da Turma & Boletim Individual (PDF)")
    df_alunos = carregar_dados_alunos()

    col_filtro_nome, col_filtro_est = st.columns([2, 1])
    with col_filtro_nome:
        busca_aluno = st.text_input("Filtrar por nome do(a) aluno(a):", placeholder="Ex: Ana, Bruno...")
    with col_filtro_est:
        filtro_estado = st.selectbox("Situação:", ["Todos", "Aprovado", "Em Risco"])

    df_exibicao = df_alunos.copy()
    if busca_aluno:
        df_exibicao = df_exibicao[df_exibicao["Nome"].str.contains(busca_aluno, case=False)]
    if filtro_estado != "Todos":
        df_exibicao = df_exibicao[df_exibicao["Estado"] == filtro_estado]

    st.dataframe(df_exibicao, use_container_width=True)

    # Painel de Emissão de Relatório PDF com ReportLab
    st.markdown("#### 📄 Exportar Relatório Oficial do Aluno em PDF")
    col_sel_aluno, col_btn_gerar = st.columns([2, 1])

    with col_sel_aluno:
        aluno_selecionado = st.selectbox(
            "Selecione o aluno para emissão:",
            options=df_exibicao["Nome"].tolist() if not df_exibicao.empty else df_alunos["Nome"].tolist(),
        )

    registro_selecionado = df_alunos[df_alunos["Nome"] == aluno_selecionado].iloc[0].to_dict()
    media_geral = float(df_alunos["Nota Média"].mean())

    with col_btn_gerar:
        st.write("")
        st.write("")
        btn_gerar_pdf = st.button("📊 Gerar Relatório PDF", type="primary", use_container_width=True)

    def gerar_pdf_academico(aluno: dict, media_turma: float) -> io.BytesIO:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            leftMargin=36,
            rightMargin=36,
            topMargin=36,
            bottomMargin=36
        )
        styles = getSampleStyleSheet()

        style_title = ParagraphStyle(
            "PDFTitle",
            parent=styles["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#38337A"),
            spaceAfter=2,
        )
        style_sub = ParagraphStyle(
            "PDFSubtitle",
            parent=styles["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=13,
            textColor=colors.HexColor("#64748B"),
            spaceAfter=10,
        )
        style_section = ParagraphStyle(
            "PDFSection",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=11,
            leading=15,
            textColor=colors.HexColor("#0F172A"),
            spaceBefore=10,
            spaceAfter=6,
        )
        style_cell = ParagraphStyle(
            "PDFCell",
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#334155"),
        )
        style_cell_bold = ParagraphStyle(
            "PDFCellBold",
            fontName="Helvetica-Bold",
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#0F172A"),
        )
        style_cell_center = ParagraphStyle(
            "PDFCellCenter",
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            alignment=1,
            textColor=colors.HexColor("#334155"),
        )
        style_card_val = ParagraphStyle(
            "PDFCardVal",
            fontName="Helvetica-Bold",
            fontSize=14,
            leading=18,
            alignment=1,
            textColor=colors.HexColor("#38337A"),
        )
        style_card_label = ParagraphStyle(
            "PDFCardLabel",
            fontName="Helvetica-Bold",
            fontSize=8,
            leading=10,
            alignment=1,
            textColor=colors.HexColor("#64748B"),
        )

        story = []
        story.append(Paragraph("🎓 EduTrack AI — Smart Education", style_title))
        story.append(Paragraph("Relatório Oficial de Desempenho e Aproveitamento Acadêmico", style_sub))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#38337A"), spaceAfter=12))

        emissao = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M")
        info_data = [
            [
                Paragraph(f"<b>Aluno(a):</b> {aluno['Nome']}", style_cell),
                Paragraph(f"<b>ID do Aluno:</b> {aluno['ID']}", style_cell),
            ],
            [
                Paragraph(f"<b>Turma:</b> {aluno['Turma']}", style_cell),
                Paragraph(f"<b>Data de Emissão:</b> {emissao}", style_cell),
            ],
        ]
        t_info = Table(info_data, colWidths=[320, 203])
        t_info.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#E2E8F0")),
            ("PADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(t_info)
        story.append(Spacer(1, 10))

        status_cor = "#10B981" if aluno["Estado"] == "Aprovado" else "#EF4444"
        style_card_status = ParagraphStyle("CardStatus", parent=style_card_val, textColor=colors.HexColor(status_cor))

        kpis = [
            [
                Paragraph("NOTA MÉDIA", style_card_label),
                Paragraph("FREQUÊNCIA", style_card_label),
                Paragraph("ESTADO ATUAL", style_card_label),
                Paragraph("MÉDIA DA TURMA", style_card_label),
            ],
            [
                Paragraph(f"{aluno['Nota Média']:.1f} / 20", style_card_val),
                Paragraph(f"{aluno['Frequência (%)']}%", style_card_val),
                Paragraph(str(aluno["Estado"]), style_card_status),
                Paragraph(f"{media_turma:.1f} / 20", style_card_val),
            ],
        ]
        t_kpis = Table(kpis, colWidths=[130, 130, 133, 130])
        t_kpis.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("PADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(t_kpis)
        story.append(Spacer(1, 12))

        story.append(Paragraph("📊 Avaliação por Unidade Curricular", style_section))
        disciplinas_data = [
            [
                Paragraph("Unidade Curricular", style_cell_bold),
                Paragraph("Docente", style_cell_bold),
                Paragraph("C.H.", style_cell_bold),
                Paragraph("Nota", style_cell_bold),
                Paragraph("Situação", style_cell_bold),
            ]
        ]
        offset = aluno["Nota Média"] - 14.0
        disciplinas = [
            ("UI UX Fundamentals", "Prof. Dr. Ricardo Neves", "80h", max(0.0, min(20.0, round(14.5 + offset, 1)))),
            ("UI Colours theories", "Prof. Ana Ribeiro", "60h", max(0.0, min(20.0, round(15.2 + offset, 1)))),
            ("Algoritmos e Programação", "Prof. Carlos Duarte", "80h", max(0.0, min(20.0, round(13.8 + offset, 1)))),
            ("Inteligência Artificial & Lab", "Prof. Guilherme Grima", "80h", max(0.0, min(20.0, round(16.0 + offset, 1)))),
        ]
        for nome_d, prof, ch, nota in disciplinas:
            sit = "Aprovado" if nota >= 9.5 else "Em Recuperação"
            disciplinas_data.append([
                Paragraph(nome_d, style_cell),
                Paragraph(prof, style_cell),
                Paragraph(ch, style_cell_center),
                Paragraph(f"{nota:.1f} / 20", style_cell_center),
                Paragraph(sit, style_cell_center),
            ])

        t_disc = Table(disciplinas_data, colWidths=[160, 153, 70, 70, 70])
        t_disc.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#38337A")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ("PADDING", (0, 0), (-1, -1), 5),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(t_disc)
        story.append(Spacer(1, 12))

        story.append(Paragraph("📋 Parecer Pedagógico e Observações", style_section))
        if aluno["Estado"] == "Aprovado" and aluno["Nota Média"] >= 14.0:
            parecer = "Aluno com excelente aproveitamento acadêmico e assiduidade satisfatória. Demonstra consistência nas avaliações e domínio dos tópicos curriculares."
        elif aluno["Estado"] == "Aprovado":
            parecer = "Aluno com aproveitamento regular e frequência adequada. Recomenda-se reforço nos tópicos com maior nível de exigência para manter a progressão."
        else:
            parecer = "Aluno em situação de risco acadêmico devido a notas abaixo da média ou frequência inferior a 75%. Recomenda-se acompanhamento de tutoria e elaboração de plano de recuperação."

        t_parecer = Table([[Paragraph(parecer, style_cell)]], colWidths=[523])
        t_parecer.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
            ("PADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(t_parecer)
        story.append(Spacer(1, 14))

        hash_txt = f"{aluno['ID']}-{aluno['Nome']}-{aluno['Nota Média']}-{aluno['Frequência (%)']}-{emissao}"
        chk = hashlib.sha256(hash_txt.encode("utf-8")).hexdigest()
        t_chk = Table([[Paragraph(
            f"<b>Código de Autenticidade (SHA-256):</b> <font face='Courier' size='7'>{chk}</font><br/>"
            "<font size='7' color='#64748B'>Documento emitido automaticamente pelo sistema EduTrack AI.</font>",
            style_cell
        )]], colWidths=[523])
        t_chk.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F1F5F9")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#94A3B8")),
            ("PADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(t_chk)

        doc.build(story)
        buffer.seek(0)
        return buffer

    if btn_gerar_pdf:
        with st.spinner(f"Compilando relatório em PDF para {registro_selecionado['Nome']}..."):
            try:
                pdf_buffer = gerar_pdf_academico(registro_selecionado, media_geral)
                st.session_state["pdf_aluno_bytes"] = pdf_buffer.getvalue()
                st.session_state["pdf_aluno_nome"] = registro_selecionado["Nome"]
                st.success(f"Relatório gerado com sucesso para **{registro_selecionado['Nome']}**!")
            except Exception as e:
                st.error(f"Erro ao gerar o relatório em PDF: {e}")

    if "pdf_aluno_bytes" in st.session_state and st.session_state["pdf_aluno_bytes"]:
        nome_arquivo = st.session_state.get("pdf_aluno_nome", "aluno").lower().replace(" ", "_")
        col_dw1, col_dw2 = st.columns([1, 2])
        with col_dw1:
            st.download_button(
                label="⬇️ Baixar Relatório (PDF)",
                data=st.session_state["pdf_aluno_bytes"],
                file_name=f"relatorio_desempenho_{nome_arquivo}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True,
            )
        with col_dw2:
            st.info(f"Relatório pronto: **{st.session_state.get('pdf_aluno_nome')}**.")


# -----------------------------------------------------------------------------
# ABA 2: MY COURSES & GESTÃO DE OBRIGAÇÕES ACADÊMICAS (ACADEMIC TASKS)
# -----------------------------------------------------------------------------
elif opcao_menu == "My Courses":
    st.markdown("## 📚 My Courses & Gestão de Obrigações Acadêmicas")
    st.caption("Registre e acompanhe lições, provas e trabalhos vinculados a cada uma de suas disciplinas.")

    # 1. Visão Geral das Disciplinas Matriculadas
    st.markdown("### Disciplinas do Semestre")
    col_d1, col_d2, col_d3 = st.columns(3)

    for idx, disc in enumerate(todas_disciplinas):
        col_atual = [col_d1, col_d2, col_d3][idx % 3]
        tasks_disc = [t for t in todas_tarefas if int(t.get("subject_id", 0)) == int(disc.get("id", 0))]
        prog = calculate_subject_progress(tasks_disc)
        cor = disc.get("color", "#4E44B4")

        with col_atual:
            st.markdown(
                f"""
                <div class="course-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-size: 11px; font-weight: 700; color: {cor}; background: #F8F9FD; padding: 2px 8px; border-radius: 6px;">
                            ID #{disc.get('id')} • {disc.get('hours', 60)}h
                        </span>
                        <span style="font-size: 12px; font-weight: 700; color: #1E293B;">{prog['percent']}%</span>
                    </div>
                    <h4>{disc.get('name')}</h4>
                    <p>{disc.get('teacher', 'Docente')} • <b>{prog['completed']}/{prog['total']} obrigações</b></p>
                    <div style="background: #E2E8F0; border-radius: 6px; height: 6px; width: 100%; overflow: hidden;">
                        <div style="background: {cor}; height: 100%; width: {prog['percent']}%;"></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("---")

    # 2. Formulário para Registrar Nova Obrigação Acadêmica
    with st.expander("➕ Cadastrar Nova Obrigação Acadêmica (Lição, Prova ou Trabalho)", expanded=False):
        st.markdown(
            """
            <div style="font-size: 13px; color: #64748B; margin-bottom: 12px;">
                Preencha os campos abaixo conforme o esquema definido na tabela <code>academic_tasks</code>:
                <b>title</b>, <b>description</b>, <b>due_date</b>, <b>status</b> e <b>subject_id</b>.
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("form_cadastrar_obrigacao", clear_on_submit=True):
            col_f_tit, col_f_disc = st.columns([2, 1])

            with col_f_tit:
                task_title = st.text_input("Título da Obrigação Acadêmica *", placeholder="Ex: Prova Bimestral de UI/UX, Lista 2...")
            with col_f_disc:
                nomes_disciplinas = {d["id"]: f"{d['name']} (ID: {d['id']})" for d in todas_disciplinas}
                selected_sub_id = st.selectbox(
                    "Disciplina Vinculada (subject_id) *",
                    options=list(nomes_disciplinas.keys()),
                    format_func=lambda x: nomes_disciplinas[x],
                )

            task_desc = st.text_area(
                "Descrição / Critérios de Entrega (description)",
                placeholder="Detalhes, capítulos para leitura, formato do arquivo ou orientações do docente...",
            )

            col_f_date, col_f_status = st.columns(2)
            with col_f_date:
                task_date = st.date_input("Data de Entrega / Realização (due_date) *", value=datetime.date.today() + datetime.timedelta(days=7))
            with col_f_status:
                task_status = st.selectbox("Status Inicial (status) *", ["Pendente", "Em Andamento", "Concluído"], index=0)

            btn_salvar_task = st.form_submit_button("💾 Salvar Obrigação Acadêmica", type="primary", use_container_width=True)

        if btn_salvar_task:
            if not task_title.strip():
                st.error("O campo 'Título' é obrigatório.")
            else:
                with st.spinner("Registrando obrigação acadêmica..."):
                    criada = create_task(
                        title=task_title,
                        description=task_desc,
                        due_date=str(task_date),
                        status=task_status,
                        subject_id=selected_sub_id,
                        token=auth_token,
                    )
                    st.success(f"Obrigação acadêmica **'{criada['title']}'** cadastrada com sucesso!")
                    st.rerun()

    # 3. Gerenciamento e Listagem de Obrigações Acadêmicas
    st.markdown("### 📋 Painel de Obrigações Acadêmicas Cadastradas")

    col_flt_sub, col_flt_stat = st.columns([2, 1])
    with col_flt_sub:
        filtro_sub_id = st.selectbox(
            "Filtrar por Disciplina:",
            options=["Todas"] + [d["id"] for d in todas_disciplinas],
            format_func=lambda x: "Todas as Disciplinas" if x == "Todas" else f"#{x} - {next((d['name'] for d in todas_disciplinas if d['id'] == x), '')}",
        )
    with col_flt_stat:
        filtro_status_task = st.selectbox(
            "Filtrar por Status:",
            options=["Todos", "Pendente", "Em Andamento", "Concluído"],
        )

    # Aplica filtros
    tarefas_filtradas = todas_tarefas
    if filtro_sub_id != "Todas":
        tarefas_filtradas = [t for t in tarefas_filtradas if int(t.get("subject_id", 0)) == int(filtro_sub_id)]
    if filtro_status_task != "Todos":
        tarefas_filtradas = [t for t in tarefas_filtradas if str(t.get("status", "")).strip().lower() == filtro_status_task.lower()]

    if not tarefas_filtradas:
        st.info("Nenhuma obrigação acadêmica encontrada com os filtros selecionados.")
    else:
        for t in tarefas_filtradas:
            t_id = t.get("id")
            t_title = t.get("title", "Sem título")
            t_desc = t.get("description", "")
            t_due = t.get("due_date", "Sem data")
            t_stat = t.get("status", "Pendente")
            t_sub_id = int(t.get("subject_id", 0))

            # Nome da disciplina correspondente
            sub_obj = next((d for d in todas_disciplinas if int(d.get("id", 0)) == t_sub_id), None)
            sub_name = sub_obj.get("name", f"Disciplina #{t_sub_id}") if sub_obj else f"Disciplina #{t_sub_id}"
            sub_color = sub_obj.get("color", "#4E44B4") if sub_obj else "#4E44B4"

            # Badge do status
            if t_stat.lower() in ("concluído", "concluido", "done"):
                badge_html = '<span class="badge-pill-success">✓ Concluído</span>'
            elif t_stat.lower() in ("em andamento", "in_progress"):
                badge_html = '<span class="badge-pill-warning">⏳ Em Andamento</span>'
            else:
                badge_html = '<span style="background: #F1F5F9; color: #475569; padding: 4px 10px; border-radius: 9999px; font-size: 11px; font-weight: 700;">● Pendente</span>'

            col_card_info, col_card_acts = st.columns([3.8, 1.2])

            with col_card_info:
                st.markdown(
                    f"""
                    <div style="background: #FFFFFF; border: 1px solid #ECEFF7; border-radius: 14px; padding: 18px; margin-bottom: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.02);">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <span style="background: #F5EDFF; color: {sub_color}; font-size: 11px; font-weight: 700; padding: 3px 10px; border-radius: 6px;">
                                {sub_name} (ID: {t_sub_id})
                            </span>
                            <div>{badge_html}</div>
                        </div>
                        <div style="font-size: 16px; font-weight: 700; color: #1E293B; margin-bottom: 4px;">{t_title}</div>
                        <div style="font-size: 13px; color: #64748B; margin-bottom: 8px;">{t_desc if t_desc else 'Sem descrição adicional.'}</div>
                        <div style="font-size: 12px; font-weight: 600; color: #4E44B4;">
                            📅 Prazo de Entrega: <b>{t_due}</b>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with col_card_acts:
                st.write("")
                # Alternar status
                if t_stat.lower() in ("concluído", "concluido", "done"):
                    if st.button("↺ Reabrir", key=f"reopen_{t_id}", use_container_width=True):
                        update_task_status(t_id, "Em Andamento", token=auth_token)
                        st.rerun()
                else:
                    if st.button("✓ Concluir", key=f"done_{t_id}", type="primary", use_container_width=True):
                        update_task_status(t_id, "Concluído", token=auth_token)
                        st.rerun()

                # Botão Excluir
                if st.button("🗑️ Excluir", key=f"del_{t_id}", use_container_width=True):
                    delete_task(t_id, token=auth_token)
                    st.rerun()
