
import streamlit as st
import pandas as pd
import os
from datetime import datetime, date

# Configuração inicial
st.set_page_config(page_title="Sistema BALICAR", layout="wide")
st.image("logo.png", width=300)

# Arquivos base
ARQ_LANCAMENTOS = "lancamentos.csv"
ARQ_AGENDA = "agenda.csv"
ARQ_USUARIOS = "usuarios.csv"

# Carregar dados
def carregar_lancamentos():
    if os.path.exists(ARQ_LANCAMENTOS):
        return pd.read_csv(ARQ_LANCAMENTOS, parse_dates=["Data"])
    return pd.DataFrame(columns=["Data", "Tipo", "Descrição", "Valor", "Categoria"])

def salvar_lancamentos(df):
    df.to_csv(ARQ_LANCAMENTOS, index=False)

def carregar_agenda():
    if os.path.exists(ARQ_AGENDA):
        return pd.read_csv(ARQ_AGENDA, parse_dates=["Data"])
    return pd.DataFrame(columns=["Data", "Tipo", "Descrição", "Valor"])

def salvar_agenda(df):
    df.to_csv(ARQ_AGENDA, index=False)

def autenticar(usuario, senha):
    if os.path.exists(ARQ_USUARIOS):
        usuarios_df = pd.read_csv(ARQ_USUARIOS)
        return any((usuarios_df["Usuario"] == usuario) & (usuarios_df["Senha"] == senha))
    return False

# Login
if "logado" not in st.session_state:
    st.session_state["logado"] = False

if not st.session_state["logado"]:
    with st.form("login"):
        st.subheader("🔐 Login")
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        if st.form_submit_button("Entrar"):
            if autenticar(usuario, senha):
                st.session_state["logado"] = True
                st.success("Login realizado com sucesso!")
                st.experimental_rerun()
            else:
                st.error("Usuário ou senha incorretos.")
    st.stop()

# Menu
aba = st.sidebar.radio("Menu", ["📥 Lançamentos", "📊 Relatórios", "🏦 Contas e Saldos", "📅 Agenda"])

# Lançamentos
if aba == "📥 Lançamentos":
    st.subheader("📥 Novo Lançamento")
    lanc_df = carregar_lancamentos()
    with st.form("form_lancamento"):
        col1, col2, col3 = st.columns(3)
        with col1:
            data = st.date_input("Data", value=date.today())
            tipo = st.selectbox("Tipo", ["Receita", "Despesa"])
        with col2:
            valor = st.number_input("Valor", min_value=0.0, step=0.01)
            categoria = st.text_input("Categoria")
        with col3:
            descricao = st.text_input("Descrição")
        if st.form_submit_button("Salvar"):
            novo = {"Data": pd.to_datetime(data), "Tipo": tipo, "Valor": valor, "Categoria": categoria, "Descrição": descricao}
            lanc_df = pd.concat([lanc_df, pd.DataFrame([novo])], ignore_index=True)
            salvar_lancamentos(lanc_df)
            st.success("Lançamento adicionado!")
            st.experimental_rerun()
    st.divider()
    st.subheader("📋 Todos os Lançamentos")
    for i, row in lanc_df.iterrows():
        with st.expander(f"{row['Data'].date()} - {row['Tipo']} - R$ {row['Valor']}"):
            with st.form(f"edit_{i}"):
                nova_data = st.date_input("Data", value=row["Data"].date(), key=f"data_{i}")
                novo_tipo = st.selectbox("Tipo", ["Receita", "Despesa"], index=["Receita", "Despesa"].index(row["Tipo"]), key=f"tipo_{i}")
                novo_valor = st.number_input("Valor", value=row["Valor"], key=f"valor_{i}")
                nova_cat = st.text_input("Categoria", value=row["Categoria"], key=f"cat_{i}")
                nova_desc = st.text_input("Descrição", value=row["Descrição"], key=f"desc_{i}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Salvar edição"):
                        lanc_df.at[i, "Data"] = pd.to_datetime(nova_data)
                        lanc_df.at[i, "Tipo"] = novo_tipo
                        lanc_df.at[i, "Valor"] = novo_valor
                        lanc_df.at[i, "Categoria"] = nova_cat
                        lanc_df.at[i, "Descrição"] = nova_desc
                        salvar_lancamentos(lanc_df)
                        st.success("Editado!")
                        st.experimental_rerun()
                with col2:
                    if st.form_submit_button("🗑 Excluir"):
                        lanc_df = lanc_df.drop(i)
                        lanc_df.reset_index(drop=True, inplace=True)
                        salvar_lancamentos(lanc_df)
                        st.success("Excluído!")
                        st.experimental_rerun()

