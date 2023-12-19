import streamlit as st
from datetime import date as dt
from qlabs.sharepoint import SharePoint
from src.btc import *
from src.datareader import data_struct
from utils.utils import *


# fazer classe
def build_screen():
    # Sidebar
    st.session_state['fund_alias'] = st.sidebar.selectbox(
        'Fundo', ('FIM MASTER', 'FIM CAPRI PREV', 'QUANTITAS FIA MONTECRISTO'))
    taxa = st.sidebar.slider('Taxa Limite (%)', min_value=0.0,
                             max_value=2.0, value=1.0, step=0.1)
    n_brokers = st.sidebar.number_input(
        'Nº de brokers', min_value=1, max_value=10, value=2, step=1)

    # Título
    title = rf"Lista Doadora - {dt.today().strftime('%d/%m/%Y')} - {st.session_state['fund_alias']}"
    title_alignment = f"""
    <div style="text-align: center;font-size: large;"> {title} </div>
    """
    st.markdown(title_alignment, unsafe_allow_html=True)

    # Content
    df = construct_listaDoadoras(
        st.session_state['fund_alias'], taxa, n_brokers)
    
    df = df[['Lado','Papel','Quantidade Limite','Taxa','Fundo']]
    
    df_styled = df.style.set_table_styles(table_styles).format(thousands='.', decimal=',', precision='2').background_gradient(
        vmin=0, vmax=66, cmap='RdYlGn_r', subset='Taxa').hide(axis='index')

    st.dataframe(df_styled, use_container_width=True,
                 hide_index=True, height=35*len(df.index)+38,
                 column_config={"Lado": {"alignment": "center"}},
                 )


if __name__ == "__main__":
    st.set_page_config(
        page_title="TRADE_DOADOR - Lista Doadora",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Checa se os arquivos base foram atualizados
    check_data()

    # session variable initialization
    if 'fund_alias' not in st.session_state:
        st.session_state['fund_alias'] = 'FIM MASTER'

    build_screen()
