
import streamlit as st
import pandas as pd
import os
from datetime import datetime, date

# Configuração da página
st.set_page_config(page_title="BALICAR - Controle Financeiro", layout="wide")
st.title("📊 Sistema Financeiro BALICAR")

# Autenticação simples
def autenticar():
    st.sidebar.title("🔐 Login")
    user = st.sidebar.text_input("Usuário")
    password = st.sidebar.text_input("Senha", type="password")
    if st.sidebar.button("Entrar"):
        if user == "admin" and password == "balicar123":
            st.session_state["autenticado"] = True
            st.rerun()
        else:
            st.sidebar.error("Usuário ou senha incorretos.")

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    autenticar()
    st.stop()

# Caminho dos arquivos CSV
ARQUIVO_LANCAMENTOS = "lancamentos.csv"
ARQUIVO_CONTAS = "contas.csv"
ARQUIVO_AGENDA = "agenda.csv"

# Funções auxiliares
def carregar_dados(caminho, colunas):
    if os.path.exists(caminho):
        return pd.read_csv(caminho)
    return pd.DataFrame(columns=colunas)

def salvar_csv(df, caminho):
    df.to_csv(caminho, index=False)

# Carregar dados
dados = carregar_dados(ARQUIVO_LANCAMENTOS, ["Data", "Tipo", "Categoria", "Descrição", "Valor"])
contas = carregar_dados(ARQUIVO_CONTAS, ["Nome", "Saldo"])
agenda = carregar_dados(ARQUIVO_AGENDA, ["Data", "Tipo", "Descrição", "Valor"])

# Menu lateral
menu = st.sidebar.radio("Navegação", ["Lançamentos", "Contas", "Agenda", "Relatórios"])

# Lançamentos
if menu == "Lançamentos":
    st.subheader("💸 Novo Lançamento")
    with st.form("form_lancamento"):
        col1, col2 = st.columns(2)
        with col1:
            data = st.date_input("Data", value=date.today())
            tipo = st.selectbox("Tipo", ["Receita", "Despesa"])
            categoria = st.text_input("Categoria")
        with col2:
            descricao = st.text_input("Descrição")
            valor = st.number_input("Valor", min_value=0.0, step=0.01)

        if st.form_submit_button("Salvar"):
            novo = {
                "Data": data.strftime("%Y-%m-%d"),
                "Tipo": tipo,
                "Categoria": categoria,
                "Descrição": descricao,
                "Valor": valor
            }
            dados = pd.concat([dados, pd.DataFrame([novo])], ignore_index=True)
            salvar_csv(dados, ARQUIVO_LANCAMENTOS)
            st.success("Lançamento salvo com sucesso!")
            st.rerun()

    st.subheader("📋 Lançamentos Registrados")
    for i, row in dados.iterrows():
        with st.expander(f"{row['Data']} - {row['Tipo']} - {row['Descrição']}"):
            with st.form(f"editar_apagar_{i}"):
                nova_data = st.date_input("Data", value=pd.to_datetime(row["Data"]), key=f"data_{i}")
                novo_tipo = st.selectbox("Tipo", ["Receita", "Despesa"], index=["Receita", "Despesa"].index(row["Tipo"]), key=f"tipo_{i}")
                nova_categoria = st.text_input("Categoria", value=row["Categoria"], key=f"cat_{i}")
                nova_desc = st.text_input("Descrição", value=row["Descrição"], key=f"desc_{i}")
                novo_valor = st.number_input("Valor", value=row["Valor"], min_value=0.0, step=0.01, key=f"valor_{i}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Salvar edição"):
                        dados.at[i, "Data"] = nova_data.strftime("%Y-%m-%d")
                        dados.at[i, "Tipo"] = novo_tipo
                        dados.at[i, "Categoria"] = nova_categoria
                        dados.at[i, "Descrição"] = nova_desc
                        dados.at[i, "Valor"] = novo_valor
                        salvar_csv(dados, ARQUIVO_LANCAMENTOS)
                        st.success("Lançamento editado com sucesso!")
                        st.rerun()
                with col2:
                    if st.form_submit_button("🗑 Excluir"):
                        dados = dados.drop(i)
                        dados.reset_index(drop=True, inplace=True)
                        salvar_csv(dados, ARQUIVO_LANCAMENTOS)
                        st.success("Lançamento excluído!")
                        st.rerun()

