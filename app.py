
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import hashlib
import os

st.set_page_config(page_title="BALICAR - Controle Financeiro", layout="wide")

# ------------------------
# Autenticação
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
# Estrutura dos dados
# ------------------------
CSV_LANCAMENTOS = "dados_financeiros.csv"
CSV_CONTAS = "contas.csv"
CSV_TAREFAS = "tarefas.csv"

def carregar_csv(caminho, colunas, parse_data=None):
    if os.path.exists(caminho):
        return pd.read_csv(caminho, parse_dates=parse_data)
    else:
        return pd.DataFrame(columns=colunas)

def salvar_csv(df, caminho):
    df.to_csv(caminho, index=False)

# Inicialização de dados
if "dados" not in st.session_state:
    st.session_state["dados"] = carregar_csv(CSV_LANCAMENTOS, ["Data", "Tipo", "Categoria", "Descrição", "Valor"], ["Data"])

if "contas" not in st.session_state:
    st.session_state["contas"] = carregar_csv(CSV_CONTAS, ["Conta", "Saldo"])

if "tarefas" not in st.session_state:
    st.session_state["tarefas"] = carregar_csv(CSV_TAREFAS, ["Data", "Tarefa", "Concluida"])

# ------------------------
# MENU LATERAL COMPLETO
# ------------------------
st.sidebar.success("Logado como: " + st.session_state['user'])
st.sidebar.title("📚 Menu")
menu = st.sidebar.radio("Navegar para:", ["Lançamentos", "Relatórios", "Agenda", "Contas"])
