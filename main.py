import pandas as pd
import numpy as np
import streamlit as st
import yfinance as yf
from datetime import datetime
import plotly as plt

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
        st.plotly_chart(st.session_state.df, x='Date', y='Close')
    else:
        st.write("Nenhum dado disponível para gerar o gráfico.")

# Botão para obter dados das ações
if st.button("Obter Dados das Ações"):
    df = get_stock_data()

# Botão para obter gráficos
if st.button("Obter Gráficos"):
    gerar_grafico()

print(st.session_state.stocks)
print(st.session_state.tickers)
print(st.session_state.datas)
