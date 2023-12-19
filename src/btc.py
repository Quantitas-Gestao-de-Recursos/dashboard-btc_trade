import streamlit as st
from qlabs.business_days.business_days import DateManager as dm
from datetime import date as dt
from numpy import isnan
from math import floor
import pandas as pd
import warnings
from utils.utils import *

warnings.filterwarnings('ignore')

estrategias_validas = ['RV_RB', 'RV_CARRY', 'RV_LM',
                       'RV_MG', 'RV_JP', 'RV_IC', 'CARTEIRARV']

nao_doados = ['15', '14', '13', '12', '17', '18', '25',
              '30', '16', '08', '23', '20', '86', '94', '35']

fundos = {'FIM MASTER': 698878, 'FIM CAPRI PREV': 1583876,
          'QUANTITAS FIA MONTECRISTO': 783621}

table_styles = [dict(selector='td', props=[('text-align', 'center')]),
                dict(selector='th', props=[('text-align', 'center')]),
                dict(selector='', props=[('margin-left', 'auto'), ('margin-right', 'auto')])]


# ------------------------------------Código velho, refatorar DAQUI PRA BAIXO ---------------

def avg_taxDay(ticker, date=dm().previous_business_day(dt.today())):

    qry_result = st.session_state['btc_b3'].query('TckrSymb == @ticker')
    # qry_result['DnrAvrgRate'] = qry_result['DnrAvrgRate'].apply(lambda text: float(text.rstrip('%').replace(',', '.')) if text.endswith('%') else text).astype(float)
    qry_result['DnrAvrgRate'] = qry_result['DnrAvrgRate'].str.replace(
        ',', '.').str.rstrip('%').astype(float)

    if sum(qry_result['QtyShrDay']) != 0:
        return round((sum(qry_result['QtyShrDay']*qry_result['DnrAvrgRate']))/sum(qry_result['QtyShrDay']), 2)
    return 0


def avg_lentTax(ticker, fund_alias):
    cci = fundos[fund_alias]
    qry_result = st.session_state['imbarq_alugueis'].query(
        "Código_do_Investidor_Solicitado == @cci and Ativo == @ticker")
    if sum(qry_result['Qtde']) != 0:
        return float(round((sum(qry_result['Qtde']*qry_result['Taxa'])/sum(qry_result['Qtde'])), 2))
    return 0


def lentQtds(ticker, fund_alias):
    cci = fundos[fund_alias]
    qry_result = st.session_state['imbarq_alugueis'].query(
        "Código_do_Investidor_Solicitado == @cci and Ativo == @ticker")
    if isnan(sum(qry_result['Qtde'])):
        return 0
    return int(sum(qry_result['Qtde']))


def expiringQtds(ticker, fund_alias):
    cci = fundos[fund_alias]
    qry_result = st.session_state['imbarq_alugueis'].query(
        "Código_do_Investidor_Solicitado == @cci and Ativo == @ticker")
    if isnan(sum(qry_result['Liquidando'])):
        return 0
    return int(sum(qry_result['Liquidando']))


def get_liqQtds(ticker, fund_alias, day=0):
    # date = dt.datetime.strptime(date_input.value,"%d/%m/%Y").date()
    date = dt.today()
    d = date if day == 0 else dm().next_business_day(dia=date, delta=day-1)
    d = d.strftime("%Y-%m-%d")
    cci = fundos[fund_alias]
    qry_result = st.session_state['imbarq_liquidacoes'].query(
        "Código_do_Investidor_Solicitado == @cci and Código_de_Negociação==@ticker and Data_de_Liquidação == @d")
    qry_result['Net'] = qry_result['Quantidade_Comprada'] - \
        qry_result['Quantidade_Vendida']
    return qry_result['Net'].sum()


def get_strategiesTickerList(fund_alias, d='d1'):
    d = 'pos_rv_' + d
    df = st.session_state[d][st.session_state[d]
                             ['Estrategia'].isin(estrategias_validas)]
    df = df[df['Fundo'] == fund_alias]
    fund_position = df.drop(columns=['Fundo', 'Estrategia']).groupby(
        'Ticker').sum().reset_index()
    return list(fund_position[(fund_position['Ticker'].astype(str).str.len() <= 5) | (~fund_position['Ticker'].str[-2:].isin(nao_doados))]['Ticker'])


def get_strategiesTickerQtds(ticker, d, fund_alias):
    d = 'pos_rv_' + d
    df = st.session_state[d][st.session_state[d]
                             ['Estrategia'].isin(estrategias_validas)]
    df = df[df['Fundo'] == fund_alias]
    fund_position = df.drop(columns=['Fundo', 'Estrategia']).groupby(
        'Ticker').sum().reset_index()
    qry_result = fund_position[(fund_position['Ticker'].astype(str).str.len() <= 5) | (
        ~fund_position['Ticker'].str[-2:].isin(nao_doados))].query("Ticker == @ticker")
    qtd = 0 if qry_result.empty else qry_result['Qtd'].item()
    return qtd


