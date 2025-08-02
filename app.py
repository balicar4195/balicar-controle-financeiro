
import streamlit as st

st.set_page_config(page_title="BALICAR - Controle Financeiro", layout="wide")
st.sidebar.title("📚 Menu")
menu = st.sidebar.radio("Navegar para:", ["Lançamentos", "Relatórios", "Agenda", "Contas"])

if menu == "Lançamentos":
    st.title("💰 Lançamentos")
    st.write("Funcionalidade ativa: salvar, editar, excluir")

elif menu == "Relatórios":
    st.title("📊 Relatórios")
    st.write("Gráficos de receitas e despesas")

elif menu == "Agenda":
    st.title("📅 Agenda")
    st.write("Tarefas do dia e contas futuras")

elif menu == "Contas":
    st.title("🏦 Contas")
    st.write("Cadastro de contas e saldo atual")
