
import streamlit as st
from PIL import Image

# Logo
st.set_page_config(page_title="BALICAR Financeiro", layout="wide")

# Login fixo
def check_login(username, password):
    return username == "admin" and password == "1234"

# Interface de login
def login_screen():
    st.title("Login - Sistema BALICAR")
    user = st.text_input("Usuário")
    passwd = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if check_login(user, passwd):
            st.session_state["logado"] = True
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha incorretos.")

# Interface principal com menu lateral
def main_app():
    logo = Image.open("logo.png")
    st.sidebar.image(logo, use_column_width=True)
    menu = st.sidebar.radio("Menu", ["Lançamentos", "Agenda", "Relatórios", "Gráficos", "Contas Bancárias"])

    st.title("Sistema de Controle Financeiro - BALICAR")

    if menu == "Lançamentos":
        st.header("📌 Lançamentos")
        st.info("Área para adicionar, editar ou excluir lançamentos.")
    elif menu == "Agenda":
        st.header("📅 Agenda de Tarefas")
        st.info("Veja tarefas do dia e contas agendadas.")
    elif menu == "Relatórios":
        st.header("📄 Relatórios")
        st.info("Filtre receitas e despesas por mês ou categoria.")
    elif menu == "Gráficos":
        st.header("📊 Gráficos")
        st.info("Visualize o desempenho financeiro em gráficos.")
    elif menu == "Contas Bancárias":
        st.header("🏦 Contas Bancárias")
        st.info("Gerencie os saldos e contas cadastradas.")

# Estado de login
if "logado" not in st.session_state:
    st.session_state["logado"] = False

if st.session_state["logado"]:
    main_app()
else:
    login_screen()
