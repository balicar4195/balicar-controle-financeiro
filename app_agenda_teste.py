
import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="BALICAR - Teste Agenda", layout="wide")

CSV_AGENDA = "agenda.csv"

def check_login(username, password):
    return username == "admin" and password == "1234"

def carregar_agenda():
    if os.path.exists(CSV_AGENDA):
        return pd.read_csv(CSV_AGENDA)
    else:
        return pd.DataFrame(columns=["Data", "Tipo", "Descrição", "Valor", "Status"])

def salvar_agenda(df):
    df.to_csv(CSV_AGENDA, index=False)

def login_screen():
    st.title("Login - BALICAR (Teste Agenda)")
    user = st.text_input("Usuário")
    passwd = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if check_login(user, passwd):
            st.session_state["logado"] = True
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha incorretos.")

def main_app():
    menu = st.sidebar.radio("Menu", ["Agenda"])
    st.title("BALICAR - Teste de Agenda")

    if menu == "Agenda":
        st.header("📅 Agenda de Tarefas e Contas Agendadas")
        agenda_df = carregar_agenda()

        st.subheader("➕ Nova Tarefa ou Conta Agendada")
        with st.form("nova_tarefa"):
            data_agenda = st.date_input("Data")
            tipo_agenda = st.selectbox("Tipo", ["Conta a pagar", "Tarefa", "Outro"])
            descricao = st.text_input("Descrição")
            valor = st.number_input("Valor (opcional)", step=0.01, format="%.2f")
            status = st.selectbox("Status", ["Pendente", "Concluído"])
            adicionar_tarefa = st.form_submit_button("Salvar Tarefa")
            if adicionar_tarefa and descricao:
                nova = {"Data": str(data_agenda), "Tipo": tipo_agenda, "Descrição": descricao, "Valor": valor, "Status": status}
                agenda_df = pd.concat([agenda_df, pd.DataFrame([nova])], ignore_index=True)
                salvar_agenda(agenda_df)
                st.success("Tarefa agendada com sucesso!")

        st.subheader("📌 Tarefas do Dia")
        hoje = pd.to_datetime("today").date()
        tarefas_hoje = agenda_df[agenda_df["Data"] == str(hoje)]
        if not tarefas_hoje.empty:
            for i, row in tarefas_hoje.iterrows():
                st.markdown(f"**{row['Tipo']}** - {row['Descrição']} - R$ {row['Valor']} - *{row['Status']}*")
        else:
            st.info("Nenhuma tarefa para hoje.")

        st.subheader("📋 Todas as Tarefas e Contas Agendadas")
        if not agenda_df.empty:
            for i in agenda_df.index:
                with st.expander(f"{agenda_df.at[i, 'Data']} - {agenda_df.at[i, 'Descrição']}"):
                    nova_data = st.date_input(f"Data", pd.to_datetime(agenda_df.at[i, "Data"]), key=f"d{i}")
                    novo_tipo = st.selectbox("Tipo", ["Conta a pagar", "Tarefa", "Outro"], index=["Conta a pagar", "Tarefa", "Outro"].index(agenda_df.at[i, "Tipo"]), key=f"t{i}")
                    nova_desc = st.text_input("Descrição", agenda_df.at[i, "Descrição"], key=f"desc{i}")
                    novo_valor = st.number_input("Valor", value=float(agenda_df.at[i, "Valor"]), step=0.01, format="%.2f", key=f"val{i}")
                    novo_status = st.selectbox("Status", ["Pendente", "Concluído"], index=["Pendente", "Concluído"].index(agenda_df.at[i, "Status"]), key=f"s{i}")
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💾 Salvar Alterações", key=f"salvar_agenda_{i}"):
                            agenda_df.at[i, "Data"] = str(nova_data)
                            agenda_df.at[i, "Tipo"] = novo_tipo
                            agenda_df.at[i, "Descrição"] = nova_desc
                            agenda_df.at[i, "Valor"] = novo_valor
                            agenda_df.at[i, "Status"] = novo_status
                            salvar_agenda(agenda_df)
                            st.success("Tarefa atualizada.")
                    with col2:
                        if st.button("🗑️ Excluir", key=f"excluir_agenda_{i}"):
                            agenda_df = agenda_df.drop(i).reset_index(drop=True)
                            salvar_agenda(agenda_df)
                            st.warning("Tarefa excluída.")

if "logado" not in st.session_state:
    st.session_state["logado"] = False

if st.session_state["logado"]:
    main_app()
else:
    login_screen()
