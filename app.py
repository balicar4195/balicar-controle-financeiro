
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import hashlib
import os

st.set_page_config(page_title="BALICAR - Controle Financeiro", layout="wide")
st.image("logo.png", width=200)

# ------------------------
# Autenticação
# ------------------------
users = {
    "admin": hashlib.sha256("senha123".encode()).hexdigest()
}

def login():
    st.sidebar.title("🔒 Login")
    username = st.sidebar.text_input("Usuário")
    password = st.sidebar.text_input("Senha", type="password")
    if st.sidebar.button("Entrar"):
        if username in users and users[username] == hashlib.sha256(password.encode()).hexdigest():
            st.session_state['logged_in'] = True
            st.session_state['user'] = username
        else:
            st.sidebar.error("Usuário ou senha incorretos.")

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if not st.session_state['logged_in']:
    login()
    st.stop()

# ------------------------
# Arquivos de dados
# ------------------------
CSV_LANCAMENTOS = "dados_financeiros.csv"
CSV_CONTAS = "contas.csv"
CSV_TAREFAS = "tarefas.csv"

def carregar_csv(caminho, colunas, parse_data=None):
    if os.path.exists(caminho):
        return pd.read_csv(caminho, parse_dates=parse_data)
    else:
        return pd.DataFrame(columns=colunas)

def salvar_csv(df, caminho):
    df.to_csv(caminho, index=False)

# ------------------------
# Inicialização dos dados
# ------------------------
if "dados" not in st.session_state:
    st.session_state["dados"] = carregar_csv(CSV_LANCAMENTOS, ["Data", "Tipo", "Categoria", "Descrição", "Valor"], ["Data"])
if "contas" not in st.session_state:
    st.session_state["contas"] = carregar_csv(CSV_CONTAS, ["Conta", "Saldo"])
if "tarefas" not in st.session_state:
    st.session_state["tarefas"] = carregar_csv(CSV_TAREFAS, ["Data", "Tarefa", "Concluida"])

if "edit_index" not in st.session_state:
    st.session_state["edit_index"] = None
if "delete_index" not in st.session_state:
    st.session_state["delete_index"] = None

# ------------------------
# Menu lateral
# ------------------------
st.sidebar.success("Logado como: " + st.session_state['user'])
st.sidebar.title("📚 Menu")
menu = st.sidebar.radio("Navegar para:", ["Lançamentos", "Relatórios", "Agenda", "Contas"])


# ------------------------
# Aba: Lançamentos
# ------------------------
if menu == "Lançamentos":
    st.title("💰 Lançamentos Financeiros")

if st.session_state["delete_index"] is not None:
    st.session_state["dados"] = st.session_state["dados"].drop(st.session_state["delete_index"]).reset_index(drop=True)
    salvar_csv(st.session_state["dados"], CSV_LANCAMENTOS)
    st.success("Lançamento excluído com sucesso.")
    st.session_state["delete_index"] = None
salvar_csv(st.session_state["dados"], CSV_LANCAMENTOS)
st.success("Lançamento excluído com sucesso.")
        st.session_state["delete_index"] = None

    if st.session_state["edit_index"] is None:
        with st.form("form_lancamento"):
            col1, col2 = st.columns(2)
            with col1:
                tipo = st.selectbox("Tipo", ["Receita", "Despesa"])
                categoria = st.selectbox("Categoria", ["Venda", "Salário", "Investimento", "Aluguel", "Manutenção", "Outros"])
            with col2:
                data = st.date_input("Data", value=datetime.today())
                valor = st.number_input("Valor", min_value=0.0, step=0.01)
            descricao = st.text_input("Descrição")
            salvar = st.form_submit_button("Salvar")

            if salvar:
                novo = pd.DataFrame([[data, tipo, categoria, descricao, valor]],
                                    columns=["Data", "Tipo", "Categoria", "Descrição", "Valor"])
                st.session_state["dados"] = pd.concat([st.session_state["dados"], novo], ignore_index=True)
salvar_csv(st.session_state["dados"], CSV_LANCAMENTOS)
                    st.success("Lançamento adicionado com sucesso!")
    else:
        st.subheader("✏️ Editar Lançamento")
        dados = st.session_state["dados"]
        row = dados.loc[st.session_state["edit_index"]]
        with st.form("form_edicao"):
            col1, col2 = st.columns(2)
            with col1:
                tipo = st.selectbox("Tipo", ["Receita", "Despesa"], index=["Receita", "Despesa"].index(row["Tipo"]))
                categoria = st.selectbox("Categoria", ["Venda", "Salário", "Investimento", "Aluguel", "Manutenção", "Outros"],
                                        index=["Venda", "Salário", "Investimento", "Aluguel", "Manutenção", "Outros"].index(row["Categoria"]))
            with col2:
                data = st.date_input("Data", value=pd.to_datetime(row["Data"]))
                valor = st.number_input("Valor", value=float(row["Valor"]), min_value=0.0, step=0.01)
            descricao = st.text_input("Descrição", value=row["Descrição"])
            atualizar = st.form_submit_button("Atualizar")

            if atualizar:
                st.session_state["dados"].loc[st.session_state["edit_index"]] = [data, tipo, categoria, descricao, valor]
