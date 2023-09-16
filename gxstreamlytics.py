from core import *

# Para acessar o venv: .\venv\Scripts\activate
# Para abrir o Streamlytics: streamlit run gxstreamlytics.py

st.title("GX STREAMLYTICS")

# Abrir dataframes necessários
df_backtest = pd.read_csv('./Dados/backtest.csv')
df_real = pd.read_csv('./Dados/real.csv')

# Ler a lista de um arquivo .txt
with open('./Dados/methods_labels.txt', 'r') as f:
    methods_labels = [line if not line.isnumeric() else int(line) for line in f.read().splitlines()]

# Criar um seletor para os métodos
metodo_selecionado = st.selectbox('Selecione o método', methods_labels)

# Chamando a função para plotar os gráficos para o método selecionado
plot_curva_lucro_drawdown_max_underwater(df_real, df_backtest, metodo_selecionado)