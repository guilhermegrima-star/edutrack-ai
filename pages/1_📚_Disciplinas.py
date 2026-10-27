import streamlit as st

st.set_page_config(page_title="Disciplinas - EduTrack AI", page_icon="📚", layout="wide")

st.title("📚 Gestão de Disciplinas")

# Uso de Abas (tabs) para organizar o layout
aba1, aba2 = st.tabs(["📋 Listagem de Disciplinas", "➕ Cadastrar Nova Disciplina"])

with aba1:
    st.subheader("Disciplinas Ativas")
    st.write("• **Matemática Aplicada** - Prof. Silva (Carga Horária: 60h)")
    st.write("• **Programação Python** - Prof. Furlan (Carga Horária: 80h)")
    st.write("• **Bases de Dados** - Profª. Costa (Carga Horária: 60h)")

with aba2:
    st.subheader("Formulário de Cadastro")
    with st.form("form_disciplina"):
        nome = st.text_input("Nome da Disciplina:")
        professor = st.text_input("Nome do Professor:")
        carga_horaria = st.number_input("Carga Horária (horas):", min_value=10, max_value=200, value=60)
        
        submetido = st.form_submit_button("Salvar Disciplina")
        if submetido:
            st.success(f"Disciplina '{nome}' cadastrada com sucesso!")