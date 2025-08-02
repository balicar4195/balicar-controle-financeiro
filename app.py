
import streamlit as st
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="BALICAR - Controle Financeiro", layout="wide")

# Estilo mais claro e com fontes maiores
st.markdown("""
    <style>
        body, .stApp {
            background-color: #f9f9f9;
            color: #111111;
        }
        h1, h2, h3, h4, h5, h6 {
            font-size: 28px !important;
            color: #000000;
        }
        .stTextInput > label, .stSelectbox > label, .stDateInput > label,
        .stNumberInput > label, .stMultiSelect > label {
            font-size: 18px !important;
        }
        .stButton > button {
            font-size: 18px !important;
        }
        .stMarkdown {
            font-size: 18px !important;
        }
    </style>
""", unsafe_allow_html=True)

# Logo no topo
st.image("logo.png", width=300)
st.title("💼 BALICAR - Sistema de Controle Financeiro")

# Sessão de dados
if "dados" not in st.session_state:
    st.session_state.dados = pd.DataFrame(columns=["Tipo", "Descrição", "Valor", "Data", "Categoria", "Status", "Conta"])

# Sessão de contas
if "contas" not in st.session_state:
    st.session_state.contas = {"Caixa": 0.0, "Carteira": 0.0}

# Sessão de tarefas
if "tarefas" not in st.session_state:
    st.session_state.tarefas = []

# Aba de cadastro
with st.expander("➕ Adicionar Lançamento"):
    tipo = st.selectbox("Tipo", ["Receita", "Despesa"])
    descricao = st.text_input("Descrição")
    valor = st.number_input("Valor", step=0.01)
    data = st.date_input("Data", value=datetime.today())
    categoria = st.text_input("Categoria")
    status = st.selectbox("Status", ["Pendente", "Pago"])
    conta = st.selectbox("Conta", list(st.session_state.contas.keys()))
    if st.button("Adicionar"):
        novo = {"Tipo": tipo, "Descrição": descricao, "Valor": valor, "Data": data.strftime('%Y-%m-%d'), 
                "Categoria": categoria, "Status": status, "Conta": conta}
        st.session_state.dados = pd.concat([st.session_state.dados, pd.DataFrame([novo])], ignore_index=True)
        st.success("Lançamento adicionado com sucesso!")

# Aba de contas correntes
with st.expander("🏦 Saldos de Contas Correntes"):
    for conta, saldo in st.session_state.contas.items():
        st.write(f"**{conta}:** R$ {saldo:,.2f}")
    nova_conta = st.text_input("Adicionar nova conta")
    if st.button("Criar conta"):
        if nova_conta and nova_conta not in st.session_state.contas:
            st.session_state.contas[nova_conta] = 0.0
            st.success("Conta criada com sucesso!")

# Aba de tarefas
with st.expander("🗓️ Tarefas do Dia"):
    tarefa = st.text_input("Nova Tarefa")
    if st.button("Adicionar Tarefa"):
        if tarefa:
            st.session_state.tarefas.append(tarefa)
            st.success("Tarefa adicionada!")
    for i, t in enumerate(st.session_state.tarefas):
        st.write(f"{i+1}. {t}")

# Filtros e exibição
st.subheader("📊 Lançamentos")
filtro_tipo = st.multiselect("Filtrar por Tipo", options=["Receita", "Despesa"])
filtro_status = st.multiselect("Filtrar por Status", options=["Pendente", "Pago"])
filtro_categoria = st.text_input("Filtrar por Categoria")

df_filtrado = st.session_state.dados.copy()

if filtro_tipo:
    df_filtrado = df_filtrado[df_filtrado["Tipo"].isin(filtro_tipo)]
if filtro_status:
    df_filtrado = df_filtrado[df_filtrado["Status"].isin(filtro_status)]
if filtro_categoria:
    df_filtrado = df_filtrado[df_filtrado["Categoria"].str.contains(filtro_categoria, case=False, na=False)]

st.dataframe(df_filtrado, use_container_width=True)

# Cálculo de saldo
saldo = 0
for _, row in df_filtrado.iterrows():
    if row["Tipo"] == "Receita":
        saldo += row["Valor"]
    else:
        saldo -= row["Valor"]

st.markdown(f"### 💰 Saldo Total: R$ {saldo:,.2f}")
