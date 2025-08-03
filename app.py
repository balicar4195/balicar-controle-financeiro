
import streamlit as st
import pandas as pd
import os
from datetime import datetime, date

ARQUIVO_CSV = "lancamentos.csv"
ARQUIVO_CONTAS = "contas.csv"
ARQUIVO_AGENDA = "agenda.csv"
USUARIO_PADRAO = "admin"
SENHA_PADRAO = "123"

st.set_page_config(page_title="BALICAR - Sistema Financeiro", layout="wide")

def login():
    st.title("🔐 Login - BALICAR")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if usuario == USUARIO_PADRAO and senha == SENHA_PADRAO:
            st.session_state["autenticado"] = True
            st.rerun()
        else:
            st.error("Usuário ou senha incorretos")

def salvar_csv(df, nome_arquivo):
    df.to_csv(nome_arquivo, index=False)

def carregar_csv(nome_arquivo, colunas):
    if os.path.exists(nome_arquivo):
        return pd.read_csv(nome_arquivo)
    return pd.DataFrame(columns=colunas)

def main_app():
    st.title("💼 Sistema Financeiro - BALICAR")

    lancamentos = carregar_csv(ARQUIVO_CSV, ["Data", "Tipo", "Descrição", "Valor", "Categoria"])
    contas = carregar_csv(ARQUIVO_CONTAS, ["Conta", "Saldo"])
    agenda = carregar_csv(ARQUIVO_AGENDA, ["Data", "Tipo", "Descrição", "Valor"])

    menu = st.sidebar.radio("Menu", ["Lançamentos", "Contas", "Relatórios", "Agenda"])

    if menu == "Lançamentos":
        st.subheader("➕ Novo Lançamento")
        with st.form("form_lancamento"):
            col1, col2, col3 = st.columns(3)
            with col1:
                data = st.date_input("Data", value=date.today())
                tipo = st.selectbox("Tipo", ["Receita", "Despesa"])
            with col2:
                descricao = st.text_input("Descrição")
                valor = st.number_input("Valor", min_value=0.0, step=0.01)
            with col3:
                categoria = st.text_input("Categoria")

            salvar = st.form_submit_button("Salvar")

            if salvar and descricao:
                novo = {"Data": str(data), "Tipo": tipo, "Descrição": descricao, "Valor": valor, "Categoria": categoria}
                lancamentos = pd.concat([lancamentos, pd.DataFrame([novo])], ignore_index=True)
                salvar_csv(lancamentos, ARQUIVO_CSV)

                tipo_agenda = "Conta a pagar" if tipo == "Despesa" else "Conta a receber"
                novo_agenda = {"Data": str(data), "Tipo": tipo_agenda, "Descrição": descricao, "Valor": valor}
                agenda = pd.concat([agenda, pd.DataFrame([novo_agenda])], ignore_index=True)
                salvar_csv(agenda, ARQUIVO_AGENDA)

                st.success("Lançamento salvo com sucesso!")
                st.rerun()

        st.subheader("📋 Lançamentos")
        for i, row in lancamentos.iterrows():
            with st.expander(f"{row['Data']} - {row['Tipo']} - {row['Descrição']}"):
                with st.form(f"form_{i}"):
                    nova_data = st.date_input("Data", value=pd.to_datetime(row["Data"]), key=f"data_{i}")
                    novo_tipo = st.selectbox("Tipo", ["Receita", "Despesa"], index=["Receita", "Despesa"].index(row["Tipo"]), key=f"tipo_{i}")
                    nova_desc = st.text_input("Descrição", value=row["Descrição"], key=f"desc_{i}")
                    novo_valor = st.number_input("Valor", value=row["Valor"], min_value=0.0, step=0.01, key=f"valor_{i}")
                    nova_cat = st.text_input("Categoria", value=row["Categoria"], key=f"cat_{i}")

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Salvar edição"):
                            lancamentos.at[i, "Data"] = str(nova_data)
                            lancamentos.at[i, "Tipo"] = novo_tipo
                            lancamentos.at[i, "Descrição"] = nova_desc
                            lancamentos.at[i, "Valor"] = novo_valor
                            lancamentos.at[i, "Categoria"] = nova_cat
                            salvar_csv(lancamentos, ARQUIVO_CSV)
                            st.success("Editado com sucesso!")
                            st.rerun()
                    with col2:
                        if st.form_submit_button("🗑 Excluir"):
                            lancamentos = lancamentos.drop(i)
                            lancamentos.reset_index(drop=True, inplace=True)
                            salvar_csv(lancamentos, ARQUIVO_CSV)
                            st.success("Excluído com sucesso!")
                            st.rerun()

    elif menu == "Contas":
        st.subheader("🏦 Contas Bancárias")
        with st.form("form_conta"):
            conta = st.text_input("Nome da Conta")
            saldo = st.number_input("Saldo Inicial", step=0.01)
            if st.form_submit_button("Salvar") and conta:
                contas = contas.append({"Conta": conta, "Saldo": saldo}, ignore_index=True)
                salvar_csv(contas, ARQUIVO_CONTAS)
                st.success("Conta salva com sucesso!")
                st.rerun()

        st.dataframe(contas)

    elif menu == "Relatórios":
        st.subheader("📊 Relatórios Financeiros")
        total_receitas = lancamentos[lancamentos["Tipo"] == "Receita"]["Valor"].sum()
        total_despesas = lancamentos[lancamentos["Tipo"] == "Despesa"]["Valor"].sum()
        saldo_total = contas["Saldo"].sum() + total_receitas - total_despesas

        st.metric("Saldo Total", f"R$ {saldo_total:,.2f}")
        st.metric("Total de Receitas", f"R$ {total_receitas:,.2f}")
        st.metric("Total de Despesas", f"R$ {total_despesas:,.2f}")

    elif menu == "Agenda":
        st.subheader("📅 Agenda de Tarefas e Contas Agendadas")
        with st.form("form_agenda"):
            col1, col2 = st.columns(2)
            with col1:
                data = st.date_input("Data", value=date.today(), key="agenda_data")
                tipo = st.selectbox("Tipo", ["Tarefa", "Conta a pagar", "Conta a receber"], key="agenda_tipo")
            with col2:
                descricao = st.text_input("Descrição", key="agenda_desc")
                valor = st.number_input("Valor (opcional)", min_value=0.0, step=0.01, key="agenda_valor")

            if st.form_submit_button("Salvar"):
                novo_item = {"Data": str(data), "Tipo": tipo, "Descrição": descricao, "Valor": valor}
                agenda = pd.concat([agenda, pd.DataFrame([novo_item])], ignore_index=True)
                salvar_csv(agenda, ARQUIVO_AGENDA)
                st.success("Item salvo na agenda!")
                st.rerun()

        st.write("📌 Tarefas para Hoje")
        hoje = pd.to_datetime(date.today())
        agenda["Data"] = pd.to_datetime(agenda["Data"])
        hoje_df = agenda[agenda["Data"].dt.date == hoje.date()]
        if not hoje_df.empty:
            st.dataframe(hoje_df.sort_values("Tipo"))
        else:
            st.info("Nenhuma tarefa agendada para hoje.")

        st.subheader("📋 Lista Completa de Tarefas e Contas")
        agenda = agenda.sort_values("Data")
        for i, row in agenda.iterrows():
            with st.expander(f"{row['Data'].date()} - {row['Tipo']} - {row['Descrição']}"):
                with st.form(f"form_agenda_{i}"):
                    nova_data = st.date_input("Data", value=row["Data"].date(), key=f"a_data_{i}")
                    novo_tipo = st.selectbox("Tipo", ["Tarefa", "Conta a pagar", "Conta a receber"], index=["Tarefa", "Conta a pagar", "Conta a receber"].index(row["Tipo"]), key=f"a_tipo_{i}")
                    nova_desc = st.text_input("Descrição", value=row["Descrição"], key=f"a_desc_{i}")
                    novo_valor = st.number_input("Valor", value=row["Valor"], min_value=0.0, step=0.01, key=f"a_valor_{i}")

                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("Salvar edição"):
                            agenda.at[i, "Data"] = pd.to_datetime(nova_data)
                            agenda.at[i, "Tipo"] = novo_tipo
                            agenda.at[i, "Descrição"] = nova_desc
                            agenda.at[i, "Valor"] = novo_valor
                            salvar_csv(agenda, ARQUIVO_AGENDA)
                            st.success("Editado com sucesso!")
                            st.rerun()
                    with col2:
                        if st.form_submit_button("🗑 Excluir"):
                            agenda = agenda.drop(i)
                            agenda.reset_index(drop=True, inplace=True)
                            salvar_csv(agenda, ARQUIVO_AGENDA)
                            st.success("Excluído com sucesso!")
                            st.rerun()

if "autenticado" not in st.session_state:
    login()
else:
    main_app()
