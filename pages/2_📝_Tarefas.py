import streamlit as st

st.set_page_config(page_title="Tarefas - EduTrack AI", page_icon="📝", layout="wide")

st.title("📝 Organização de Tarefas")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📌 Pendentes")
    with st.expander("Entrega da Tarefa 09 - Streamlit UI"):
        st.write("Desenvolver a estrutura MPA e aplicar layouts avançados.")
        st.write("**Prazo:** Hoje")

with col2:
    st.subheader("✅ Concluídas")
    with st.expander("Configuração do Ambiente Virtual"):
        st.write("Criação do venv, ativação e instalação das bibliotecas.")