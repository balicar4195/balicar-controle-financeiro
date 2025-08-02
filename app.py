
import streamlit as st
import pandas as pd
from datetime import datetime
from io import BytesIO

st.set_page_config(page_title="BALICAR - Controle Financeiro", layout="wide")

# Menu lateral
with st.sidebar:
    st.image("logo.png", width=200)
    st.title("BALICAR")
    menu = st.radio("Navegação", ["💼 Lançamentos", "📈 Gráficos", "📅 Agenda", "📄 Relatórios", "⚙️ Configurações"])

if "dados" not in st.session_state:
    st.session_state.dados = pd.DataFrame(columns=["Tipo", "Descrição", "Valor", "Data", "Categoria", "Status", "Conta"])

if "tarefas" not in st.session_state:
    st.session_state.tarefas = []

def exportar_para_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Lançamentos')
    return output.getvalue()

if menu == "💼 Lançamentos":
    st.title("📌 Lançamentos Financeiros")

    with st.expander("➕ Adicionar novo lançamento"):
        tipo = st.selectbox("Tipo", ["Receita", "Despesa"])
        descricao = st.text_input("Descrição")
        valor = st.number_input("Valor (R$)", step=0.01)
        data = st.date_input("Data", value=datetime.today())
        categoria = st.text_input("Categoria")
        status = st.selectbox("Status", ["Pendente", "Pago"])
        conta = st.text_input("Conta")

        if st.button("Salvar lançamento"):
            novo = {
                "Tipo": tipo,
                "Descrição": descricao,
                "Valor": valor,
                "Data": data.strftime('%Y-%m-%d'),
                "Categoria": categoria,
                "Status": status,
                "Conta": conta
            }
            st.session_state.dados = pd.concat([st.session_state.dados, pd.DataFrame([novo])], ignore_index=True)
            st.success("Lançamento adicionado com sucesso!")

    st.subheader("🔍 Lançamentos salvos")
    st.dataframe(st.session_state.dados, use_container_width=True)

    if st.download_button("⬇️ Exportar para Excel", data=exportar_para_excel(st.session_state.dados),
                          file_name="balicar_lancamentos.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"):
        st.success("Arquivo exportado com sucesso!")

elif menu == "📈 Gráficos":
    st.title("📊 Gráficos (em breve)")
    st.info("Aqui você verá gráficos de receitas, despesas e totais por categoria.")

elif menu == "📅 Agenda":
    st.title("🗓️ Agenda de Tarefas")
    nova_tarefa = st.text_input("Nova tarefa")
    data_tarefa = st.date_input("Data para a tarefa", value=datetime.today())

    if st.button("Adicionar tarefa"):
        st.session_state.tarefas.append({"tarefa": nova_tarefa, "data": data_tarefa})
        st.success("Tarefa agendada!")

    st.subheader("📋 Tarefas agendadas")
    for t in st.session_state.tarefas:
        st.write(f"📌 {t['data'].strftime('%d/%m/%Y')}: {t['tarefa']}")

elif menu == "📄 Relatórios":
    st.title("📄 Relatórios (em breve)")
    st.info("Aqui você poderá gerar relatórios por mês, categoria, status, etc.")

elif menu == "⚙️ Configurações":
    st.title("⚙️ Configurações (em breve)")
    st.info("Futuramente: login, senha, usuários, preferências do sistema.")
