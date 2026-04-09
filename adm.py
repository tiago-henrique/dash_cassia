import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from io import BytesIO

st.set_page_config(layout="wide")
#database = pd.read_excel(st.secrets['DATABASE'])
database = pd.read_excel("database/dados_cassia_n.xlsx")
st.title("Indicadores Sentinela -  SEPSE")
#Excluir as duplicatas e definir dados
db_clean = database[database['Result_episdo'] == "Primeira amostra"]
db_clean = db_clean[db_clean['Susp. SEPSE?'] == "SIM"]

#Inserir colunas de mês e ano do registro
db_clean['data_registro'] = pd.to_datetime(db_clean['Data/Hora Abertura Informada na Ficha Med'], format='%d/%m/%y %H:%M')
db_clean['hora_registro'] = db_clean['data_registro'].dt.time
db_clean['dia_registro'] = db_clean['data_registro'].dt.day
db_clean['mes_registro'] = db_clean['data_registro'].dt.month
db_clean['ano_registro'] = db_clean['data_registro'].dt.year
db_clean['dia_semana'] = db_clean['data_registro'].dt.strftime("%A")
db_clean['mes_ano'] = db_clean['data_registro'].dt.strftime('%m-%Y')
db_clean['idade_anos'] = db_clean['Idade'].str.extract(r'(\d+)\s*Ano').fillna(0).astype(int)

mes_ano_opcoes = db_clean['mes_ano'].sort_values().dropna().unique()
bundle_opcoes = ['', 'CONFORME']
lactato_opcoes = ['', 'CONFORME']
hemocultura_opcoes = ['', 'CONFORME']
atb_opcoes = ['', 'CONFORME']
expansao_volemica_opcoes = ['', 'CONFORME']
especialidade_opcoes =['Todas'] +list(db_clean['Especialidade'].sort_values().unique())


#mes_ano_opcoes = ['Todos'] + list(mes_ano_opcoes)
with st.sidebar:
    selecao_mes_ano = st.selectbox("Mês / Ano", options=mes_ano_opcoes)
    selecao_bundle = st.selectbox("Bundle Completo", options=bundle_opcoes)
    selecao_lactato = st.selectbox("Lactato", options=lactato_opcoes)
    selecao_hemocultura = st.selectbox("Hemocultura", options=hemocultura_opcoes)
    selecao_atb = st.selectbox("ATB 1 h", options=atb_opcoes)
    selecao_exp_volemica = st.selectbox("Expansão Volêmica", options=expansao_volemica_opcoes)
    selecao_especialidade = st.selectbox("Especialidade", options=especialidade_opcoes)
    
    

#Aplicando os filtros no dataset
#db_clean_filtrado = db_clean[(db_clean['mes_ano'] == selecao_mes_ano) & (db_clean['Suspeita sepse final'] == selecao_supeita_sepse) & (db_clean['Result_episdo'] == selecao_tipo_registro)]
# if(mes_ano_opcoes == 'Todos'):
db_clean_filtrado = db_clean
# else:

filtros = []

if selecao_mes_ano:
    filtros.append(db_clean_filtrado['mes_ano'] == selecao_mes_ano)

if selecao_bundle == 'CONFORME':
    filtros.append(db_clean_filtrado['Bundle Completo'] == 'CONFORME')

if selecao_lactato == 'CONFORME':
    filtros.append(db_clean_filtrado['Lactato 30 min (Bundle)'] == 'CONFORME')

if selecao_especialidade != 'Todas':
    filtros.append(db_clean_filtrado['Especialidade'] == selecao_especialidade)

if filtros:
    db_clean_filtrado = db_clean_filtrado[np.logical_and.reduce(filtros)]

#Contar atendimentos após aplicação dos filtros
total_atendidos = db_clean_filtrado['Prontuário'].count()
st.write(f'Total de atendimentos: {total_atendidos}')

#Obter a média de idade dos pacientes atendidos

media_idade = db_clean_filtrado['idade_anos'].mean()
media_idade = round(media_idade,1)
st.write(f'Média de idade: {media_idade}')

#Imprimir tabela com os dados
st.write(db_clean_filtrado)

#Gráfico de Bundle completo e Bundle completo %
col1, col2 = st.columns([1,1], border=True)

valores = ['CONFORME', 'NÃO CONFORME']

with col1:
    st.header("Bundle Conforme?")
    grafico_bundle = db_clean_filtrado['Bundle Completo'].value_counts()
    fig = px.pie(
        values=grafico_bundle.values,
        names=grafico_bundle.index,
        #  title="Distribuição do Bundle"
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(showlegend=True)
    st.plotly_chart(fig)

with col2:
    # Calculando dados
    bundle_completo_perc = db_clean_filtrado[
        db_clean_filtrado['Bundle Completo'].isin(valores)
    ]['Bundle Completo'].value_counts().reset_index()

    bundle_completo_perc.columns = ['categoria', 'quantidade']

    # Criando gráfico
    fig_bundle = px.bar(
        bundle_completo_perc,
        x='categoria',
        y='quantidade',
        title='% Bundle Completo por Mês'
    )

    # Linha de meta (ex: 80)
    fig_bundle.add_hline(
        y=80,
        line_dash='dash',
        line_color='red',
        annotation_text='Meta: 80%',
        annotation_position='top right'
    )

    # Mostrar no Streamlit
    st.plotly_chart(fig_bundle, use_container_width=True)

col3, col4 = st.columns([1, 1], border=True)

with col3:
    # Calculando dados
    atm_perc = db_clean_filtrado[db_clean_filtrado['ATB 1h (Bundle)'].isin(valores)]['ATB 1h (Bundle)'].value_counts().reset_index()
    atm_perc.columns = ['categoria', 'quantidade']

    # Criando gráfico
    fig_atm = px.bar(
        bundle_completo_perc,
        x='categoria',
        y='quantidade',
        title='% ATB em 1h por Mês'
    )

    # Linha de meta (ex: 80)
    fig_atm.add_hline(
        y=100,
        line_dash='dash',
        line_color='red',
        annotation_text='Meta: 100%',
        annotation_position='top right'
    )

    # Mostrar no Streamlit
    st.plotly_chart(fig_atm, use_container_width=True)
