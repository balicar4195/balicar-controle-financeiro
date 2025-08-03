
import streamlit as st
import pandas as pd
import os
from datetime import datetime, date

# Login fixo
st.set_page_config(page_title="BALICAR - Sistema Financeiro", layout="wide")
if "logado" not in st.session_state:
    st.session_state["logado"] = False

def login():
    st.title("🔐 Login")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if usuario == "admin" and senha == "balicar4195":
            st.session_state["logado"] = True
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha incorretos.")

if not st.session_state["logado"]:
    login()
    st.stop()

# Arquivos
CSV_LANCAMENTOS = "lancamentos.csv"
CSV_CONTAS = "contas.csv"
CSV_AGENDA = "agenda.csv"

# Carregar dados
def carregar_dados():
    if os.path.exists(CSV_LANCAMENTOS):
        lanc = pd.read_csv(CSV_LANCAMENTOS, parse_dates=["Data"])
    else:
        lanc = pd.DataFrame(columns=["Data", "Tipo", "Categoria", "Descrição", "Valor"])
    if os.path.exists(CSV_CONTAS):
        contas = pd.read_csv(CSV_CONTAS)
    else:
        contas = pd.DataFrame(columns=["Conta", "Saldo"])
    if os.path.exists(CSV_AGENDA):
        agenda = pd.read_csv(CSV_AGENDA, parse_dates=["Data"])
    else:
        agenda = pd.DataFrame(columns=["Data", "Tipo", "Descrição", "Valor"])
    return lanc, contas, agenda

def salvar_csv(df, nome):
    df.to_csv(nome, index=False)

lancamentos, contas, agenda = carregar_dados()

st.sidebar.title("BALICAR - Menu")
opcao = st.sidebar.radio("Ir para", ["📥 Lançamentos", "💰 Contas", "📊 Relatórios", "📅 Agenda"])

if opcao == "📥 Lançamentos":
    st.title("📥 Lançamentos")
    with st.form("form_lancamento"):
        col1, col2, col3 = st.columns(3)
        with col1:
            data = st.date_input("Data", value=date.today())
            tipo = st.selectbox("Tipo", ["Receita", "Despesa"])
        with col2:
            categoria = st.text_input("Categoria")
            descricao = st.text_input("Descrição")
        with col3:
            valor = st.number_input("Valor", min_value=0.0, step=0.01)
        salvar = st.form_submit_button("Salvar")
        if salvar and descricao:
            novo = {"Data": pd.to_datetime(data), "Tipo": tipo, "Categoria": categoria, "Descrição": descricao, "Valor": valor}
            lancamentos = pd.concat([lancamentos, pd.DataFrame([novo])], ignore_index=True)
            salvar_csv(lancamentos, CSV_LANCAMENTOS)
            if tipo in ["Conta a pagar", "Conta a receber"]:
                agenda = pd.concat([agenda, pd.DataFrame([{"Data": data, "Tipo": tipo, "Descrição": descricao, "Valor": valor}])], ignore_index=True)
                salvar_csv(agenda, CSV_AGENDA)
            st.success("Lançamento salvo.")
            st.rerun()

    st.subheader("📋 Lista de Lançamentos")
    for i, row in lancamentos.sort_values("Data").iterrows():
        with st.expander(f"{row['Data'].date()} - {row['Tipo']} - {row['Descrição']}"):
            with st.form(f"edit_{i}"):
                nova_data = st.date_input("Data", value=row["Data"].date(), key=f"data_{i}")
                novo_tipo = st.selectbox("Tipo", ["Receita", "Despesa"], index=["Receita", "Despesa"].index(row["Tipo"]), key=f"tipo_{i}")
                nova_cat = st.text_input("Categoria", value=row["Categoria"], key=f"cat_{i}")
                nova_desc = st.text_input("Descrição", value=row["Descrição"], key=f"desc_{i}")
                novo_valor = st.number_input("Valor", value=row["Valor"], min_value=0.0, step=0.01, key=f"valor_{i}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Salvar edição", use_container_width=True):
                        lancamentos.at[i, "Data"] = pd.to_datetime(nova_data)
                        lancamentos.at[i, "Tipo"] = novo_tipo
                        lancamentos.at[i, "Categoria"] = nova_cat
                        lancamentos.at[i, "Descrição"] = nova_desc
                        lancamentos.at[i, "Valor"] = novo_valor
                        salvar_csv(lancamentos, CSV_LANCAMENTOS)
                        st.success("Alterado.")
                        st.rerun()
                with col2:
                    if st.form_submit_button("🗑 Excluir", use_container_width=True):
                        lancamentos = lancamentos.drop(i)
                        lancamentos.reset_index(drop=True, inplace=True)
                        salvar_csv(lancamentos, CSV_LANCAMENTOS)
                        st.success("Excluído.")
                        st.rerun()

