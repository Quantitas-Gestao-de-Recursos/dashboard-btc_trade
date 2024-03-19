import streamlit as st
import pandas as pd
from utils import *
from src.datareader import *
from utils.utils import *
from src.btc import *
from datetime import date as dt


def update_state():

    progress_bar = st.progress(0, text="Downloading data...")

    for data_alias in data_struct.keys():
        reader = DataReader(data_alias)
        st.session_state[data_alias] = reader.read_data()
        progress_bar.progress((list(data_struct.keys()).index(
            data_alias)+1)/len(data_struct.keys()), text='Downloading data...')

    st.session_state['updated'] = not st.session_state['updated']
    progress_bar.progress(100)

    # gambiarra
    st.session_state['proporcoes_df'] = construct_listaPorFundo()
    st.session_state['doadoras_df'] = construct_listaConcatenada(
        st.session_state['proporcoes_df'])


def build_screen():
    # Sidebar

    for data_alias in data_struct.keys():
        string = '<span style="color:red">Outdated</span>' if st.session_state[
            data_alias].empty else '<span style="color:green">Updated</span>'
        st.sidebar.markdown(
            f'<div style="text-align: left;">{data_alias}</div><div style="text-align: right;">{string}</div>', unsafe_allow_html=True)
    st.sidebar.button('Atualizar', on_click=update_state)

    # Título
    title = f"Dashboard - {dt.today().strftime('%d/%m/%Y')}"
    title_alignment = f"""
    <div style="text-align: center;font-size: 35px;"> {title} </div>
    """
    # st.header(title_alignment,unsafe_allow_html=True)
    st.markdown(title_alignment, unsafe_allow_html=True)

    # Content
    if st.session_state['updated']:
        c1, c2 = st.columns((1, 1))
        with c1:
            st.subheader("Doadoras por fundo")

            updated_df_prop = st.data_editor(st.session_state['proporcoes_df'], height=35*len(
                st.session_state['proporcoes_df'].index)+38, num_rows="dynamic", key='data_editor_2')

            if not st.session_state["proporcoes_df"].equals(updated_df_prop):
                st.session_state["proporcoes_df"] = updated_df_prop.copy()
                st.session_state["doadoras_df"] = construct_listaConcatenada(
                    st.session_state['proporcoes_df'])

        with c2:
            st.subheader("Lista Doadora")
            updated_df_doadoras = st.data_editor(st.session_state['doadoras_df'], height=35*len(
                st.session_state['doadoras_df'].index)+38, hide_index=True, num_rows="dynamic", key='data_editor_1')

            # if not st.session_state["doadoras_df"].equals(updated_df_doadoras):
            # st.button(
            #     'Copy Dataframe', on_click=st.session_state['doadoras_df'].to_clipboard(index=False), key='data1')

    else:
        st.info("Por favor, atualize os dados.")


if __name__ == "__main__":

    st.set_page_config(
        page_title="TRADE_DOADOR - Dashboard",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Intialize session variables
    if 'updated' not in st.session_state:
        st.session_state['updated'] = False
        st.session_state['fund_alias'] = 'FIM MASTER'

        for data_alias in data_struct.keys():
            st.session_state[data_alias] = pd.DataFrame()

        st.session_state['doadoras_df'] = pd.DataFrame()
        st.session_state['proporcoes_df'] = pd.DataFrame()

    build_screen()
