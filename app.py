
import streamlit as st
import pandas as pd
import os
from datetime import datetime, date
import hashlib

st.set_page_config(page_title="BALICAR - Sistema Financeiro", layout="wide")

# ------------------- Autenticação -------------------
def verificar_login(usuario, senha):
    return usuario == "admin" and senha == "balicar4195"

def login():
    st.title("🔐 Sistema Financeiro - BALICAR")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar", use_container_width=True):
        if verificar_login(usuario, senha):
            st.session_state["logado"] = True
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos.")

if "logado" not in st.session_state:
    st.session_state["logado"] = False

if not st.session_state["logado"]:
    login()
    st.stop()

# ------------------- Arquivos -------------------
ARQUIVO_LANCAMENTOS = "lancamentos.csv"
ARQUIVO_CONTAS = "contas.csv"
ARQUIVO_AGENDA = "agenda.csv"

def carregar_dados(caminho, colunas):
    if os.path.exists(caminho):
        return pd.read_csv(caminho)
    return pd.DataFrame(columns=colunas)

def salvar_dados(df, caminho):
    df.to_csv(caminho, index=False)

# ------------------- Dados -------------------
df_lanc = carregar_dados(ARQUIVO_LANCAMENTOS, ["Data", "Tipo", "Categoria", "Descrição", "Valor", "Conta"])
df_contas = carregar_dados(ARQUIVO_CONTAS, ["Nome", "Saldo"])
df_agenda = carregar_dados(ARQUIVO_AGENDA, ["Data", "Tipo", "Descrição", "Valor"])

# ------------------- Menu -------------------
menu = st.sidebar.selectbox("📂 Menu", ["Lançamentos", "Contas Bancárias", "Agenda", "Relatórios"])

# ------------------- Lançamentos -------------------
if menu == "Lançamentos":
    st.header("💸 Lançamentos Financeiros")
    with st.form("novo_lancamento"):
        col1, col2, col3 = st.columns(3)
        with col1:
            data = st.date_input("Data", value=date.today())
            tipo = st.selectbox("Tipo", ["Receita", "Despesa"])
        with col2:
            categoria = st.text_input("Categoria")
            conta = st.selectbox("Conta", df_contas["Nome"] if not df_contas.empty else [])
        with col3:
            descricao = st.text_input("Descrição")
            valor = st.number_input("Valor", min_value=0.0, step=0.01)

        if st.form_submit_button("Salvar"):
            if descricao and categoria and conta:
                novo = {
                    "Data": data,
                    "Tipo": tipo,
                    "Categoria": categoria,
                    "Descrição": descricao,
                    "Valor": valor,
                    "Conta": conta
                }
                df_lanc = pd.concat([df_lanc, pd.DataFrame([novo])], ignore_index=True)
                salvar_dados(df_lanc, ARQUIVO_LANCAMENTOS)
                st.success("Lançamento salvo com sucesso!")
                st.rerun()

    st.subheader("📋 Lançamentos Salvos")
    for i, row in df_lanc.iterrows():
        with st.expander(f"{row['Data']} - {row['Tipo']} - {row['Descrição']}"):
            with st.form(f"edit_{i}"):
                col1, col2 = st.columns(2)
                with col1:
                    nova_data = st.date_input("Data", value=pd.to_datetime(row["Data"]).date(), key=f"data_{i}")
                    novo_tipo = st.selectbox("Tipo", ["Receita", "Despesa"], index=["Receita", "Despesa"].index(row["Tipo"]), key=f"tipo_{i}")
                    nova_cat = st.text_input("Categoria", value=row["Categoria"], key=f"cat_{i}")
                with col2:
                    nova_desc = st.text_input("Descrição", value=row["Descrição"], key=f"desc_{i}")
                    novo_valor = st.number_input("Valor", value=row["Valor"], key=f"val_{i}")
                    nova_conta = st.selectbox("Conta", df_contas["Nome"] if not df_contas.empty else [], index=df_contas[df_contas["Nome"] == row["Conta"]].index[0] if row["Conta"] in df_contas["Nome"].values else 0, key=f"conta_{i}")
                col3, col4 = st.columns(2)
                with col3:
                    if st.form_submit_button("Salvar edição"):
                        df_lanc.at[i, "Data"] = nova_data
                        df_lanc.at[i, "Tipo"] = novo_tipo
                        df_lanc.at[i, "Categoria"] = nova_cat
                        df_lanc.at[i, "Descrição"] = nova_desc
                        df_lanc.at[i, "Valor"] = novo_valor
                        df_lanc.at[i, "Conta"] = nova_conta
                        salvar_dados(df_lanc, ARQUIVO_LANCAMENTOS)
                        st.success("Editado com sucesso!")
                        st.rerun()
                with col4:
                    if st.form_submit_button("🗑 Excluir"):
                        df_lanc = df_lanc.drop(i).reset_index(drop=True)
                        salvar_dados(df_lanc, ARQUIVO_LANCAMENTOS)
                        st.success("Excluído!")
                        st.rerun()
