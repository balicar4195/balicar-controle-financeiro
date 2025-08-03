
import streamlit as st
from PIL import Image
import pandas as pd
import os

st.set_page_config(page_title="BALICAR Financeiro", layout="wide")

CSV_LANCAMENTOS = "lancamentos.csv"

# Verifica login fixo
def check_login(username, password):
    return username == "admin" and password == "1234"

# Carrega os dados existentes
def carregar_dados():
    if os.path.exists(CSV_LANCAMENTOS):
        return pd.read_csv(CSV_LANCAMENTOS)
    else:
        return pd.DataFrame(columns=["Data", "Tipo", "Categoria", "Valor", "Forma de Pagamento", "Conta Bancária", "Observação"])

# Salva os dados no CSV
def salvar_csv(df):
    df.to_csv(CSV_LANCAMENTOS, index=False)

# Tela de login
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

# Tela principal
def main_app():
    logo = Image.open("logo.png")
    st.sidebar.image(logo, use_container_width=True)
    menu = st.sidebar.radio("Menu", ["Lançamentos", "Agenda", "Relatórios", "Gráficos", "Contas Bancárias"])

    st.title("Sistema de Controle Financeiro - BALICAR")

    if menu == "Lançamentos":
        st.header("📌 Lançamentos")

        df = carregar_dados()

        with st.form("form_lancamento"):
            col1, col2, col3 = st.columns(3)
            with col1:
                data = st.date_input("Data")
                tipo = st.selectbox("Tipo", ["Receita", "Despesa"])
                valor = st.number_input("Valor", step=0.01, format="%.2f")
            with col2:
                categoria = st.text_input("Categoria")
                forma_pagamento = st.selectbox("Forma de Pagamento", ["Dinheiro", "PIX", "Cartão", "Boleto", "Transferência"])
            with col3:
                conta = st.text_input("Conta Bancária")
                observacao = st.text_input("Observação")

            submit = st.form_submit_button("Salvar")
            if submit:
                novo = {
                    "Data": str(data),
                    "Tipo": tipo,
                    "Categoria": categoria,
                    "Valor": valor,
                    "Forma de Pagamento": forma_pagamento,
                    "Conta Bancária": conta,
                    "Observação": observacao
                }
                df = pd.concat([df, pd.DataFrame([novo])], ignore_index=True)
                salvar_csv(df)
                st.success("Lançamento salvo com sucesso!")
                st.experimental_rerun()

        st.subheader("📋 Lançamentos Salvos")

        if not df.empty:
            for i in df.index:
                with st.expander(f"{df.at[i, 'Data']} - {df.at[i, 'Categoria']} - R$ {df.at[i, 'Valor']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"Tipo: {df.at[i, 'Tipo']}")
                        st.write(f"Forma de Pagamento: {df.at[i, 'Forma de Pagamento']}")
                        st.write(f"Conta Bancária: {df.at[i, 'Conta Bancária']}")
                    with col2:
                        st.write(f"Observação: {df.at[i, 'Observação']}")
                        if st.button("✏️ Editar", key=f"editar_{i}"):
                            st.session_state["edit_index"] = i
                        if st.button("🗑️ Excluir", key=f"excluir_{i}"):
                            df = df.drop(i).reset_index(drop=True)
                            salvar_csv(df)
                            st.experimental_rerun()

            # Edição
            if "edit_index" in st.session_state:
                idx = st.session_state["edit_index"]
                st.subheader("✏️ Editar Lançamento")
                with st.form("form_editar"):
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        data = st.date_input("Data", pd.to_datetime(df.at[idx, "Data"]))
                        tipo = st.selectbox("Tipo", ["Receita", "Despesa"], index=["Receita", "Despesa"].index(df.at[idx, "Tipo"]))
                        valor = st.number_input("Valor", value=float(df.at[idx, "Valor"]), step=0.01, format="%.2f")
                    with col2:
                        categoria = st.text_input("Categoria", df.at[idx, "Categoria"])
                        forma_pagamento = st.selectbox("Forma de Pagamento", ["Dinheiro", "PIX", "Cartão", "Boleto", "Transferência"], 
                                                       index=["Dinheiro", "PIX", "Cartão", "Boleto", "Transferência"].index(df.at[idx, "Forma de Pagamento"]))
                    with col3:
                        conta = st.text_input("Conta Bancária", df.at[idx, "Conta Bancária"])
                        observacao = st.text_input("Observação", df.at[idx, "Observação"])
                    salvar = st.form_submit_button("Salvar Alterações")
                    if salvar:
                        df.at[idx, "Data"] = str(data)
                        df.at[idx, "Tipo"] = tipo
                        df.at[idx, "Categoria"] = categoria
                        df.at[idx, "Valor"] = valor
                        df.at[idx, "Forma de Pagamento"] = forma_pagamento
                        df.at[idx, "Conta Bancária"] = conta
                        df.at[idx, "Observação"] = observacao
                        salvar_csv(df)
                        del st.session_state["edit_index"]
                        st.success("Lançamento editado com sucesso!")
                        st.experimental_rerun()

    else:
        st.info(f"A seção '{menu}' será implementada em breve.")

# Executar login ou app principal
if "logado" not in st.session_state:
    st.session_state["logado"] = False

if st.session_state["logado"]:
    main_app()
else:
    login_screen()
