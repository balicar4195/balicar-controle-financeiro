
import streamlit as st
import pandas as pd
import os
from datetime import datetime, date

ARQUIVO_AGENDA = "agenda.csv"

st.set_page_config(page_title="Agenda BALICAR", layout="wide")
st.image("logo.png", width=300)
st.title("📅 Agenda de Tarefas e Contas Agendadas")

# Função para carregar dados
def carregar_agenda():
    if os.path.exists(ARQUIVO_AGENDA):
        return pd.read_csv(ARQUIVO_AGENDA, parse_dates=["Data"])
    return pd.DataFrame(columns=["Data", "Tipo", "Descrição", "Valor"])

# Função para salvar dados
def salvar_agenda(df):
    df.to_csv(ARQUIVO_AGENDA, index=False)

# Carregar dados
agenda_df = carregar_agenda()

# Formulário para nova tarefa/conta
st.subheader("➕ Nova Tarefa ou Conta Agendada")
with st.form("form_nova_agenda"):
    col1, col2 = st.columns(2)
    with col1:
        data = st.date_input("Data", value=date.today())
        tipo = st.selectbox("Tipo", ["Tarefa", "Conta a pagar", "Conta a receber"])
    with col2:
        descricao = st.text_input("Descrição")
        valor = st.number_input("Valor (opcional)", min_value=0.0, step=0.01)

    salvar = st.form_submit_button("Salvar")

    if salvar and descricao:
        novo_item = {"Data": pd.to_datetime(data), "Tipo": tipo, "Descrição": descricao, "Valor": valor}
        agenda_df = pd.concat([agenda_df, pd.DataFrame([novo_item])], ignore_index=True)
        salvar_agenda(agenda_df)
        st.success("Item adicionado com sucesso!")
        st.rerun()

# Corrigir datas inválidas e mostrar tarefas de hoje
agenda_df["Data"] = pd.to_datetime(agenda_df["Data"], errors="coerce")
st.subheader("📌 Tarefas para Hoje")
hoje = pd.to_datetime(date.today())
agenda_hoje = agenda_df[agenda_df["Data"].dt.date == hoje.date()]
if not agenda_hoje.empty:
    st.dataframe(agenda_hoje.sort_values("Tipo"))
else:
    st.info("Nenhuma tarefa agendada para hoje.")

# Mostrar lista completa com opção de editar e excluir
st.subheader("📋 Lista Completa de Tarefas e Contas")
agenda_df = agenda_df.sort_values("Data")
for i, row in agenda_df.iterrows():
    with st.expander(f"{row['Data'].date()} - {row['Tipo']} - {row['Descrição']}"):
        with st.form(f"form_editar_excluir_{i}"):
            nova_data = st.date_input("Data", value=row["Data"].date(), key=f"data_{i}")
            novo_tipo = st.selectbox("Tipo", ["Tarefa", "Conta a pagar", "Conta a receber"], index=["Tarefa", "Conta a pagar", "Conta a receber"].index(row["Tipo"]), key=f"tipo_{i}")
            nova_desc = st.text_input("Descrição", value=row["Descrição"], key=f"desc_{i}")
            novo_valor = st.number_input("Valor", value=row["Valor"], min_value=0.0, step=0.01, key=f"valor_{i}")

            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("Salvar edição", use_container_width=True):
                    agenda_df.at[i, "Data"] = pd.to_datetime(nova_data)
                    agenda_df.at[i, "Tipo"] = novo_tipo
                    agenda_df.at[i, "Descrição"] = nova_desc
                    agenda_df.at[i, "Valor"] = novo_valor
                    salvar_agenda(agenda_df)
                    st.success("Item editado com sucesso!")
                    st.rerun()
            with col2:
                if st.form_submit_button("🗑 Excluir", use_container_width=True):
                    agenda_df = agenda_df.drop(i)
                    agenda_df.reset_index(drop=True, inplace=True)
                    salvar_agenda(agenda_df)
                    st.success("Item excluído com sucesso!")
                    st.rerun()
