
import streamlit as st
import pandas as pd
import datetime as dt
import plotly.express as px
import os

# Caminhos dos arquivos
CSV_LANCAMENTOS = "lancamentos.csv"
CSV_CONTAS = "contas.csv"
CSV_TAREFAS = "tarefas.csv"

# Funções de utilidade
def carregar_csv(caminho, colunas):
    if os.path.exists(caminho):
        return pd.read_csv(caminho)
    else:
        return pd.DataFrame(columns=colunas)

def salvar_csv(df, caminho):
    df.to_csv(caminho, index=False)

# Inicializar sessão
if "dados" not in st.session_state:
    st.session_state["dados"] = carregar_csv(CSV_LANCAMENTOS, ["Data", "Tipo", "Categoria", "Descrição", "Valor", "Conta"])
if "contas" not in st.session_state:
    st.session_state["contas"] = carregar_csv(CSV_CONTAS, ["Conta", "Saldo"])
if "tarefas" not in st.session_state:
    st.session_state["tarefas"] = carregar_csv(CSV_TAREFAS, ["Tarefa", "Data", "Concluida"])

# Layout principal
st.set_page_config(page_title="Controle Financeiro BALICAR", layout="wide")

with st.sidebar:
    st.title("📊 BALICAR Financeiro")
    pagina = st.radio("Menu", ["Lançamentos", "Contas Bancárias", "Relatórios", "Agenda de Tarefas", "Configurações"])

# PÁGINAS
if pagina == "Lançamentos":
    st.header("💰 Lançamentos")
    with st.form("form_lancamento"):
        col1, col2 = st.columns(2)
        with col1:
            data = st.date_input("Data", value=dt.date.today())
            tipo = st.selectbox("Tipo", ["Receita", "Despesa"])
            categoria = st.text_input("Categoria")
        with col2:
            descricao = st.text_input("Descrição")
            valor = st.number_input("Valor", step=0.01)
            conta = st.selectbox("Conta", st.session_state["contas"]["Conta"] if not st.session_state["contas"].empty else [])
        salvar = st.form_submit_button("Adicionar")
        if salvar and categoria and descricao:
            novo = pd.DataFrame([[data, tipo, categoria, descricao, valor, conta]], columns=st.session_state["dados"].columns)
            st.session_state["dados"] = pd.concat([st.session_state["dados"], novo], ignore_index=True)
            salvar_csv(st.session_state["dados"], CSV_LANCAMENTOS)
            st.success("Lançamento adicionado com sucesso!")

    st.subheader("📄 Todos os Lançamentos")
    filtro_data = st.date_input("Filtrar por data", [])
    if filtro_data:
        df_filtrado = st.session_state["dados"][st.session_state["dados"]["Data"].isin([str(d) for d in filtro_data])]
    else:
        df_filtrado = st.session_state["dados"]

    st.dataframe(df_filtrado)

elif pagina == "Contas Bancárias":
    st.header("🏦 Contas Bancárias")
    with st.form("form_contas"):
        col1, col2 = st.columns(2)
        with col1:
            conta = st.text_input("Nome da Conta")
        with col2:
            saldo = st.number_input("Saldo Inicial", step=0.01)
        add_conta = st.form_submit_button("Adicionar Conta")
        if add_conta and conta:
            nova = pd.DataFrame([[conta, saldo]], columns=st.session_state["contas"].columns)
            st.session_state["contas"] = pd.concat([st.session_state["contas"], nova], ignore_index=True)
            salvar_csv(st.session_state["contas"], CSV_CONTAS)
            st.success("Conta adicionada com sucesso!")

    st.subheader("✏️ Editar Saldo das Contas")
    for i in st.session_state["contas"].index:
        nome = st.session_state["contas"].loc[i, "Conta"]
        saldo_atual = st.session_state["contas"].loc[i, "Saldo"]
        novo_saldo = st.number_input(f"Saldo da conta {nome}", value=saldo_atual, key=f"saldo_{i}")
        if novo_saldo != saldo_atual:
            st.session_state["contas"].loc[i, "Saldo"] = novo_saldo
    salvar_csv(st.session_state["contas"], CSV_CONTAS)

    st.dataframe(st.session_state["contas"])

elif pagina == "Relatórios":
    st.header("📈 Relatórios")
    df = st.session_state["dados"]
    if not df.empty:
        df["Data"] = pd.to_datetime(df["Data"])
        df["Mês"] = df["Data"].dt.to_period("M")

        st.subheader("Gráfico por Mês")
        barras = df.groupby(["Mês", "Tipo"])["Valor"].sum().reset_index()
        fig_barra = px.bar(barras, x="Mês", y="Valor", color="Tipo", barmode="group")
        st.plotly_chart(fig_barra)

        st.subheader("Gráfico por Categoria")
        pizza = df.groupby("Categoria")["Valor"].sum().reset_index()
        fig_pizza = px.pie(pizza, names="Categoria", values="Valor")
        st.plotly_chart(fig_pizza)

        st.subheader("Visão Geral")
        receita = df[df["Tipo"] == "Receita"]["Valor"].sum()
        despesa = df[df["Tipo"] == "Despesa"]["Valor"].sum()
        saldo_total = receita - despesa + st.session_state["contas"]["Saldo"].sum()
        st.metric("💵 Saldo Geral", f"R$ {saldo_total:,.2f}")

elif pagina == "Agenda de Tarefas":
    st.header("📅 Agenda de Tarefas")
    with st.form("form_tarefa"):
        col1, col2 = st.columns(2)
        with col1:
            tarefa = st.text_input("Tarefa")
        with col2:
            data_tarefa = st.date_input("Data da tarefa", dt.date.today())
        add_tarefa = st.form_submit_button("Adicionar")
        if add_tarefa and tarefa:
            nova = pd.DataFrame([[tarefa, data_tarefa, False]], columns=st.session_state["tarefas"].columns)
            st.session_state["tarefas"] = pd.concat([st.session_state["tarefas"], nova], ignore_index=True)
            salvar_csv(st.session_state["tarefas"], CSV_TAREFAS)
            st.success("Tarefa adicionada!")

    st.subheader("📋 Tarefas Futuras")
    for i in st.session_state["tarefas"].index:
        nome = st.session_state["tarefas"].loc[i, "Tarefa"]
        data = st.session_state["tarefas"].loc[i, "Data"]
        feita = st.session_state["tarefas"].loc[i, "Concluida"]
        marcado = st.checkbox(f"{nome} ({data})", value=feita, key=f"tarefa_{i}")
        st.session_state["tarefas"].loc[i, "Concluida"] = marcado
    salvar_csv(st.session_state["tarefas"], CSV_TAREFAS)

elif pagina == "Configurações":
    st.header("⚙️ Configurações")
    if st.button("Exportar lançamentos para Excel"):
        st.download_button("📤 Baixar Excel", data=st.session_state["dados"].to_csv(index=False), file_name="lancamentos.csv", mime="text/csv")
