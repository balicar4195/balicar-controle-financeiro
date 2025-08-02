
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import hashlib

st.set_page_config(page_title="BALICAR - Controle Financeiro", layout="wide")

# ------------------------
# Autenticação simples
# ------------------------
users = {
    "admin": hashlib.sha256("senha123".encode()).hexdigest()
}

def login():
    st.sidebar.title("🔒 Login")
    username = st.sidebar.text_input("Usuário")
    password = st.sidebar.text_input("Senha", type="password")
    if st.sidebar.button("Entrar"):
        if username in users and users[username] == hashlib.sha256(password.encode()).hexdigest():
            st.session_state['logged_in'] = True
            st.session_state['user'] = username
        else:
            st.sidebar.error("Usuário ou senha incorretos.")

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    login()
    st.stop()

# ------------------------
# Dados simulados
# ------------------------
st.sidebar.success("Logado como: " + st.session_state['user'])
st.sidebar.title("📚 Menu")
menu = st.sidebar.radio("Navegar para:", ["Lançamentos", "Relatórios"])

if "dados" not in st.session_state:
    st.session_state["dados"] = pd.DataFrame(columns=["Data", "Tipo", "Categoria", "Descrição", "Valor"])

# ------------------------
# Página de Lançamentos
# ------------------------
if menu == "Lançamentos":
    st.title("💰 Lançamentos Financeiros")

    with st.form("form_lancamento"):
        col1, col2 = st.columns(2)
        with col1:
            tipo = st.selectbox("Tipo", ["Receita", "Despesa"])
            categoria = st.selectbox("Categoria", ["Venda", "Salário", "Investimento", "Aluguel", "Manutenção", "Outros"])
        with col2:
            data = st.date_input("Data", value=datetime.today())
            valor = st.number_input("Valor", min_value=0.0, step=0.01)
        descricao = st.text_input("Descrição")
        salvar = st.form_submit_button("Salvar")

        if salvar:
            novo = pd.DataFrame([[data, tipo, categoria, descricao, valor]],
                                columns=["Data", "Tipo", "Categoria", "Descrição", "Valor"])
            st.session_state["dados"] = pd.concat([st.session_state["dados"], novo], ignore_index=True)
            st.success("Lançamento adicionado com sucesso!")

    st.subheader("📄 Lista de Lançamentos")
    st.dataframe(st.session_state["dados"], use_container_width=True)

# ------------------------
# Página de Relatórios
# ------------------------
elif menu == "Relatórios":
    st.title("📊 Relatórios Financeiros")

    dados = st.session_state["dados"]
    if dados.empty:
        st.info("Nenhum dado disponível.")
    else:
        dados["Data"] = pd.to_datetime(dados["Data"])
        dados["AnoMes"] = dados["Data"].dt.to_period("M").astype(str)

        col1, col2, col3 = st.columns(3)
        total_receitas = dados[dados["Tipo"] == "Receita"]["Valor"].sum()
        total_despesas = dados[dados["Tipo"] == "Despesa"]["Valor"].sum()
        saldo = total_receitas - total_despesas

        col1.metric("Total de Receitas", f"R$ {total_receitas:,.2f}")
        col2.metric("Total de Despesas", f"R$ {total_despesas:,.2f}")
        col3.metric("Saldo", f"R$ {saldo:,.2f}")

        # Gráfico de Barras
        st.subheader("📅 Receitas e Despesas por Mês")
        resumo = dados.groupby(["AnoMes", "Tipo"])["Valor"].sum().unstack().fillna(0)
        st.bar_chart(resumo)

        # Gráfico de Pizza
        st.subheader("📂 Despesas por Categoria")
        despesas = dados[dados["Tipo"] == "Despesa"]
        if not despesas.empty:
            categoria_data = despesas.groupby("Categoria")["Valor"].sum()
            fig, ax = plt.subplots()
            ax.pie(categoria_data, labels=categoria_data.index, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            st.pyplot(fig)
        else:
            st.info("Ainda não há despesas para exibir o gráfico.")
