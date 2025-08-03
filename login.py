import streamlit as st

def autenticar_usuario():
    st.title("🔐 Sistema BALICAR - Login")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if usuario == "admin" and senha == "balicar4195":
            st.session_state["autenticado"] = True
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha incorretos.")