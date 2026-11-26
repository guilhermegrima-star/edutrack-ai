"""
utils/theme.py
--------------
Módulo de identidade visual e componentes de UI do EduTrack AI.
Inspirado nas diretrizes de design:
- assets/login.png (Landing Page minimalista estilo Notion)
- assets/home principal.png (painel de educação inteligente em tons de índigo/roxo)
"""

from __future__ import annotations
import streamlit as st
import html

# -----------------------------------------------------------------------------
# CSS Global - Dashboard (Estilo /assets/home principal.png)
# -----------------------------------------------------------------------------
CSS_DASHBOARD = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #1E293B;
}

/* Fundo da aplicação */
.stApp {
    background: #F4F7FA !important;
}

/* Barra Superior do Streamlit */
header[data-testid="stHeader"] {
    background-color: transparent !important;
}

/* Barra lateral com estilo de educação inteligente */
[data-testid="stSidebar"] {
    background: #10233A !important;
    border-right: 1px solid #1C3552 !important;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] span,
[data-testid="stSidebar"] label {
    color: #F1F5F9 !important;
}

[data-testid="stSidebar"] hr {
    border-color: rgba(255, 255, 255, 0.12) !important;
}

/* Itens de navegação do Sidebar */
[data-testid="stSidebar"] .stRadio > div {
    gap: 8px;
}

[data-testid="stSidebar"] .stRadio > div > label {
    background: transparent;
    padding: 10px 14px;
    border-radius: 12px;
    color: #E2E8F0 !important;
    font-weight: 500;
    transition: all 0.2s ease-in-out;
    border: 1px solid transparent;
}

[data-testid="stSidebar"] .stRadio > div > label:hover {
    background: rgba(255, 255, 255, 0.08);
    color: #FFFFFF !important;
}

[data-testid="stSidebar"] .stRadio > div > label[data-checked="true"],
[data-testid="stSidebar"] .stRadio > div > label:has(input:checked) {
    background: #DFF37A !important;
    color: #10233A !important;
    font-weight: 600;
    box-shadow: none;
}

/* Botões primários */
.stButton > button[kind="primary"],
.stButton > button:first-child:not([kind="secondary"]) {
    background: #2456A6 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 10px 22px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    box-shadow: 0 3px 10px rgba(36, 86, 166, 0.16) !important;
    transition: all 0.2s ease;
}

.stButton > button:hover {
    background: #4338CA !important;
    transform: translateY(-1px);
    box-shadow: 0 6px 18px rgba(78, 68, 180, 0.35) !important;
}

/* Campos de entrada */
.stTextInput > div > div > input,
.stSelectbox > div > div {
    border-radius: 12px !important;
    border: 1px solid #E2E8F0 !important;
    background-color: #FFFFFF !important;
    font-size: 14px !important;
    padding: 10px 14px !important;
    transition: all 0.2s ease;
}

.stTextInput > div > div > input:focus {
    border-color: #4E44B4 !important;
    box-shadow: 0 0 0 3px rgba(78, 68, 180, 0.15) !important;
}

/* Barra de Pesquisa Superior */
.top-search-bar {
    background: #FFFFFF;
    border: 1px solid #E8EBF3;
    border-radius: 14px;
    padding: 8px 16px;
    display: flex;
    align-items: center;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
    margin-bottom: 20px;
}

/* Banner de Boas-Vindas Lilás */
.welcome-banner {
    background: #FFFFFF;
    border-radius: 14px;
    padding: 28px 32px;
    margin-bottom: 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border: 1px solid #DDE6EF;
    border-left: 5px solid #2456A6;
    box-shadow: 0 4px 16px rgba(16, 35, 58, 0.05);
    position: relative;
    overflow: hidden;
}

.welcome-banner h2 {
    color: #38337A !important;
    font-size: 26px;
    font-weight: 800;
    margin: 0 0 8px 0;
    letter-spacing: -0.02em;
}

.welcome-banner p {
    color: #5A539B !important;
    font-size: 14px;
    font-weight: 500;
    line-height: 1.5;
    margin: 0;
    max-width: 580px;
}

.welcome-avatar-container {
    width: 90px;
    height: 90px;
    background: #FFFFFF;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #EAF1FB;
    box-shadow: none;
    border: 1px solid #C9D9EF;
    font-family: 'Manrope', sans-serif;
    font-size: 28px;
    color: #2456A6;
}

/* Cards Rápidos de KPI */
.kpi-card {
    background: #FFFFFF;
    border-radius: 12px;
    padding: 22px 24px;
    border: 1px solid #ECEFF7;
    box-shadow: 0 3px 12px rgba(16, 35, 58, 0.04);
    display: flex;
    align-items: center;
    gap: 18px;
    height: 100%;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.kpi-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(78, 68, 180, 0.08);
}

.kpi-icon-wrap {
    width: 54px;
    height: 54px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 26px;
    flex-shrink: 0;
}

.kpi-label {
    font-size: 13px;
    font-weight: 600;
    color: #64748B;
    margin: 0 0 4px 0;
    text-transform: capitalize;
}

.kpi-val {
    font-size: 30px;
    font-weight: 800;
    color: #1E293B;
    line-height: 1.1;
    margin: 0;
}

/* Card Principal da Atividade */
.activity-card {
    background: #FFFFFF;
    border-radius: 20px;
    padding: 26px;
    border: 1px solid #ECEFF7;
    box-shadow: 0 4px 18px rgba(0, 0, 0, 0.03);
    margin-bottom: 24px;
}

.activity-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
}

