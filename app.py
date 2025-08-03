import streamlit as st
import pandas as pd
import os
from datetime import datetime, date
from login import autenticar_usuario

st.set_page_config(page_title="Controle Financeiro BALICAR", layout="wide")

if "autenticado" not in st.session_state:
    autenticar_usuario()
    st.stop()

st.title("💼 BALICAR - Sistema de Controle Financeiro")

st.sidebar.success("Login realizado com sucesso!")

st.markdown("Este é um sistema básico em desenvolvimento. Mais funcionalidades serão integradas.")