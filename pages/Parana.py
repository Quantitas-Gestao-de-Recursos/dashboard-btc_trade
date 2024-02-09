import streamlit as st
import pandas as pd
from src.btc import *
from src.datareader import *
from utils.utils import *
import datetime as dt
import streamlit_calendar as st_calendar


def build_screen():

    # Sidebar
    show_calendar = st.sidebar.toggle("Show Calendar", key="show_calendar")

    verify_date = st.sidebar.date_input(
        "BTC Liquidation List Date", value="today", format="DD/MM/YYYY")

    # Título
    title = rf"Controle Doadoras Paraná"
    title_alignment = f"""
    <div style="text-align: center;font-size: large;"> {title} </div>
    """

    st.markdown(title_alignment, unsafe_allow_html=True)

    # Content

    column_config = {
        "% Doadas": st.column_config.ProgressColumn(
            "Doadas",
            help="Percentual da posição doado",
            format="%.2f",
            min_value=0,
            max_value=100,
        ),
    }

    try:

        df_quant = construct_controleDfQuant(st.session_state['fund_alias'])
        df_quant = df_quant[~df_quant['Ticker'].isin(
                ['RRRP3', 'SMAL11'])]
        df_liquidacao = df_quant[['Ticker', 'Doar D0']].copy()
        df_liquidacao.rename(columns={'Doar D0': 'Liquidar D0'}, inplace=True)
        df_liquidacao = df_liquidacao[df_liquidacao['Liquidar D0'] < 0]
        
        doadoras_quant = construct_listaDoadorasQuant(df_quant, broker_input=2)

        if not df_quant.empty:
            df_quant = df_quant.style.set_table_styles(table_styles).format(
                thousands='.', decimal=',', precision='2').hide(axis='index')

            st.dataframe(df_quant, hide_index=True, height=35*len(df_quant.index)+38,
                         column_config={
                "% Doadas": st.column_config.ProgressColumn(
                    "Doadas",
                    help="Percentual da posição doado",
                    format="%.2f",
                    min_value=0,
                    max_value=100,
                ),
            }
            )
        if not doadoras_quant.empty:
            st.text("1 BROKER SÓ !!!")
            doadoras_quant = doadoras_quant[[
                'Lado', 'Papel', 'Quantidade Limite', 'Taxa', 'Fundo']]
            # Filter the DataFrame by values not contained in the list
            doadoras_quant = doadoras_quant[~doadoras_quant['Papel'].isin(
                ['POMO4', 'UGPA3', 'CSMG3', 'BBSE3', 'RRRP3', 'SMAL11'])]

            df_styled_doadoras = doadoras_quant.style.set_table_styles(table_styles).format(thousands='.', decimal=',', precision='2').background_gradient(
                vmin=0, vmax=66, cmap='RdYlGn_r', subset='Taxa').hide(axis='index')
            st.dataframe(df_styled_doadoras, use_container_width=True,
                         hide_index=True, height=35*len(doadoras_quant.index)+38,
                         column_config={"Lado": {"alignment": "center"}},
                         )

        if not df_liquidacao.empty:

            df_liquidacao = df_liquidacao.style.set_table_styles(table_styles).format(
                thousands='.', decimal=',', precision='2').hide(axis='index')
            st.text(f"Lista Liquidação {verify_date.strftime('%d/%m')}")
            st.dataframe(df_liquidacao, hide_index=True,
                         height=35*len(df_liquidacao.index)+38)

        if show_calendar:
            df_calendar = get_calendarList()
            print(df_calendar)
            calendar_events = []
            for key in df_calendar.keys():
                for index, row in df_calendar[key].iterrows():
                    event = {
                        "title": f'{row["Ticker"]} - {row["Quantidade"]}',
                        "start": key.strftime('%Y-%m-%dT%H:%M:%S'),
                        "end": key.strftime('%Y-%m-%dT%H:%M:%S'),
                        "allDay": True,
                    }
                    calendar_events.append(event)
            calendar = st_calendar.calendar(events=calendar_events)

    except Exception as e:
        st.error(e)


if __name__ == "__main__":
    st.set_page_config(
        page_title="TRADE_DOADOR - Paraná",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    check_data()

    # session variable initialization
    if 'fund_alias' not in st.session_state:
        st.session_state['fund_alias'] = 'FIM MASTER'

    build_screen()
