
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


# ------------------------
# ABA CONTAS
# ------------------------
if menu == "Contas":
    st.title("🏦 Contas e Saldos")

    with st.form("form_conta"):
        col1, col2 = st.columns(2)
        with col1:
            nome_conta = st.text_input("Nome da Conta")
        with col2:
            saldo_inicial = st.number_input("Saldo Inicial", step=0.01, min_value=0.0)
        adicionar = st.form_submit_button("Adicionar Conta")

        if adicionar and nome_conta:
            nova = pd.DataFrame([[nome_conta, saldo_inicial]], columns=["Conta", "Saldo"])
            st.session_state["contas"] = pd.concat([st.session_state["contas"], nova], ignore_index=True)
            salvar_csv(st.session_state["contas"], CSV_CONTAS)
            st.success("Conta adicionada com sucesso!")

    st.subheader("💳 Contas Cadastradas")
    if not st.session_state["contas"].empty:
        st.dataframe(st.session_state["contas"], use_container_width=True)
    else:
        st.info("Nenhuma conta cadastrada.")

# ------------------------
# ABA AGENDA
# ------------------------
elif menu == "Agenda":
    st.title("📅 Agenda: Contas Futuras e Tarefas")

    dados = st.session_state["dados"]
    hoje = pd.to_datetime(datetime.today().date())

    # CONTAS FUTURAS
    st.subheader("💸 Contas Agendadas (Receber/Pagar)")
    futuras = dados[pd.to_datetime(dados["Data"]) > hoje]
    vencem_hoje = dados[pd.to_datetime(dados["Data"]) == hoje]
    vencidas = dados[pd.to_datetime(dados["Data"]) < hoje]

    def mostrar_lista(df, titulo, cor):
        if df.empty:
            return
        st.markdown(f"### <span style='color:{cor}'>{titulo}</span>", unsafe_allow_html=True)
        for i in df.index:
            with st.expander(f"{df.loc[i, 'Tipo']} | {df.loc[i, 'Categoria']} | {df.loc[i, 'Descrição']} | {df.loc[i, 'Data'].strftime('%d/%m/%Y')} | R$ {df.loc[i, 'Valor']:.2f}"):
                if st.button(f"✔ Marcar como {df.loc[i, 'Tipo'].lower()}", key=f"marcar_{i}"):
                    lanc = df.loc[i]
                    st.session_state["dados"] = st.session_state["dados"].drop(i).reset_index(drop=True)
                    hoje_lanc = lanc.copy()
                    hoje_lanc["Data"] = hoje
                    st.session_state["dados"] = pd.concat([st.session_state["dados"], pd.DataFrame([hoje_lanc])], ignore_index=True)
                    salvar_csv(st.session_state["dados"], CSV_LANCAMENTOS)
                    st.success("Lançamento movido para hoje.")

    mostrar_lista(vencidas, "Atrasadas", "red")
    mostrar_lista(vencem_hoje, "Vencem Hoje", "orange")
    mostrar_lista(futuras, "Futuras", "green")

    # TAREFAS
    st.subheader("✅ Tarefas do Dia e Futuras")
    with st.form("form_tarefa"):
        col1, col2 = st.columns([3, 1])
        with col1:
            tarefa = st.text_input("Descrição da tarefa")
        with col2:
            data_tarefa = st.date_input("Data", value=hoje)
        adicionar_tarefa = st.form_submit_button("Adicionar")

        if adicionar_tarefa and tarefa:
            nova_tarefa = pd.DataFrame([[data_tarefa, tarefa, False]], columns=["Data", "Tarefa", "Concluida"])
            st.session_state["tarefas"] = pd.concat([st.session_state["tarefas"], nova_tarefa], ignore_index=True)
            salvar_csv(st.session_state["tarefas"], CSV_TAREFAS)
            st.success("Tarefa adicionada com sucesso!")

    tarefas_hoje = st.session_state["tarefas"][pd.to_datetime(st.session_state["tarefas"]["Data"]) == hoje]
    tarefas_futuras = st.session_state["tarefas"][pd.to_datetime(st.session_state["tarefas"]["Data"]) > hoje]

    def exibir_tarefas(lista, titulo):
        if lista.empty:
            return
        st.markdown(f"### {titulo}")
        for i in lista.index:
            concluida = st.checkbox(f"{lista.loc[i, 'Tarefa']} ({lista.loc[i, 'Data'].strftime('%d/%m/%Y')})", value=lista.loc[i, 'Concluida'], key=f"check_{i}")
            if concluida != lista.loc[i, 'Concluida']:
                st.session_state["tarefas"].loc[i, "Concluida"] = concluida
                salvar_csv(st.session_state["tarefas"], CSV_TAREFAS)

    exibir_tarefas(tarefas_hoje, "Tarefas do Dia")
    exibir_tarefas(tarefas_futuras, "Tarefas Futuras")
