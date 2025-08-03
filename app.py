
import streamlit as st
import pandas as pd
import os
from datetime import datetime, date

USUARIO_PADRAO = "admin"
SENHA_PADRAO = "balicar123"

st.set_page_config(page_title="Sistema BALICAR", layout="wide")

# Autenticação
if "logado" not in st.session_state:
    st.session_state["logado"] = False

if not st.session_state["logado"]:
    st.title("🔐 Login - BALICAR")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if usuario == USUARIO_PADRAO and senha == SENHA_PADRAO:
            st.session_state["logado"] = True
            st.experimental_rerun()
        else:
            st.error("Usuário ou senha incorretos")
    st.stop()

# Logo e título
st.image("logo.png", width=300)
st.title("📊 Sistema de Controle Financeiro BALICAR")

st.success("Login realizado com sucesso! A partir daqui, o restante do sistema será integrado.")
