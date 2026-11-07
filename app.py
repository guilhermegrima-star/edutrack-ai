import streamlit as st
import pandas as pd
import numpy as np
import io
import datetime
import hashlib

# Configuração da página
st.set_page_config(
    page_title="EduTrack AI",
    page_icon="🎓",
    layout="wide"
)

# Título principal
st.title("🎓 EduTrack AI")
st.subheader("Painel de Acompanhamento Académico")

# Criar dados de exemplo para os alunos
@st.cache_data
def carregar_dados():
    dados = {
        "ID": [101, 102, 103, 104, 105, 106, 107, 108],
        "Nome": ["Ana Silva", "Bruno Santos", "Carla Costa", "Diogo Rocha", 
                 "Elena Martins", "Fábio Lima", "Gonçalo Alves", "Helena Ribeiro"],
        "Turma": ["A", "B", "A", "C", "B", "A", "C", "B"],
        "Nota Média": [16.5, 9.2, 14.0, 8.5, 18.2, 11.0, 7.8, 15.4],
        "Frequência (%)": [95, 70, 88, 65, 98, 82, 60, 91],
        "Estado": ["Aprovado", "Em Risco", "Aprovado", "Em Risco", 
                  "Aprovado", "Aprovado", "Em Risco", "Aprovado"]
    }
    return pd.DataFrame(dados)

df_alunos = carregar_dados()

# Menu lateral
st.sidebar.header("Navegação")
opcao = st.sidebar.radio("Ir para:", ["Visão Geral", "Alunos", "Configurações"])

if opcao == "Visão Geral":
    st.markdown("### 📊 Visão Geral do Desempenho")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Alunos", len(df_alunos))
    col2.metric("Média Geral", f"{df_alunos['Nota Média'].mean():.1f} / 20")
    col3.metric("Taxa de Frequência", f"{df_alunos['Frequência (%)'].mean():.0f}%")
    col4.metric("Alunos em Risco", len(df_alunos[df_alunos["Estado"] == "Em Risco"]))

    st.markdown("---")

    st.markdown("### 📈 Distribuição de Notas por Disciplina")
    chart_data = pd.DataFrame(
        np.random.normal(14, 2.5, size=(20, 3)),
        columns=["Matemática", "Programação", "Bases de Dados"]
    )
    st.line_chart(chart_data)

elif opcao == "Alunos":
    st.markdown("### 👨‍🎓 Gestão e Consulta de Alunos")
    
    # Filtros interativos
    col_busca, col_filtro = st.columns([2, 1])
    with col_busca:
        nome_busca = st.text_input("🔍 Pesquisar por nome:")
    with col_filtro:
        estado_filtro = st.selectbox("Filtrar por Estado:", ["Todos", "Aprovado", "Em Risco"])
    
    # Aplicar filtros
    df_filtrado = df_alunos.copy()
    if nome_busca:
        df_filtrado = df_filtrado[df_filtrado["Nome"].str.contains(nome_busca, case=False)]
    if estado_filtro != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Estado"] == estado_filtro]
        
    # Exibir a tabela interativa
    st.dataframe(df_filtrado, use_container_width=True)

    st.markdown("---")

    # Secção de Geração e Download de Relatório PDF
    st.markdown("### 📄 Exportar Relatório de Desempenho (PDF)")
    st.caption("Gere um documento formal em PDF com o desempenho acadêmico, notas por disciplina e assiduidade utilizando ReportLab.")

    col_sel, col_acoes = st.columns([2, 1])

    with col_sel:
        aluno_nome_sel = st.selectbox(
            "Selecione o(a) aluno(a) para emissão do relatório:",
            options=df_filtrado["Nome"].tolist() if not df_filtrado.empty else df_alunos["Nome"].tolist(),
            help="Escolha o aluno para compilar o boletim/relatório individual.",
        )

    # Recupera o registro do aluno selecionado
    registro_aluno = df_alunos[df_alunos["Nome"] == aluno_nome_sel].iloc[0].to_dict()
    media_geral_turma = float(df_alunos["Nota Média"].mean())

    with col_acoes:
        st.write("")  # Espaçamento vertical
        st.write("")
        gerar_clicado = st.button("📊 Gerar Relatório PDF", type="primary", use_container_width=True)

    # Função geradora de PDF com ReportLab
    def gerar_pdf_aluno(aluno: dict, media_turma: float) -> io.BytesIO:
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
            textColor=colors.HexColor("#1E3A8A"),
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
            textColor=colors.HexColor("#1E3A8A"),
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

        # 1. Cabeçalho
        story.append(Paragraph("🎓 EduTrack AI", style_title))
        story.append(Paragraph("Relatório Individual de Desempenho Académico do Aluno", style_sub))
        story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1E3A8A"), spaceAfter=12))

        # 2. Informações do Aluno
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

        # 3. Painel de Indicadores
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

        # 4. Avaliação por Disciplina
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
            ("Matemática Aplicada", "Prof. Dr. Ricardo Neves", "60h", max(0.0, min(20.0, round(14.5 + offset, 1)))),
            ("Algoritmos e Programação", "Prof. Ana Ribeiro", "80h", max(0.0, min(20.0, round(15.2 + offset, 1)))),
            ("Bases de Dados Relacionais", "Prof. Carlos Duarte", "60h", max(0.0, min(20.0, round(13.8 + offset, 1)))),
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
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("BOX", (0, 0), (-1, -1), 1, colors.HexColor("#CBD5E1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ("PADDING", (0, 0), (-1, -1), 5),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        story.append(t_disc)
        story.append(Spacer(1, 12))

        # 5. Parecer Pedagógico
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

        # 6. Rodapé com Código de Autenticidade
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

    # Gerenciamento de geração do PDF
    if gerar_clicado:
        with st.spinner(f"Compilando relatório em PDF para {registro_aluno['Nome']}..."):
            try:
                pdf_buffer = gerar_pdf_aluno(registro_aluno, media_geral_turma)
                st.session_state["pdf_aluno_bytes"] = pdf_buffer.getvalue()
                st.session_state["pdf_aluno_nome"] = registro_aluno["Nome"]
                st.success(f"Relatório gerado com sucesso para **{registro_aluno['Nome']}**!")
            except Exception as e:
                st.error(f"Erro ao gerar o relatório em PDF: {e}")

    # Exibe o botão de download se o PDF estiver disponível
    if "pdf_aluno_bytes" in st.session_state and st.session_state["pdf_aluno_bytes"]:
        nome_arquivo_sanitizado = st.session_state.get("pdf_aluno_nome", "aluno").lower().replace(" ", "_")
        col_down1, col_down2 = st.columns([1, 2])
        with col_down1:
            st.download_button(
                label="⬇️ Baixar Relatório (PDF)",
                data=st.session_state["pdf_aluno_bytes"],
                file_name=f"relatorio_desempenho_{nome_arquivo_sanitizado}.pdf",
                mime="application/pdf",
                type="primary",
                use_container_width=True,
            )
        with col_down2:
            st.info(f"Relatório pronto para download: **{st.session_state.get('pdf_aluno_nome')}**.")

else:
    st.warning("⚙️ Configurações do Sistema.")