.activity-title {
    font-size: 20px;
    font-weight: 800;
    color: #1E293B;
    margin: 0;
}

.badge-pill-success {
    background-color: #DEF7EC;
    color: #03543F;
    font-size: 12px;
    font-weight: 700;
    padding: 4px 12px;
    border-radius: 9999px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

.badge-pill-warning {
    background-color: #FEF08A;
    color: #713F12;
    font-size: 12px;
    font-weight: 700;
    padding: 4px 12px;
    border-radius: 9999px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

.badge-pill-danger {
    background-color: #FDE8E8;
    color: #9B1C1C;
    font-size: 12px;
    font-weight: 700;
    padding: 4px 12px;
    border-radius: 9999px;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

/* Coluna de Métricas Laterais */
.metric-summary-box {
    background: #F8F9FD;
    border-radius: 14px;
    padding: 16px;
    border: 1px solid #EDF0F8;
    margin-bottom: 12px;
}

.metric-summary-label {
    font-size: 12px;
    font-weight: 600;
    color: #64748B;
    margin-bottom: 4px;
}

.metric-summary-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.metric-summary-value {
    font-size: 24px;
    font-weight: 800;
    color: #1E293B;
}

/* Cards de Cursos */
.course-card {
    background: #FFFFFF;
    border-radius: 16px;
    padding: 20px;
    border: 1px solid #EDF0F8;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.02);
    margin-bottom: 16px;
    transition: all 0.2s ease;
}

.course-card:hover {
    border-color: #D8D2EB;
    box-shadow: 0 6px 18px rgba(78, 68, 180, 0.06);
}

.course-card h4 {
    margin: 0 0 6px 0;
    font-size: 16px;
    font-weight: 700;
    color: #1E293B;
}

.course-card p {
    font-size: 13px;
    color: #64748B;
    margin: 0 0 12px 0;
}
</style>
"""

# -----------------------------------------------------------------------------
# CSS da Landing Page de Login (Estilo /assets/login.png - Notion Style)
# -----------------------------------------------------------------------------
CSS_LOGIN_LANDING = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #0F172A;
}

.stApp {
    background-color: #FFFFFF !important;
}

/* Oculta totalmente o sidebar do Streamlit no modo deslogado */
[data-testid="stSidebar"] {
    display: none !important;
}

header[data-testid="stHeader"] {
    display: none !important;
}

/* Navbar Notion */
.notion-navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 32px;
    border-bottom: 1px solid #F1F5F9;
    background: #FFFFFF;
    position: sticky;
    top: 0;
    z-index: 100;
}

.notion-brand {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 20px;
    font-weight: 800;
    color: #0F172A;
    text-decoration: none;
}

.notion-brand-icon {
    width: 36px;
    height: 36px;
    background: #0F172A;
    color: #FFFFFF;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    font-weight: 800;
}

.notion-nav-links {
    display: flex;
    align-items: center;
    gap: 28px;
    font-size: 14px;
    font-weight: 500;
    color: #475569;
}

/* Hero Section */
.hero-wrapper {
    max-width: 920px;
    margin: 48px auto 24px auto;
    text-align: center;
    padding: 0 20px;
}

.hero-pill {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #DCFCE7;
    color: #166534;
    padding: 6px 16px;
    border-radius: 9999px;
    font-size: 13px;
    font-weight: 600;
    margin-bottom: 24px;
}

.hero-pill-dot {
    width: 8px;
    height: 8px;
    background: #22C55E;
    border-radius: 50%;
}

.hero-title {
    font-size: 58px;
    line-height: 1.12;
    font-weight: 800;
    color: #0F172A;
    letter-spacing: -0.035em;
    margin-bottom: 20px;
}

.hero-title-highlight {
    background: #DCFCE7;
    color: #0F172A;
    padding: 2px 14px;
    border-radius: 20px;
    display: inline-flex;
    align-items: center;
    gap: 8px;
}

.hero-subtitle {
    font-size: 19px;
    line-height: 1.55;
    color: #475569;
    max-width: 720px;
    margin: 0 auto 36px auto;
    font-weight: 400;
}

/* Card de Autenticação */
.auth-box-container {
    max-width: 480px;
    margin: 0 auto 48px auto;
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 20px;
    padding: 32px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
}

/* Mockup da Janela Mac / Dashboard Preview */
.mockup-window {
    max-width: 960px;
    margin: 40px auto 60px auto;
    background: #FFFFFF;
    border: 1px solid #CBD5E1;
    border-radius: 16px;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.08);
    overflow: hidden;
}

.mockup-header {
    background: #F8FAFC;
    border-bottom: 1px solid #E2E8F0;
    padding: 12px 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.mockup-dot {
    width: 12px;
    height: 12px;
    border-radius: 50%;
}

.dot-red { background: #EF4444; }
.dot-yellow { background: #F59E0B; }
.dot-green { background: #10B981; }

.mockup-body {
    padding: 24px;
    background: #F8F9FD;
}
</style>
"""


def apply_dashboard_theme():
    """Aplica o tema do Dashboard principal inspirado em assets/home principal.png."""
    st.markdown(CSS_DASHBOARD, unsafe_allow_html=True)


def apply_login_landing_theme():
    """Aplica o tema da Landing Page e Login inspirado em assets/login.png."""
    st.markdown(CSS_LOGIN_LANDING, unsafe_allow_html=True)


def render_sidebar_header():
    """Renderiza a marca e o logotipo EduTrack AI no topo da barra lateral."""
    st.sidebar.markdown(
        """
        <div style="display: flex; align-items: center; gap: 12px; padding: 12px 4px 20px 4px;">
            <div style="
                width: 42px;
                height: 42px;
                background: #DFF37A;
                border-radius: 10px;
                display: flex;
                align-items: center;
                justify-content: center;
                box-shadow: 0 4px 12px rgba(0,0,0,0.25);
                font-size: 17px;
                color: #10233A;
            ">
                🎓
            </div>
            <div>
                <div style="font-size: 19px; font-weight: 800; color: #FFFFFF; line-height: 1.1; letter-spacing: -0.02em;">
                    educação inteligente
                </div>
                <div style="font-size: 11px; font-weight: 600; color: #C7D2FE; letter-spacing: 0.05em; text-transform: uppercase;">
                    EduTrack AI
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_welcome_banner(user_name: str = "Aluno(a)", days_streak: int = 4):
    """Renderiza o banner de boas-vindas lilás com saudação personalizada e avatar 3D."""
    clean_name = html.escape(str(user_name).strip() or "Estudante")
    st.markdown(
        f"""
        <div class="welcome-banner">
            <div>
                <h2>Olá novamente, {clean_name}</h2>
                <p>
                    Esta semana você manteve <b>{days_streak} dias consecutivos de estudos</b>! 
                    Continue no ritmo para alcançar suas metas acadêmicas e evoluir nas disciplinas.
                </p>
            </div>
            <div class="welcome-avatar-container">
                🧑‍🎓
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_cards(certificados: int = 18, em_andamento: int = 5, concluidos: int = 21):
    """Renderiza os 3 cartões rápidos de KPIs alinhados horizontalmente."""
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-icon-wrap" style="background: #EEF2FF; color: #4F46E5;">
                    📜
                </div>
                <div>
                    <div class="kpi-label">Certificados Conquistados</div>
                    <div class="kpi-val" style="color: #38337A;">{certificados}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-icon-wrap" style="background: #EFF6FF; color: #2563EB;">
                    📖
                </div>
                <div>
                    <div class="kpi-label">Disciplinas em Andamento</div>
                    <div class="kpi-val" style="color: #2563EB;">{em_andamento}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-icon-wrap" style="background: #F0FDF4; color: #16A34A;">
                    🎓
                </div>
                <div>
                    <div class="kpi-label">Disciplinas Concluídas</div>
                    <div class="kpi-val" style="color: #16A34A;">{concluidos}</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_landing_navbar():
    """Renderiza o cabeçalho minimalista da Landing Page estilo Notion."""
    st.markdown(
        """
        <div class="notion-navbar">
            <div class="notion-brand">
                <div class="notion-brand-icon">🎓</div>
                <span>EduTrack AI</span>
            </div>
            <div class="notion-nav-links">
                <span>Produto ▾</span>
                <span>Recursos ▾</span>
                <span>Metodologia</span>
                <span>Preços</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
