from datetime import date as dt

# import qlabs.business_days as business_days
from qlabs.business_days.business_days import DateManager as dm
from qlabs.sharepoint import SharePoint
import streamlit as st
import pandas as pd


# Coloquei aqui e não em um JSON pra nao ter que ficar lendo arquivo
# meu objetivo era rodar tudo isso na nuvem, e ler arquivos pelo sharepoint

data_struct = {
    "pos_rv_d1": [
        "\\Publico - Documentos\\gerenciais\\POS_RV COMPLETO",
        "POS_RV_COMPLETO_DATE.xlsx",
        "Plan1",
        0
    ],
    "pos_rv_d2": [
        "\\Publico - Documentos\\gerenciais\\POS_RV COMPLETO",
        "POS_RV_COMPLETO_DATE.xlsx",
        "Plan1",
        1
    ],
    "pos_rv_d3": [
        "\\Publico - Documentos\\gerenciais\\POS_RV COMPLETO",
        "POS_RV_COMPLETO_DATE.xlsx",
        "Plan1",
        2
    ],
    "imbarq_liquidacoes": [
        "\\Publico - Documentos\\Arquivos Imbarq\\Processados\\02_Posicao_do_mercado_a_vista",
        "02_Posicao_do_mercado_a_vista_DATE.csv",
        '02_Posicao_do_mercado_a_vista_2',
        0
    ],
    "imbarq_alugueis": [
        "\\Publico - Documentos\\Arquivos Imbarq\\Processados\\06_Posicoes_de_aluguel_de_ativos",
        "06_Posicoes_de_aluguel_de_ativos_DATE.csv",
        '06_Posicoes_de_aluguel_de_ativo',
        0
    ],
    "btc_b3": [
        "\\Gestao de Recursos - Documentos\\Operacional Mesa\\Alugueis\\dados_b3",
        "BTC_DATE.csv",
        'BTC_DATE',
        0
    ]
}


class DataReader:
    def __init__(self, data_alias):

        # dir_type = 'publico' or 'gestao'
        self.dir_type = data_struct[data_alias][0].split()[0].lower()[1:]

        # data_dir  diretorio do arquivo
        self.data_dir = data_struct[data_alias][0].split('\\')[2:]
        self.data_dir = "\\".join(self.data_dir)

        # data_filename = nome do arquivo
        self.data_filename = data_struct[data_alias][1]

        # data_sheetname = nome da planilha
        self.data_sheetname = data_struct[data_alias][2] if not "DATE" in data_struct[data_alias][2] else data_struct[data_alias][2].replace("DATE", dm().previous_business_day(
            dt.today(), data_struct[data_alias][3]).strftime("%Y%m%d"))

        # substitute DATE string for self.date
        self.data_filename = self.data_filename.replace("DATE", dm().previous_business_day(
            dt.today(), data_struct[data_alias][3]).strftime("%Y%m%d"))

        self.sharepoint = SharePoint(self.dir_type)
        self.data_alias = data_alias

    def read_data(self):
        # Read data from file and return dataframe
        try:
            data = self.sharepoint.download_file_to_memory(
                path=self.data_dir,
                target_file_name=self.data_filename,
                sheet_name=self.data_sheetname
            )

            # Se não for xlsx, é csv
            if not self.data_filename.endswith('.xlsx'):
                data = pd.read_csv(data, encoding='latin-1', sep=";")

            return self.clean_data(data)

        except Exception as e:
            st.error(f"Não foi possível ler o arquivo {self.data_filename}")
            st.error(f"{e}")
            st.stop()

        return True

    def clean_data(self, data):
        # Clean data accordingly to data_alias
        df = data

        if 'pos_rv' in self.data_alias:
            df = df.drop(columns=['ESTRATÉGIA MACRO']).rename(
                columns={'ATIVO': 'Ticker', 'FUNDO': 'Fundo', 'ESTRATÉGIA MICRO': 'Estrategia', 'QTDE': 'Qtd'})
            df.columns = [
                c.replace(' ', '_') for c in df.columns]
            df['Fundo'] = df['Fundo'].str.upper()

        elif 'imbarq_liquidacoes' in self.data_alias:
            df.columns = [c.replace(' ', '_') for c in df.columns]
            columns_imbarqLiq = ['Código_do_Investidor_Solicitado', 'Código_de_Negociação',
                                 'Data_de_Liquidação', 'Quantidade_Comprada', 'Quantidade_Vendida']

            df = df[columns_imbarqLiq].fillna(0)
            df['Quantidade_Comprada'] = df['Quantidade_Comprada'].astype(int)
            df['Quantidade_Vendida'] = df['Quantidade_Vendida'].astype(int)
            df['Código_de_Negociação'] = df['Código_de_Negociação'].apply(
                lambda text: text.rstrip('F') if text.endswith('F') else text)

        elif 'imbarq_alugueis' in self.data_alias:
            df.columns = [c.replace(' ', '_') for c in df.columns]
            columns_imbarqAluguel = ['Número_do_Contrato', 'Data_de_negociação', 'Código_do_Investidor_Solicitado', 'Natureza/Lado_Doador/Vendedor',
                                     'Código_de_Negociação', 'Quantidade_Atual', 'Taxa_doadora_ou_tomadora_dependendo_da_posição', 'Quantidade_em_Liquidação']

            df = df[columns_imbarqAluguel]

            df = df.query("`Natureza/Lado_Doador/Vendedor` == 'DOADOR'").drop(
                columns=['Natureza/Lado_Doador/Vendedor']).drop_duplicates().fillna(0)
            df['Taxa_doadora_ou_tomadora_dependendo_da_posição'] = df['Taxa_doadora_ou_tomadora_dependendo_da_posição'].replace(
                ',', '.', regex=True).astype(float)
            df['Taxa_doadora_ou_tomadora_dependendo_da_posição'] = df['Taxa_doadora_ou_tomadora_dependendo_da_posição'].apply(
                lambda x: x*100).dropna()
            df['Quantidade_em_Liquidação'] = df['Quantidade_em_Liquidação'].astype(
                int)
            df['Quantidade_Atual'] = df['Quantidade_Atual'].astype(int)
            df = df.reset_index(drop=True).rename(columns={'Taxa_doadora_ou_tomadora_dependendo_da_posição': 'Taxa', 'Código_de_Negociação': 'Ativo',
                                                           'Quantidade_Atual': 'Qtde', 'Quantidade_em_Liquidação': 'Liquidando'})

        return df
