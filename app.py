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

# Configuração da página para Mobile
st.set_page_config(page_title="M5Stack Dash", layout="tight")
st.title("📊 Monitoramento M5Stack")

# Botão de atualização manual na interface do celular
if st.button("🔄 Atualizar Dados"):
    st.rerun()

# --- SEU ALGORITMO ORIGINAL DE CAPTURA E TRATAMENTO ---

http_req_m = requests.get('https://m5stack.com', headers={'Content-Type': 'application/json'})
M = http_req_m.json()

http_req_click = requests.get('https://m5stack.com', headers={'Content-Type': 'application/json'})
C = http_req_click.json()

rows_m = M['data']['rows']
del rows_m[-1]
exit = 0

date_format = '%Y-%m-%d %H:%M:%S'
china_tz = pytz.timezone('Asia/Shanghai')
sp_tz = pytz.timezone('America/Sao_Paulo')

i_m = 0
time_l_m = []
val_l_m = []
last_c = "None"

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
        if exit == 0:
            last_c = time_c_f
            exit = 1
    i_c = i_c + 1

x_c = time_l_c
y_c = val_l_c

# --- SEU ALGORITMO ORIGINAL DE GRÁFICO (MATPLOTLIB) ---

fig, ax1 = plt.subplots(figsize=(10, 6)) # Ajustado levemente a proporção para telas móveis
plt.xticks(rotation=45, ha='right')

ax1.plot(x_m, y_m)
ax1.xaxis.set_major_locator(mdates.DayLocator(interval=25))
ax2 = ax1.twinx()
ax2.set_ylim([0, 4])

ax2.plot(x_m, y_c, 'o', color='r') 
plt.grid(axis='y')

for xy in zip(x_m, y_c):
    if xy[1] == 1:
        ax2.annotate('(%s)' % xy[0], xy=xy, textcoords='data', rotation=45)

# Caixa de texto com o último acionamento
props = dict(boxstyle='round', facecolor='azure', alpha=0.5)
textstr = 'Ultimo acionamento ' + last_c

ax1.text(0.05, 0.95, textstr, transform=ax1.transAxes, fontsize=10,
         verticalalignment='top', bbox=props)

plt.autoscale()

# --- EXIBIÇÃO NO STREAMLIT (CELULAR) ---
# Mostra o gráfico adaptando o tamanho dinamicamente para a tela do celular
st.pyplot(fig, clear_figure=True)