def get_lendableTickerQtds(value):
    qtd = floor(value*(2/3))
    return qtd


def add_if_negative(row):
    total_d2 = row['Total D-2']
    liq_d1 = row['Liq D1'] if row['Liq D1'] < 0 else 0
    liq_d2 = row['Liq D2'] if row['Liq D2'] < 0 else 0
    return total_d2 + liq_d1 + liq_d2


@st.cache_data
def construct_controleDf(fund_alias):

    df = pd.DataFrame({'Ticker': get_strategiesTickerList(fund_alias)})
    df['Total D-2'] = df['Ticker'].apply(
        lambda x: get_strategiesTickerQtds(x, 'd3', fund_alias))
    df['Liq D2'] = df['Ticker'].apply(lambda x: get_liqQtds(x, fund_alias))
    df['Total D-1'] = df['Ticker'].apply(
        lambda x: get_strategiesTickerQtds(x, 'd2', fund_alias))
    df['Liq D1'] = df['Ticker'].apply(lambda x: get_liqQtds(x, fund_alias, 1))
    df['Total D0'] = df['Ticker'].apply(
        lambda x: get_strategiesTickerQtds(x, 'd1', fund_alias))

    df['Total Livre'] = df.apply(add_if_negative, axis=1)

    df['Usáveis'] = df['Total Livre'].apply(get_lendableTickerQtds)
    df['Doadas'] = df['Ticker'].apply(lambda x: lentQtds(x, fund_alias))
    df['% Doadas'] = (round(df['Doadas']/df['Total Livre'], 4)*100)
    df['Doar D0'] = df['Usáveis'] - df['Doadas']
    df['Vencendo'] = df['Ticker'].apply(lambda x: expiringQtds(x, fund_alias))

    df['Taxa Média Doadas'] = df['Ticker'].apply(
        lambda x: avg_lentTax(x, fund_alias))
    df['Taxa Média Mercado'] = df['Ticker'].apply(
        lambda x: avg_taxDay(x, fund_alias))
    df['Taxa Média Mercado'] = df['Taxa Média Mercado'].astype(float)

    return df.reset_index(drop=True)


@st.cache_data
def construct_listaDoadoras(cci_input, min_tax=1, broker_input=2):

    if st.session_state['fund_alias'] != cci_input:
        # limpa cache = evita duplicidade da lista
        st.cache_data.clear()
        st.session_state['fund_alias'] = cci_input

    df = construct_controleDf(cci_input)
    df = df[df['Taxa Média Mercado'] >= min_tax]
    df = df[['Ticker', 'Doar D0', 'Taxa Média Mercado']].rename(
        columns={'Ticker': 'Papel', 'Taxa Média Mercado': 'Taxa', 'Doar D0': 'Quantidade Limite'})
    df['Quantidade Limite'] = df['Quantidade Limite'].apply(
        lambda x: floor((x/broker_input)/1000) * 1000)
    df = df[df['Quantidade Limite'] >= 1000].sort_values(
        by=['Taxa'], ascending=False)
    df['Lado'] = 'Doador'
    df['Fundo'] = cci_input
    df = df[['Lado', 'Papel', 'Quantidade Limite', 'Fundo', 'Taxa']]
    df['Taxa'] = df['Taxa'].round(2)

    return df


@st.cache_data
def construct_listaPorFundo():

    merged_df = load_distribuicao()

    distrib_df = merged_df.copy()
    distrib_df = pd.pivot_table(
        merged_df, index='Papel', columns='Fundo', values='Quantidade Limite', fill_value=0)
    distrib_df = distrib_df[['FIM MASTER',
                             'FIM CAPRI PREV', 'QUANTITAS FIA MONTECRISTO']]

    return distrib_df


@st.cache_data
def load_distribuicao():
    merged_df = pd.DataFrame()
    
    for fund_alias in fundos:
        merged_df = construct_listaDoadoras(fund_alias) if merged_df.empty else pd.concat([
            merged_df, construct_listaDoadoras(fund_alias)])
    return merged_df

@st.cache_data
def construct_listaConcatenada(df):

    merged_df = load_distribuicao()

    merged_df = merged_df.groupby(
        ['Papel', 'Lado', 'Taxa']).sum().reset_index()
    # Lista Concatenada
    merged_df = merged_df[['Lado', 'Papel', 'Quantidade Limite', 'Taxa']]
    merged_df['Quantidade Limite'] = merged_df['Papel'].map(df.sum(axis=1))

    merged_df = merged_df.dropna()

    merged_df['Quantidade Limite'] = merged_df['Quantidade Limite'].astype(int)
    merged_df['Quantidade Limite'] = merged_df['Quantidade Limite'].apply(
        lambda x: str(x).replace(',', '.'))
    merged_df['Taxa'] = merged_df['Taxa'].apply(
        lambda x: str(x).replace('.', ','))

    return merged_df