# Contas
elif menu == "Contas":
    st.subheader("🏦 Contas Bancárias")
    with st.form("form_conta"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome da Conta")
        with col2:
            saldo = st.number_input("Saldo Atual", min_value=0.0, step=0.01)

        if st.form_submit_button("Adicionar Conta"):
            nova = {"Nome": nome, "Saldo": saldo}
            contas = pd.concat([contas, pd.DataFrame([nova])], ignore_index=True)
            salvar_csv(contas, ARQUIVO_CONTAS)
            st.success("Conta adicionada com sucesso!")
            st.rerun()

    st.subheader("📋 Lista de Contas")
    for i, row in contas.iterrows():
        with st.expander(f"{row['Nome']} - R$ {row['Saldo']:.2f}"):
            with st.form(f"editar_conta_{i}"):
                novo_nome = st.text_input("Nome", value=row["Nome"], key=f"nome_{i}")
                novo_saldo = st.number_input("Saldo", value=row["Saldo"], min_value=0.0, step=0.01, key=f"saldo_{i}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Salvar"):
                        contas.at[i, "Nome"] = novo_nome
                        contas.at[i, "Saldo"] = novo_saldo
                        salvar_csv(contas, ARQUIVO_CONTAS)
                        st.success("Conta atualizada com sucesso!")
                        st.rerun()
                with col2:
                    if st.form_submit_button("🗑 Excluir"):
                        contas = contas.drop(i)
                        contas.reset_index(drop=True, inplace=True)
                        salvar_csv(contas, ARQUIVO_CONTAS)
                        st.success("Conta excluída com sucesso!")
                        st.rerun()

# Agenda
elif menu == "Agenda":
    st.subheader("📅 Nova Tarefa ou Conta Agendada")
    with st.form("form_agenda"):
        col1, col2 = st.columns(2)
        with col1:
            data_agenda = st.date_input("Data", value=date.today())
            tipo_agenda = st.selectbox("Tipo", ["Tarefa", "Conta a pagar", "Conta a receber"])
        with col2:
            descricao_agenda = st.text_input("Descrição")
            valor_agenda = st.number_input("Valor", min_value=0.0, step=0.01)

        if st.form_submit_button("Salvar"):
            nova = {
                "Data": data_agenda.strftime("%Y-%m-%d"),
                "Tipo": tipo_agenda,
                "Descrição": descricao_agenda,
                "Valor": valor_agenda
            }
            agenda = pd.concat([agenda, pd.DataFrame([nova])], ignore_index=True)
            salvar_csv(agenda, ARQUIVO_AGENDA)
            st.success("Tarefa adicionada com sucesso!")
            st.rerun()

    st.subheader("📌 Tarefas para Hoje")
    hoje = date.today().strftime("%Y-%m-%d")
    agenda_hoje = agenda[agenda["Data"] == hoje]
    if not agenda_hoje.empty:
        st.dataframe(agenda_hoje)
    else:
        st.info("Nenhuma tarefa para hoje.")

    st.subheader("📋 Todas as Tarefas e Contas")
    for i, row in agenda.iterrows():
        with st.expander(f"{row['Data']} - {row['Tipo']} - {row['Descrição']}"):
            with st.form(f"editar_agenda_{i}"):
                nova_data = st.date_input("Data", value=pd.to_datetime(row["Data"]), key=f"adata_{i}")
                novo_tipo = st.selectbox("Tipo", ["Tarefa", "Conta a pagar", "Conta a receber"], index=["Tarefa", "Conta a pagar", "Conta a receber"].index(row["Tipo"]), key=f"atipo_{i}")
                nova_desc = st.text_input("Descrição", value=row["Descrição"], key=f"adesc_{i}")
                novo_valor = st.number_input("Valor", value=row["Valor"], min_value=0.0, step=0.01, key=f"avalor_{i}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("Salvar"):
                        agenda.at[i, "Data"] = nova_data.strftime("%Y-%m-%d")
                        agenda.at[i, "Tipo"] = novo_tipo
                        agenda.at[i, "Descrição"] = nova_desc
                        agenda.at[i, "Valor"] = novo_valor
                        salvar_csv(agenda, ARQUIVO_AGENDA)
                        st.success("Tarefa atualizada com sucesso!")
                        st.rerun()
                with col2:
                    if st.form_submit_button("🗑 Excluir"):
                        agenda = agenda.drop(i)
                        agenda.reset_index(drop=True, inplace=True)
                        salvar_csv(agenda, ARQUIVO_AGENDA)
                        st.success("Tarefa excluída!")
                        st.rerun()

# Relatórios
elif menu == "Relatórios":
    st.subheader("📈 Relatório Financeiro")
    if dados.empty:
        st.warning("Nenhum dado disponível.")
    else:
        receitas = dados[dados["Tipo"] == "Receita"]["Valor"].sum()
        despesas = dados[dados["Tipo"] == "Despesa"]["Valor"].sum()
        saldo = receitas - despesas

        st.metric("Total de Receitas", f"R$ {receitas:.2f}")
        st.metric("Total de Despesas", f"R$ {despesas:.2f}")
        st.metric("Saldo Final", f"R$ {saldo:.2f}")
