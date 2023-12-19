import streamlit as st
import pandas as pd
from utils.utils import *

if __name__ == "__main__":
    
    st.set_page_config(
        page_title="TRADE_DOADOR - Histórico",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Checa se os arquivos base foram atualizados
    check_data()
    
    st.markdown("### Histórico")
