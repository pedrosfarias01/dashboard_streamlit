import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import numpy as np

# Função para plotar os gráficos
def plot_curva_lucro_drawdown_max_underwater(df_real, df_backtest, metodo):

    df_backtest['Date'] = pd.to_datetime(df_backtest['Date'])
    df_real['Date'] = pd.to_datetime(df_real['Date'])

    # Filtrar os dados do método específico
    df_real_metodo = df_real[(df_real['Método'] == metodo) & (df_real['Stake'] > 0)]

    # Definindo a data de início do método em questão
    data_inicio = df_real_metodo['Date'].min()

    # Filtrando o df_backtest
    df_backtest_metodo = df_backtest[(df_backtest['Método'] == metodo) & (df_backtest['Date'] < data_inicio)]

    # Concatenar os DataFrames de Backtest e Real
    df_concatenado = pd.concat([df_backtest_metodo, df_real_metodo])

    # Ordenar o DataFrame por data
    df_concatenado.sort_values(by='Date', inplace=True)

    # Criar um DataFrame de resumo agrupando por dia
    df_resumo = df_concatenado.groupby(df_concatenado['Date'].dt.date)['L/P'].sum().reset_index()
    df_resumo.columns = ['Date', 'L/P']

    # Definir a coluna 'Date' como índice
    df_resumo.set_index('Date', inplace=True)

    # Calcular o número de entradas por dia para as linhas filtradas
    df_resumo['Entradas'] = df_concatenado.groupby(df_concatenado['Date'].dt.date)['L/P'].count()

    # Adicionar a coluna 'Tipo' no df_resumo com base nas condições
    df_resumo['Tipo'] = np.where(df_resumo.index < pd.Timestamp(data_inicio).date(), 'Backtest', 'Real')

    # Calcular a coluna 'L/P Acu'
    df_resumo['L/P Acu'] = df_resumo['L/P'].cumsum()
    
    # Criando os gráficos com Plotly Express
    fig1 = px.line(df_resumo, x=df_resumo.index, y='L/P Acu', color='Tipo', 
                title=f'GX Method: {metodo}', labels={'L/P Acu':'Lucro Acumulado'}, 
                line_shape='linear', color_discrete_map={'Backtest':'blue', 'Real':'green'}, height=600, width=900)

    # Adicionando uma linha vertical vermelha na data de início
    fig1.add_vline(x=data_inicio, line_width=2, line_color="red")

    # Adicionando uma anotação para indicar o "Início da Validação Prática"
    fig1.add_annotation(
        x=data_inicio,
        y=df_resumo['L/P Acu'].min(),
        text= "Início da validação prática",
        showarrow=False,
        font=dict(
            family="Courier New, monospace",
            size=12,
            color="#ff0000"
        ),
    )

    # Calcular o drawdown
    df_resumo['Highwater'] = df_resumo['L/P Acu'].cummax()
    df_resumo['Drawdown'] = df_resumo['L/P Acu'] - df_resumo['Highwater']

    # Traçar o gráfico de drawdown
    fig2 = px.area(df_resumo, x=df_resumo.index, y='Drawdown',
                title='Gráfico de Drawdown', labels={'Drawdown':'Drawdown'}, 
                line_shape='linear', height=600, width=900)
    # Mudar a cor da área para vermelho
    fig2.update_traces(line_color='red', fillcolor='rgba(255,0,0,0.5)')

    # Calcular e exibir informações adicionais no início da tela, com uma fonte maior
    entradas_backtest = df_resumo[df_resumo['Tipo'] == 'Backtest']['Entradas'].sum()
    entradas_real = df_resumo[df_resumo['Tipo'] == 'Real']['Entradas'].sum()
    roi_backtest = df_resumo[df_resumo['Tipo'] == 'Backtest']['L/P'].sum() / entradas_backtest * 100
    roi_real = df_resumo[df_resumo['Tipo'] == 'Real']['L/P'].sum() / entradas_real * 100
    odd_media_real = round(df_real_metodo['Odd'].mean(), 2)

    st.markdown(f'### Entradas do Backtest: {entradas_backtest}')
    st.markdown(f'### Entradas Reais: {entradas_real}')
    st.markdown(f'### ROI do Backtest: {roi_backtest:.1f}%')
    st.markdown(f'### ROI Real: {roi_real:.1f}%')
    st.markdown(f'### Odd Média: {odd_media_real}')
    
    # Mostrando os gráficos no Streamlit
    st.plotly_chart(fig1)
    st.plotly_chart(fig2)

