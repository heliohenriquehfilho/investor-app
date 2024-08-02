import pandas as pd
import numpy as np
import streamlit as st
import yfinance as yf
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats

st.write("Bem-Vindo Investidor!")

# Inicialize as variáveis de sessão se ainda não estiverem inicializadas
if 'stocks' not in st.session_state:
    st.session_state.stocks = {}
if 'tickers' not in st.session_state:
    st.session_state.tickers = []
if 'datas' not in st.session_state:
    st.session_state.datas = []
if 'df' not in st.session_state:
    st.session_state.df = None

def add_stock(ticker, data):
    if ticker and data:
        st.session_state.tickers.append(ticker)
        st.session_state.datas.append(data)
        st.session_state.stocks[ticker] = data
        st.write("Ativo adicionado com sucesso!")

# Captura de inputs
ticker = st.text_input("Ticker do ativo: ")
data = st.date_input("Data de compra", format="DD/MM/YYYY")

# Botão para adicionar o ativo
if st.button("Adicionar Ativo"):
    add_stock(ticker, data)

# Mostrar os dados armazenados
st.write("Ativos adicionados:")
st.write(st.session_state.stocks)

st.write("Tickers adicionados:")
st.write(st.session_state.tickers)

st.write("Datas de compra:")
st.write(st.session_state.datas)

def get_stock_data():
    data_frames = []
    for ticker, date in st.session_state.stocks.items():
        start_date = date.strftime("%Y-%m-%d")
        end_date = datetime.today().strftime("%Y-%m-%d")
        data = yf.download(ticker, start=start_date, end=end_date)
        data.reset_index(inplace=True)  # Reseta o índice para transformar as datas em uma coluna
        data['Ticker'] = ticker
        data_frames.append(data)
    
    if data_frames:
        result = pd.concat(data_frames)
        st.session_state.df = result  # Armazena o DataFrame no estado da sessão
        st.write(result)
        return result
    else:
        st.write("Nenhum dado encontrado.")
        return None

def gerar_grafico():
    if st.session_state.df is not None:
        # Criar o gráfico de dispersão
        figure = px.scatter(st.session_state.df, x='Date', y='Close', color='Ticker', hover_name='Ticker')
        
        # Adicionar linhas ao gráfico
        for ticker in st.session_state.df['Ticker'].unique():
            ticker_data = st.session_state.df[st.session_state.df['Ticker'] == ticker]
            figure.add_trace(go.Scatter(x=ticker_data['Date'], y=ticker_data['Close'], mode='lines', name=f'{ticker} Line'))
        
        st.write(figure)
    else:
        st.write("Nenhum dado disponível para gerar o gráfico.")

# Botão para obter dados das ações
if st.button("Obter Dados das Ações"):
    df = get_stock_data()

# Botão para obter gráficos
if st.button("Obter Gráficos"):
    gerar_grafico()


def monte_carlo_previsao(dataset, ativo, dias_a_frente, simulacoes):
  dataset = dataset[dataset['Ticker'] == ativo].set_index('Date')
  dataset = pd.DataFrame(dataset['Close'])

  dataset_normalizado = dataset.copy()
  for i in dataset:
    dataset_normalizado[i] = dataset[i] / dataset[i][0]

  dataset_taxa_retorno = np.log(1 + dataset_normalizado.pct_change())
  dataset_taxa_retorno.fillna(0, inplace=True)

  media = dataset_taxa_retorno.mean()
  variancia = dataset_taxa_retorno.var()

  drift = media - (0.5 * variancia)
  desvio_padrao = dataset_taxa_retorno.std()
  Z = stats.norm.ppf(np.random.rand(dias_a_frente, simulacoes))
  retornos_diarios = np.exp(drift.values + desvio_padrao.values * Z)

  previsoes = np.zeros_like(retornos_diarios)
  previsoes[0] = dataset.iloc[-1]

  for dia in range(1, dias_a_frente):
    previsoes[dia] = previsoes[dia - 1] * retornos_diarios[dia]

  figura = go.Figure()

  # Adicionar os dados históricos ao gráfico
  figura.add_trace(go.Scatter(x=dataset.index, y=dataset['Close'], mode='lines', name='Histórico'))


  # Adicionar as previsões ao gráfico
  for i in range(simulacoes):
    figura.add_trace(go.Scatter(
        x=pd.date_range(start=dataset.index[-1], periods=dias_a_frente, freq='D'),
        y=previsoes[:, i],
        mode='lines',
        name=f'Simulação {i + 1}',
        line=dict(width=1),
        opacity=0.5
    ))

  figura.update_layout(title=f'Previsões do preço das ações - {ativo}', xaxis_title='Data', yaxis_title='Preço')
  st.write(figura)

  retorno = previsoes.T[0] - previsoes.T[-1]
  #print(retorno)

  return previsoes.T

selected_ticker = st.selectbox('Selecione uma ação', st.session_state.tickers)

# Botão para obter gráficos montte carlo
if st.button("Obter Gráficos Monte Carlo"):
    monte_carlo_previsao(st.session_state.df, selected_ticker, 20, 10)

print(st.session_state.stocks)
print(st.session_state.tickers)
print(st.session_state.datas)