# Relatórios
elif aba == "📊 Relatórios":
    st.subheader("📊 Relatórios de Lançamentos")
    lanc_df = carregar_lancamentos()
    if lanc_df.empty:
        st.info("Nenhum dado disponível.")
    else:
        mes = st.selectbox("Filtrar por mês", lanc_df["Data"].dt.strftime("%Y-%m").unique())
        filtrado = lanc_df[lanc_df["Data"].dt.strftime("%Y-%m") == mes]
        st.write("Resumo do mês:", mes)
        st.write(f"Total Receita: R$ {filtrado[filtrado['Tipo'] == 'Receita']['Valor'].sum():.2f}")
        st.write(f"Total Despesa: R$ {filtrado[filtrado['Tipo'] == 'Despesa']['Valor'].sum():.2f}")
        st.bar_chart(filtrado.groupby("Tipo")["Valor"].sum())

# Contas e Saldos
elif aba == "🏦 Contas e Saldos":
    st.subheader("🏦 Contas Bancárias e Saldos")
    if "contas" not in st.session_state:
        st.session_state["contas"] = {}
    with st.form("form_conta"):
        col1, col2 = st.columns(2)
        nome_conta = col1.text_input("Nome da Conta")
        saldo = col2.number_input("Saldo Inicial", step=0.01)
        if st.form_submit_button("Salvar Conta"):
            st.session_state["contas"][nome_conta] = saldo
            st.success("Conta salva com sucesso!")
    st.write("💰 Saldos:")
    total = 0
    for nome, valor in st.session_state["contas"].items():
        st.write(f"• {nome}: R$ {valor:.2f}")
        total += valor
    st.write(f"**Total em contas: R$ {total:.2f}**")

# Agenda
elif aba == "📅 Agenda":
    st.subheader("📅 Agenda de Tarefas e Contas Agendadas")
    agenda_df = carregar_agenda()
    with st.form("form_nova_agenda"):
        col1, col2 = st.columns(2)
        with col1:
            data = st.date_input("Data", value=date.today())
            tipo = st.selectbox("Tipo", ["Tarefa", "Conta a pagar", "Conta a receber"])
        with col2:
            descricao = st.text_input("Descrição")
            valor = st.number_input("Valor (opcional)", min_value=0.0, step=0.01)
        if st.form_submit_button("Salvar"):
            novo_item = {"Data": pd.to_datetime(data), "Tipo": tipo, "Descrição": descricao, "Valor": valor}
            agenda_df = pd.concat([agenda_df, pd.DataFrame([novo_item])], ignore_index=True)
            salvar_agenda(agenda_df)
            st.success("Item salvo na agenda!")
            st.experimental_rerun()

    hoje = pd.to_datetime(date.today())
    agenda_hoje = agenda_df[agenda_df["Data"].dt.date == hoje.date()]
    st.markdown("### 📌 Tarefas para Hoje")
    if not agenda_hoje.empty:
        st.dataframe(agenda_hoje.sort_values("Tipo"))
    else:
        st.info("Nenhuma tarefa para hoje.")

    st.markdown("### 📋 Lista Completa")
    agenda_df = agenda_df.sort_values("Data")
    for i, row in agenda_df.iterrows():
        with st.expander(f"{row['Data'].date()} - {row['Tipo']} - {row['Descrição']}"):
            with st.form(f"edit_agenda_{i}"):
                nova_data = st.date_input("Data", value=row["Data"].date(), key=f"adata_{i}")
                novo_tipo = st.selectbox("Tipo", ["Tarefa", "Conta a pagar", "Conta a receber"], index=["Tarefa", "Conta a pagar", "Conta a receber"].index(row["Tipo"]), key=f"atipo_{i}")
                nova_desc = st.text_input("Descrição", value=row["Descrição"], key=f"adesc_{i}")
                novo_valor = st.number_input("Valor", value=row["Valor"], key=f"avalor_{i}")
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Salvar edição"):
                        agenda_df.at[i, "Data"] = pd.to_datetime(nova_data)
                        agenda_df.at[i, "Tipo"] = novo_tipo
                        agenda_df.at[i, "Descrição"] = nova_desc
                        agenda_df.at[i, "Valor"] = novo_valor
                        salvar_agenda(agenda_df)
                        st.success("Editado com sucesso!")
                        st.experimental_rerun()
                with col2:
                    if st.form_submit_button("🗑 Excluir"):
                        agenda_df = agenda_df.drop(i)
                        agenda_df.reset_index(drop=True, inplace=True)
                        salvar_agenda(agenda_df)
                        st.success("Item excluído.")
                        st.experimental_rerun()
