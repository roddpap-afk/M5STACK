import os
import sys
import io
import requests
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.dates as mdates
import numpy as np
import pandas as pd
import pytz
from datetime import datetime
import streamlit as st

st.set_page_config(page_title="M5Stack Dash", layout="wide")
st.title("📊 Monitoramento M5Stack")

# --- FUNÇÃO DE REQUISIÇÃO PROTEGIDA COM CACHE ---
# Se o servidor do M5Stack falhar/bloquear, o Streamlit guarda a última resposta válida por até 5 minutos
@st.cache_data(ttl=300, show_spinner="Buscando dados no servidor IoT...")
def carregar_dados_iot():
    # Simulando um navegador limpo com headers completos para camuflar o robô da nuvem
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'
    }
    
    # Requisição do Histórico M
    req_m = requests.get(
        'https://m5stack.com', 
        headers=headers, 
        timeout=12
    )
    
    # Requisição dos Clicks
    req_c = requests.get(
        'https://m5stack.com', 
        headers=headers, 
        timeout=12
    )
    
    # Se retornar algum erro HTTP (ex: 403, 502), joga para o bloco de exceção
    req_m.raise_for_status()
    req_c.raise_for_status()
    
    return req_m.json(), req_c.json()

# Inicialização das variáveis estruturais do app
dados_carregados = False
M, C = None, None

try:
    M, C = carregar_dados_iot()
    dados_carregados = True
except Exception as e:
    st.error("⚠️ O servidor da nuvem foi temporariamente bloqueado ou não conseguiu conectar com a API da M5Stack.")
    st.warning("⚠️ Isso ocorre porque a M5Stack às vezes bloqueia conexões vindas de servidores da AWS (EUA).")
    st.info("💡 No seu computador (VS Code) funciona porque seu IP de internet residencial é aceito sem problemas.")
    
    # Botão explícito para forçar o celular a tentar novamente furar o bloqueio
    if st.button("🔄 Tentar Novamente (Forçar Recarregamento)"):
        st.cache_data.clear()
        st.rerun()

# --- EXECUÇÃO DO GRÁFICO CASO OS DADOS EXISTAM ---
if dados_carregados and M and C:
    
    # Executa o botão de atualizar limpando o cache
    if st.button("🔄 Atualizar Gráfico"):
        st.cache_data.clear()
        st.rerun()

    rows_m = M['data']['rows']
    del rows_m[-1]
    exit_status = 0

    date_format = '%Y-%m-%d %H:%M:%S'
    china_tz = pytz.timezone('Asia/Shanghai')
    sp_tz = pytz.timezone('America/Sao_Paulo')

    i_m = 0
    time_l_m = []
    val_l_m = []

    for k in rows_m:
        raw_updt = (rows_m[i_m])['updateTime']
        updt = datetime.strptime(raw_updt, date_format)
        updt_cn = china_tz.localize(updt)
        updt = updt_cn.astimezone(sp_tz)
        val_m = (rows_m[i_m])['value']
        time_m_f = updt.strftime("%d-%m:%H:%M")
        time_l_m.insert(0, time_m_f)
        val_l_m.insert(0, val_m)
        i_m = i_m + 1
    x_m = time_l_m
    y_m = val_l_m

    ### CLICKS ###
    rows_c = C['data']['rows']
    del rows_c[-1]

    i_c = 0
    time_l_c = []
    val_l_c = []
    last_c = "None"

    for k in rows_c:
        raw_updt_c = (rows_c[i_c])['updateTime']
        updt_c = datetime.strptime(raw_updt_c, date_format)
        updt_cn_c = china_tz.localize(updt_c)
        updt_c = updt_cn_c.astimezone(sp_tz)
        val_c = (rows_c[i_c])['value']
        time_c_f = updt_c.strftime("%d-%m:%H:%M")
        time_l_c.insert(0, time_c_f)
        val_l_c.insert(0, val_c)  
        if val_c > 0: 
            if exit_status == 0:
                last_c = time_c_f
                exit_status = 1
        i_c = i_c + 1
    x_c = time_l_c
    y_c = val_l_c

    # Construção do gráfico idêntico ao VS Code
    fig, ax1 = plt.subplots(figsize=(10, 5))
    plt.xticks(rotation=45, ha='right')

    ax1.plot(x_m, y_m)
    ax1.xaxis.set_major_locator(mdates.DayLocator(interval=25))
    ax2 = ax1.twinx()
    ax2.set_ylim()

    ax2.plot(x_m, y_c, 'o', color='r') 
    plt.grid(axis='y')

    for xy in zip(x_m, y_c):
        if xy == 1:
            ax2.annotate('(%s)' % xy, xy=xy, textcoords='data', rotation=45)

    props = dict(boxstyle='round', facecolor='azure', alpha=0.5)
    textstr = 'Ultimo acionamento ' + last_c

    ax1.text(0.05, 0.95, textstr, transform=ax1.transAxes, fontsize=10,
             verticalalignment='top', bbox=props)

    plt.autoscale()
    
    # Entrega o gráfico na tela mobile de forma segura
    st.pyplot(fig)