salvar_csv(st.session_state["dados"], CSV_LANCAMENTOS)
                    st.success("Lançamento atualizado com sucesso!")
                st.session_state["edit_index"] = None

    st.subheader("📄 Lista de Lançamentos")
    dados = st.session_state["dados"]
    for i in range(len(dados)):
        col1, col2, col3 = st.columns([6, 1, 1])
        col1.write(f"{dados.loc[i, 'Data']} | {dados.loc[i, 'Tipo']} | {dados.loc[i, 'Categoria']} | {dados.loc[i, 'Descrição']} | R$ {dados.loc[i, 'Valor']:.2f}")
        if col2.button("✏️", key=f"edit_{i}"):
            st.session_state["edit_index"] = i
        if col3.button("🗑️", key=f"del_{i}"):
            st.session_state["delete_index"] = i
        st.write("---")

# ------------------------
# Aba: Relatórios
# ------------------------
    st.title("📊 Relatórios Financeiros")

    dados = st.session_state["dados"]
    contas = st.session_state["contas"]
    if dados.empty:
        st.info("Nenhum dado disponível.")
    else:
        dados["Data"] = pd.to_datetime(dados["Data"])
        dados["AnoMes"] = dados["Data"].dt.to_period("M").astype(str)

        meses = sorted(dados["AnoMes"].unique())
        categorias = sorted(dados["Categoria"].unique())

        filtro_mes = st.selectbox("📅 Filtrar por Mês", ["Todos"] + meses)
        filtro_categoria = st.selectbox("📂 Filtrar por Categoria", ["Todas"] + categorias)

        dados_filtrados = dados.copy()
        if filtro_mes != "Todos":
            dados_filtrados = dados_filtrados[dados_filtrados["AnoMes"] == filtro_mes]
        if filtro_categoria != "Todas":
            dados_filtrados = dados_filtrados[dados_filtrados["Categoria"] == filtro_categoria]

        total_receitas = dados_filtrados[dados_filtrados["Tipo"] == "Receita"]["Valor"].sum()
        total_despesas = dados_filtrados[dados_filtrados["Tipo"] == "Despesa"]["Valor"].sum()
        saldo_lancamentos = total_receitas - total_despesas

        saldo_contas = contas["Saldo"].sum() if not contas.empty else 0
        saldo_total = saldo_contas + saldo_lancamentos

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Receitas", f"R$ {total_receitas:,.2f}")
        col2.metric("Despesas", f"R$ {total_despesas:,.2f}")
        col3.metric("Saldo (Lançamentos)", f"R$ {saldo_lancamentos:,.2f}")
        col4.metric("Saldo Total (Contas + Receitas)", f"R$ {saldo_total:,.2f}")

        st.subheader("📊 Gráfico por Mês")
        resumo = dados_filtrados.groupby(["AnoMes", "Tipo"])["Valor"].sum().unstack().fillna(0)
        if not resumo.empty:
            st.bar_chart(resumo)

        st.subheader("🥧 Despesas por Categoria")
        despesas = dados_filtrados[dados_filtrados["Tipo"] == "Despesa"]
        if not despesas.empty:
            categoria_data = despesas.groupby("Categoria")["Valor"].sum()
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots()
            ax.pie(categoria_data, labels=categoria_data.index, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            st.pyplot(fig)
        else:
            st.info("Nenhuma despesa para exibir no gráfico.")
elif menu == "Agenda":
    st.title("📅 Agenda: Contas Futuras e Tarefas")
    dados = st.session_state["dados"]
    hoje = pd.to_datetime(datetime.today().date())

    # CONTAS FUTURAS
    st.subheader("💸 Contas Agendadas (Receber/Pagar)")
    futuras = dados[pd.to_datetime(dados["Data"]) > hoje]
    vencem_hoje = dados[pd.to_datetime(dados["Data"]) == hoje]
    vencidas = dados[pd.to_datetime(dados["Data"]) < hoje]

    def mostrar_lista(df, titulo, cor):
        if df.empty:
            return
        st.markdown(f"### <span style='color:{cor}'>{titulo}</span>", unsafe_allow_html=True)
        for i in df.index:
            with st.expander(f"{df.loc[i, 'Tipo']} | {df.loc[i, 'Categoria']} | {df.loc[i, 'Descrição']} | {df.loc[i, 'Data'].strftime('%d/%m/%Y')} | R$ {df.loc[i, 'Valor']:.2f}"):
                if st.button(f"✔ Marcar como {df.loc[i, 'Tipo'].lower()}", key=f"marcar_{i}"):
                    lanc = df.loc[i]
                    st.session_state["dados"] = st.session_state["dados"].drop(i).reset_index(drop=True)
                    hoje_lanc = lanc.copy()
                    hoje_lanc["Data"] = hoje
                    st.session_state["dados"] = pd.concat([st.session_state["dados"], pd.DataFrame([hoje_lanc])], ignore_index=True)
salvar_csv(st.session_state["dados"], CSV_LANCAMENTOS)
                        st.success("Lançamento movido para hoje.")

    mostrar_lista(vencidas, "Atrasadas", "red")
    mostrar_lista(vencem_hoje, "Vencem Hoje", "orange")
    mostrar_lista(futuras, "Futuras", "green")

    # TAREFAS
    st.subheader("✅ Tarefas do Dia e Futuras")
    with st.form("form_tarefa"):
        col1, col2 = st.columns([3, 1])
        with col1:
            tarefa = st.text_input("Descrição da tarefa")
        with col2:
            data_tarefa = st.date_input("Data", value=hoje)
        adicionar_tarefa = st.form_submit_button("Adicionar")

        if adicionar_tarefa and tarefa:
            nova_tarefa = pd.DataFrame([[data_tarefa, tarefa, False]], columns=["Data", "Tarefa", "Concluida"])
            st.session_state["tarefas"] = pd.concat([st.session_state["tarefas"], nova_tarefa], ignore_index=True)
                salvar_csv(st.session_state["tarefas"], CSV_TAREFAS)
                st.success("Tarefa adicionada com sucesso!")

    tarefas_hoje = st.session_state["tarefas"][pd.to_datetime(st.session_state["tarefas"]["Data"]) == hoje]
    tarefas_futuras = st.session_state["tarefas"][pd.to_datetime(st.session_state["tarefas"]["Data"]) > hoje]

    def exibir_tarefas(lista, titulo):
        if lista.empty:
            return
        st.markdown(f"### {titulo}")
        for i in lista.index:
            concluida = st.checkbox(f"{lista.loc[i, 'Tarefa']} ({pd.to_datetime(lista.loc[i, 'Data']).strftime('%d/%m/%Y')})", value=lista.loc[i, 'Concluida'], key=f"check_{i}")
            if concluida != lista.loc[i, 'Concluida']:
                st.session_state["tarefas"].loc[i, "Concluida"] = concluida
                    salvar_csv(st.session_state["tarefas"], CSV_TAREFAS)

    exibir_tarefas(tarefas_hoje, "Tarefas do Dia")
    exibir_tarefas(tarefas_futuras, "Tarefas Futuras")

# ------------------------
# Aba: Contas
# ------------------------
elif menu == "Contas":
    st.title("🏦 Contas e Saldos")

    with st.form("form_conta"):
        col1, col2 = st.columns(2)
        with col1:
            nome_conta = st.text_input("Nome da Conta")
        with col2:
            saldo_inicial = st.number_input("Saldo Inicial", step=0.01, min_value=0.0)
        adicionar = st.form_submit_button("Adicionar Conta")

        if adicionar and nome_conta:
            nova = pd.DataFrame([[nome_conta, saldo_inicial]], columns=["Conta", "Saldo"])
            st.session_state["contas"] = pd.concat([st.session_state["contas"], nova], ignore_index=True)
                salvar_csv(st.session_state["contas"], CSV_CONTAS)
                st.success("Conta adicionada com sucesso!")

    st.subheader("💳 Contas Cadastradas")
    if not st.session_state["contas"].empty:

        st.subheader("✏️ Editar Saldo das Contas")
        for i in st.session_state["contas"].index:
                conta = st.session_state["contas"].loc[i, "Conta"]
                saldo = st.session_state["contas"].loc[i, "Saldo"]
                novo_saldo = st.number_input(f"Saldo de {conta}", value=saldo, key=f"saldo_{i}")
                if novo_saldo != saldo:
                        st.session_state["contas"].loc[i, "Saldo"] = novo_saldo
        salvar_csv(st.session_state["contas"], CSV_CONTAS)
        st.success("Saldos atualizados com sucesso!")

        st.dataframe(st.session_state["contas"], use_container_width=True)
    else:
        st.info("Nenhuma conta cadastrada.")
