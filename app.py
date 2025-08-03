
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
            # st.experimental_rerun() removido por segurança
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
                # st.experimental_rerun() removido por segurança

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
                            # st.experimental_rerun() removido por segurança

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
                        # st.experimental_rerun() removido por segurança

    
    elif menu == "Contas Bancárias":
        st.header("🏦 Contas Bancárias")

        CSV_CONTAS = "contas.csv"

        def carregar_contas():
            if os.path.exists(CSV_CONTAS):
                return pd.read_csv(CSV_CONTAS)
            else:
                return pd.DataFrame(columns=["Nome", "Saldo"])

        def salvar_contas(df):
            df.to_csv(CSV_CONTAS, index=False)

        contas_df = carregar_contas()

        st.subheader("➕ Adicionar Nova Conta")
        with st.form("nova_conta"):
            nome_conta = st.text_input("Nome da Conta")
            saldo_inicial = st.number_input("Saldo Inicial", step=0.01, format="%.2f")
            adicionar = st.form_submit_button("Salvar Conta")
            if adicionar and nome_conta:
                nova = {"Nome": nome_conta, "Saldo": saldo_inicial}
                contas_df = pd.concat([contas_df, pd.DataFrame([nova])], ignore_index=True)
                salvar_contas(contas_df)
                st.success("Conta salva com sucesso!")
                # st.experimental_rerun() removido por segurança

        st.subheader("📋 Contas Cadastradas")
        if not contas_df.empty:
            for i in contas_df.index:
                with st.expander(f"{contas_df.at[i, 'Nome']} - R$ {contas_df.at[i, 'Saldo']}"):
                    novo_nome = st.text_input(f"Editar Nome - {i}", contas_df.at[i, "Nome"], key=f"nome_{i}")
                    novo_saldo = st.number_input(f"Editar Saldo - {i}", value=float(contas_df.at[i, "Saldo"]), step=0.01, format="%.2f", key=f"saldo_{i}")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💾 Salvar Alterações", key=f"salvar_conta_{i}"):
                            contas_df.at[i, "Nome"] = novo_nome
                            contas_df.at[i, "Saldo"] = novo_saldo
                            salvar_contas(contas_df)
                            st.success("Conta atualizada.")
                            # st.experimental_rerun() removido por segurança
                    with col2:
                        if st.button("🗑️ Excluir Conta", key=f"excluir_conta_{i}"):
                            contas_df = contas_df.drop(i).reset_index(drop=True)
                            salvar_contas(contas_df)
                            st.warning("Conta excluída.")
                            # st.experimental_rerun() removido por segurança

    else:
        st.info(f"A seção '{menu}' será implementada em breve.")

# Executar login ou app principal
if "logado" not in st.session_state:
    st.session_state["logado"] = False

if st.session_state["logado"]:
    main_app()
else:
    login_screen()
