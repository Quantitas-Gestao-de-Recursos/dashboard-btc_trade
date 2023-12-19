import streamlit as st
import pandas as pd
from src.btc import *
from src.datareader import *
from utils.utils import *

def build_screen():
    
    # Sidebar
    st.session_state['fund_alias'] = st.sidebar.selectbox('Fundo',('FIM MASTER', 'FIM CAPRI PREV', 'QUANTITAS FIA MONTECRISTO'))
    
    # Título
    title = rf"Controle - {dt.today().strftime('%d/%m/%Y')} - {st.session_state['fund_alias']}"
    title_alignment = f"""
    <div style="text-align: center;font-size: large;"> {title} </div>
    """
    
    st.markdown(title_alignment, unsafe_allow_html=True)

    # Content
    df_styled = construct_controleDf(st.session_state['fund_alias']).style.set_table_styles(table_styles).format(thousands='.',decimal=',',precision='2').hide(axis='index')
    
    st.dataframe(df_styled,use_container_width=True,hide_index=True,height=35*len(df_styled.index)+38,
                 column_config={
                    "% Doadas": st.column_config.ProgressColumn(
                        "Doadas",
                        help="Percentual da posição doado",
                        format="%.2f",
                        min_value=0,
                        max_value=66,
                    ),
                }
                 )

if __name__ == "__main__":
    st.set_page_config(
        page_title="TRADE_DOADOR - Controle",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    check_data()
    
    # session variable initialization
    if 'fund_alias' not in st.session_state:
        st.session_state['fund_alias'] = 'FIM MASTER'
        
    build_screen()


    

