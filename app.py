import streamlit as st
import pandas as pd
import numpy as np

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

else:
    st.warning("⚙️ Configurações do Sistema.")