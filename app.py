import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import requests

# Configuração da página para dispositivos móveis
st.set_page_config(page_title="Meu App de Gráficos", layout="centered")

st.title("📊 Monitor de Dados API")
st.write("Este aplicativo consulta uma API e atualiza o gráfico automaticamente.")

# Botão para atualizar a consulta manualmente
if st.button("🔄 Atualizar Dados"):
    st.toast("Buscando novos dados...")

# --- SIMULAÇÃO DA SUA CONSULTA DE API ---
# Substitua este bloco pela sua função real de consulta:
# response = requests.get("SUA_API_URL")
# dados = response.json()
@st.cache_data(ttl=60)  # Guarda o resultado por 60 segundos para economizar a API
def buscar_dados_api():
    # Simulando dados numéricos vindos de uma API externa
    eixo_x = np.arange(1, 11)
    eixo_y = np.random.randint(10, 100, size=10)
    return eixo_x, eixo_y

try:
    x, y = buscar_dados_api()

    # --- CRIAÇÃO DO GRÁFICO MATPLOTLIB ---
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot(x, y, marker='o', color='#1E88E5', linewidth=2, label='Métrica')
    
    # Customização para o visual mobile
    ax.set_title("Evolução dos Dados em Tempo Real", fontsize=12, pad=15)
    ax.set_xlabel("Tempo / Amostras", fontsize=10)
    ax.set_ylabel("Valores Indicados", fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend()
    
    plt.tight_layout()

    # --- EXIBIÇÃO NO STREAMLIT ---
    # O argumento use_container_width garante que o gráfico se ajuste à tela do celular
    st.pyplot(fig, use_container_width=True)

    # Exibição de métricas rápidas em cartões para o celular
    col1, col2 = st.columns(2)
    col1.metric(label="Último Valor", value=f"{y[-1]}")
    col2.metric(label="Média Atual", value=f"{y.mean():.1f}")

except Exception as e:
    st.error(f"Erro ao conectar com a API: {e}")
