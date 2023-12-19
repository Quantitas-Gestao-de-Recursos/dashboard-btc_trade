import streamlit as st
from src.datareader import data_struct


def float_comma(value):
    return '{:,.2f}'.format(value).replace('.', ',')


def comma_to_point(value):
    return '{:.}'.format(value)

def check_data():
    for data_alias in data_struct.keys():
        # check if variable exists
        if data_alias not in st.session_state or st.session_state[data_alias].empty:
            st.error(
                f'Arquivos base não atualizados. Por favor atualize os dados.')
            st.stop()
    pass
