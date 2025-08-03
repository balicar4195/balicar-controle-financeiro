
import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Contas Bancárias", layout="wide")

st.title("🏦 Contas Bancárias BALICAR")

ARQUIVO_CONTAS = "contas.csv"

# Função para carregar dados
def carregar_contas():
    if os.path.exists(ARQUIVO_CONTAS):
        return pd.read_csv(ARQUIVO_CONTAS)
    return pd.DataFrame(columns=["Conta", "Saldo"])

# Função para salvar dados
def salvar_contas(df):
    df.to_csv(ARQUIVO_CONTAS, index=False)

# Carregar dados
df_contas = carregar_contas()

# Formulário para adicionar nova conta
st.subheader("➕ Nova Conta Bancária")
with st.form("form_nova_conta"):
    nome_conta = st.text_input("Nome da Conta")
    saldo_inicial = st.number_input("Saldo Inicial", step=0.01, format="%.2f")
    adicionar = st.form_submit_button("Adicionar")
    if adicionar and nome_conta:
        df_contas = pd.concat([df_contas, pd.DataFrame([{"Conta": nome_conta, "Saldo": saldo_inicial}])], ignore_index=True)
        salvar_contas(df_contas)
        st.success("Conta adicionada com sucesso!")
        st.rerun()

# Mostrar contas e permitir edição
st.subheader("📋 Contas Cadastradas")
for i, row in df_contas.iterrows():
    with st.expander(f"{row['Conta']}"):
        with st.form(f"form_editar_{i}"):
            novo_nome = st.text_input("Nome da Conta", value=row["Conta"], key=f"nome_{i}")
            novo_saldo = st.number_input("Saldo", value=row["Saldo"], step=0.01, format="%.2f", key=f"saldo_{i}")
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Salvar"):
                    df_contas.at[i, "Conta"] = novo_nome
                    df_contas.at[i, "Saldo"] = novo_saldo
                    salvar_contas(df_contas)
                    st.success("Conta atualizada com sucesso!")
                    st.rerun()
            with col2:
                if st.form_submit_button("🗑 Excluir"):
                    df_contas = df_contas.drop(i)
                    df_contas.reset_index(drop=True, inplace=True)
                    salvar_contas(df_contas)
                    st.success("Conta excluída com sucesso!")
                    st.rerun()
