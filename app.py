
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import hashlib
import os

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
# Funções de persistência
# ------------------------
CSV_PATH = "dados_financeiros.csv"

def carregar_dados():
    if os.path.exists(CSV_PATH):
        return pd.read_csv(CSV_PATH, parse_dates=["Data"])
    else:
        return pd.DataFrame(columns=["Data", "Tipo", "Categoria", "Descrição", "Valor"])

def salvar_dados(df):
    df.to_csv(CSV_PATH, index=False)

# ------------------------
# Inicialização
# ------------------------
st.sidebar.success("Logado como: " + st.session_state['user'])
st.sidebar.title("📚 Menu")
menu = st.sidebar.radio("Navegar para:", ["Lançamentos", "Relatórios"])

if "dados" not in st.session_state:
    st.session_state["dados"] = carregar_dados()

if "edit_index" not in st.session_state:
    st.session_state["edit_index"] = None

if "delete_index" not in st.session_state:
    st.session_state["delete_index"] = None

# ------------------------
# Página de Lançamentos
# ------------------------
if menu == "Lançamentos":
    st.title("💰 Lançamentos Financeiros")

    if st.session_state["delete_index"] is not None:
        st.session_state["dados"] = st.session_state["dados"].drop(st.session_state["delete_index"]).reset_index(drop=True)
        salvar_dados(st.session_state["dados"])
        st.success("Lançamento excluído com sucesso.")
        st.session_state["delete_index"] = None

    if st.session_state["edit_index"] is None:
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
                salvar_dados(st.session_state["dados"])
                st.success("Lançamento adicionado com sucesso!")
    else:
        st.subheader("✏️ Editar Lançamento")
        dados = st.session_state["dados"]
        row = dados.loc[st.session_state["edit_index"]]
        with st.form("form_edicao"):
            col1, col2 = st.columns(2)
            with col1:
                tipo = st.selectbox("Tipo", ["Receita", "Despesa"], index=["Receita", "Despesa"].index(row["Tipo"]))
                categoria = st.selectbox("Categoria", ["Venda", "Salário", "Investimento", "Aluguel", "Manutenção", "Outros"],
                                         index=["Venda", "Salário", "Investimento", "Aluguel", "Manutenção", "Outros"].index(row["Categoria"]))
            with col2:
                data = st.date_input("Data", value=pd.to_datetime(row["Data"]))
                valor = st.number_input("Valor", value=float(row["Valor"]), min_value=0.0, step=0.01)
            descricao = st.text_input("Descrição", value=row["Descrição"])
            atualizar = st.form_submit_button("Atualizar")

            if atualizar:
                st.session_state["dados"].loc[st.session_state["edit_index"]] = [data, tipo, categoria, descricao, valor]
                salvar_dados(st.session_state["dados"])
                st.success("Lançamento atualizado com sucesso!")
                st.session_state["edit_index"] = None

    st.subheader("📄 Lista de Lançamentos")
    dados = st.session_state["dados"]
    for i in range(len(dados)):
        col1, col2, col3 = st.columns([6, 1, 1])
        col1.write(f"{dados.loc[i, 'Data']} | {dados.loc[i, 'Tipo']} | {dados.loc[i, 'Categoria']} | {dados.loc[i, 'Descrição']} | R$ {dados.loc[i, 'Valor']:.2f}")
        if col2.button("✏️", key=f"edit_{i}"):
            st.session_state["edit_index"] = i
        if col3.button("🗑️", key=f"del_{i}"):
            st.session_state["delete_index"] = i
        st.write("---")

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

        st.subheader("📅 Receitas e Despesas por Mês")
        resumo = dados.groupby(["AnoMes", "Tipo"])["Valor"].sum().unstack().fillna(0)
        st.bar_chart(resumo)

        st.subheader("📂 Despesas por Categoria")
        despesas = dados[dados["Tipo"] == "Despesa"]
        if not despesas.empty:
            categoria_data = despesas.groupby("Categoria")["Valor"].sum()
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots()
            ax.pie(categoria_data, labels=categoria_data.index, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            st.pyplot(fig)
        else:
            st.info("Ainda não há despesas para exibir o gráfico.")
