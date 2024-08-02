import pandas as pd
import numpy as np
import streamlit as stl

stl.write("Bem-Vindo Investidor!")

def add_stock():
    stl.text_input("Ticker do ativo: ", key="ticker")
    stl.write(stl.session_state.ticker)

stl.button("Adicionar Ativo", on_click=add_stock())