elif opcao == "💰 Contas":
    st.title("💰 Contas Bancárias")
    with st.form("nova_conta"):
        nome = st.text_input("Nome da Conta")
        saldo = st.number_input("Saldo Manual", step=0.01)
        if st.form_submit_button("Salvar Conta"):
            nova = {"Conta": nome, "Saldo": saldo}
            contas = pd.concat([contas, pd.DataFrame([nova])], ignore_index=True)
            salvar_csv(contas, CSV_CONTAS)
            st.success("Conta adicionada.")
            st.rerun()
    st.dataframe(contas)

elif opcao == "📊 Relatórios":
    st.title("📊 Relatórios")
    receita = lancamentos[lancamentos["Tipo"] == "Receita"]["Valor"].sum()
    despesa = lancamentos[lancamentos["Tipo"] == "Despesa"]["Valor"].sum()
    saldo = receita - despesa
    saldo_contas = contas["Saldo"].sum()
    st.metric("Total em Contas", f"R$ {saldo_contas:,.2f}")
    st.metric("Receitas", f"R$ {receita:,.2f}")
    st.metric("Despesas", f"R$ {despesa:,.2f}")
    st.metric("Saldo Final", f"R$ {saldo_contas + saldo:,.2f}")

elif opcao == "📅 Agenda":
    st.title("📅 Agenda de Tarefas e Contas Agendadas")
    with st.form("nova_tarefa"):
        col1, col2 = st.columns(2)
        with col1:
            data = st.date_input("Data", value=date.today())
            tipo = st.selectbox("Tipo", ["Tarefa", "Conta a pagar", "Conta a receber"])
        with col2:
            descricao = st.text_input("Descrição")
            valor = st.number_input("Valor (opcional)", min_value=0.0, step=0.01)
        if st.form_submit_button("Salvar"):
            novo_item = {"Data": pd.to_datetime(data), "Tipo": tipo, "Descrição": descricao, "Valor": valor}
            agenda = pd.concat([agenda, pd.DataFrame([novo_item])], ignore_index=True)
            salvar_csv(agenda, CSV_AGENDA)
            st.success("Adicionado com sucesso!")
            st.rerun()

    st.subheader("📌 Tarefas para Hoje")
    hoje = pd.to_datetime(date.today())
    try:
        hoje_df = agenda[agenda["Data"].dt.date == hoje.date()]
        if not hoje_df.empty:
            st.dataframe(hoje_df)
        else:
            st.info("Nenhuma tarefa para hoje.")
    except Exception as e:
        st.warning("Erro ao processar datas na agenda.")

    st.subheader("📋 Todas as Tarefas")
    for i, row in agenda.sort_values("Data").iterrows():
        with st.expander(f"{row['Data'].date()} - {row['Tipo']} - {row['Descrição']}"):
            with st.form(f"agenda_{i}"):
                nova_data = st.date_input("Data", value=row["Data"].date(), key=f"data_{i}")
                novo_tipo = st.selectbox("Tipo", ["Tarefa", "Conta a pagar", "Conta a receber"], index=["Tarefa", "Conta a pagar", "Conta a receber"].index(row["Tipo"]), key=f"tipo_{i}")
                nova_desc = st.text_input("Descrição", value=row["Descrição"], key=f"desc_{i}")
                novo_valor = st.number_input("Valor", value=row["Valor"], min_value=0.0, step=0.01, key=f"valor_{i}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Salvar edição", use_container_width=True):
                        agenda.at[i, "Data"] = pd.to_datetime(nova_data)
                        agenda.at[i, "Tipo"] = novo_tipo
                        agenda.at[i, "Descrição"] = nova_desc
                        agenda.at[i, "Valor"] = novo_valor
                        salvar_csv(agenda, CSV_AGENDA)
                        st.success("Alterado.")
                        st.rerun()
                with col2:
                    if st.form_submit_button("🗑 Excluir", use_container_width=True):
                        agenda = agenda.drop(i)
                        agenda.reset_index(drop=True, inplace=True)
                        salvar_csv(agenda, CSV_AGENDA)
                        st.success("Excluído.")
                        st.rerun()
