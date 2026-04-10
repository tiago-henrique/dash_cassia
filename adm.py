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
database = pd.read_excel(st.secrets['DATABASE'])

st.title("Indicadores Sentinela -  SEPSE")
#Excluir as duplicatas e definir dados
db_clean = database[database['Result_episdo'] == "Primeira amostra"]
db_clean = db_clean[db_clean['Susp. SEPSE?'] == "SIM"]
db_clean_filtrado = db_clean

#Inserir colunas de mês e ano do registro
db_clean['data_registro'] = pd.to_datetime(db_clean['Data/Hora Abertura Informada na Ficha Med'], format='%d/%m/%y %H:%M')
db_clean['hora_registro'] = db_clean['data_registro'].dt.time
db_clean['dia_registro'] = db_clean['data_registro'].dt.day
db_clean['mes_registro'] = db_clean['data_registro'].dt.month
db_clean['ano_registro'] = db_clean['data_registro'].dt.year
db_clean['dia_semana'] = db_clean['data_registro'].dt.strftime("%A")
db_clean['mes_ano'] = db_clean['data_registro'].dt.strftime('%m-%Y')
db_clean['idade_anos'] = db_clean['Idade'].str.extract(r'(\d+)\s*Ano').fillna(0).astype(int)

mes_ano_opcoes = ['Todos os meses'] + list (db_clean['mes_ano'].sort_values().dropna().unique())
bundle_opcoes = ['', 'CONFORME']
lactato_opcoes = ['', 'CONFORME']
hemocultura_opcoes = ['', 'CONFORME']
atb_opcoes = ['', 'CONFORME']
expansao_volemica_opcoes = ['', 'CONFORME']
especialidade_opcoes =['Todas'] +list(db_clean['Especialidade'].sort_values().unique())

with st.sidebar:
    selecao_mes_ano = st.selectbox("Mês / Ano", options=mes_ano_opcoes)
    selecao_bundle = st.selectbox("Bundle Completo", options=bundle_opcoes)
    selecao_lactato = st.selectbox("Lactato", options=lactato_opcoes)
    selecao_hemocultura = st.selectbox("Hemocultura", options=hemocultura_opcoes)
    selecao_atb = st.selectbox("ATB 1 h", options=atb_opcoes)
    selecao_exp_volemica = st.selectbox("Expansão Volêmica", options=expansao_volemica_opcoes)
    selecao_especialidade = st.selectbox("Especialidade", options=especialidade_opcoes)
  
#Aplicar os filtros    
filtros = []
if selecao_mes_ano != 'Todos os meses':
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

st.markdown("""
    <style>
        .header{
            display: flex;
            flex-wrap: wrap;
            width: 100%;
        }
        .atendimentos {
            background: #336799;
            border: 1px solid #c0c0c0;
            border-radius: 5px;
            box-shadow: 0 4px 8px 0 #c0c0c0;
            color: #FFF ;
            text-align: left;
            padding: 0.7rem;
            width: 15vw;
            margin-bottom: 5px;
            margin-left: 5px;
            width: 20%;
        }
        .atendimentos h4{
            font-size: 20px;
            text-align: center;
            width: 100%;
        }
        .atendimentos p{
            font-size: 17px;
            font-weight: bold;
            margin: auto;
            width: 20%;

        }
    </style>
""", unsafe_allow_html=True)


#Obter a média de idade dos pacientes atendidos
media_idade = db_clean_filtrado['idade_anos'].mean()
media_idade = round(media_idade,1)
st.markdown(f'<div class="header"><div class="atendimentos"><h4>Total de atendimentos</h4><p>{total_atendidos}</p></div><div class="atendimentos"><h4>Média de Idade</h4> <p>{media_idade}</p></div></div>',unsafe_allow_html=True)

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

    if bundle_completo_perc.empty or bundle_completo_perc.shape[1] <= 1:
        bundle_meta = 'Sem dados disponíveis'
        cor = "gray"
    else:
        valor_bundle = int(bundle_completo_perc.iloc[0, 1])
        bundle_meta = 'A meta foi atingida' if valor_bundle > 80 else 'A meta não foi atingida'
        cor = "green" if valor_bundle > 80 else "red"
    st.badge(bundle_meta, color=cor)
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
    fig_bundle.update_traces(texttemplate='%{text}', textposition='outside', marker_color='#336799')
    fig_bundle.update_layout(xaxis_title='Status', yaxis_title='Total')

    # Mostrar no Streamlit
    st.plotly_chart(fig_bundle, use_container_width=True)

col3, col4 = st.columns([1, 1], border=True)
with col3:
    # Calculando dados
    atb_perc = db_clean_filtrado[db_clean_filtrado['ATB 1h (Bundle)'].isin(valores)]['ATB 1h (Bundle)'].value_counts().reset_index()
    atb_perc.columns = ['categoria', 'quantidade']
   
    if atb_perc.empty or atb_perc.shape[1] <= 1:
        atb_meta = 'Sem dados disponíveis'
        cor = "gray"
    else:
        valor = int(atb_perc.iloc[0, 1])
        atb_meta = 'A meta foi atingida' if valor > 100 else 'A meta não foi atingida'
        cor = "green" if valor > 100 else "red"

    st.badge(atb_meta, color=cor)
    # Criando gráfico
    fig_atb = px.bar(
        bundle_completo_perc,
        x='categoria',
        y='quantidade',
        title='% ATB em 1h por Mês'
    )
    # Linha de meta (ex: 80)
    fig_atb.add_hline(
        y=100,
        line_dash='dash',
        line_color='red',
        annotation_text='Meta: 100%',
        annotation_position='top right'
    )

    fig_atb.update_traces(texttemplate='%{text}', textposition='outside', marker_color='#336799')
    fig_atb.update_layout(xaxis_title='Status', yaxis_title='Total')

    # Mostrar no Streamlit
    st.plotly_chart(fig_atb, use_container_width=True)

with col4:
    sexo_perc = db_clean_filtrado['Sexo'].value_counts().reset_index()
    sexo_perc.columns = ['Sexo', 'Quantidade']
    fig_sexo = px.bar(
        sexo_perc,
        x='Sexo',
        y='Quantidade',
        title='Sexo'
    )
    fig_sexo.update_traces(texttemplate='%{text}', textposition='outside', marker_color='#336799')
    fig_sexo.update_layout(xaxis_title='Status', yaxis_title='Total')

    st.plotly_chart(fig_sexo, use_container_width=True)

col5, col6 = st.columns([1,1], border=True)
with col5:
    hemocultura = db_clean_filtrado['Hemoculturas (Bundle)'].value_counts().reset_index()
    hemocultura.columns = ['Status', 'Quantidade']
    fig_hemocultura = px.bar(
        hemocultura,
        x='Status',
        y='Quantidade',
        title='Hemocultura'
    )
    fig_hemocultura.update_traces(texttemplate='%{text}', textposition='outside', marker_color='#336799')
    fig_hemocultura.update_layout(xaxis_title='Status', yaxis_title='Total')

    st.plotly_chart(fig_hemocultura, use_container_width=True)

with col6:
    atb = db_clean_filtrado['ATB 1h (Bundle)'].value_counts().reset_index()
    atb.columns = ['Status', 'Quantidade']
    fig_atb = px.bar(
        atb,
        x='Status',
        y='Quantidade',
        title='ATB 1h'
    )
    fig_atb.update_traces(texttemplate='%{text}', textposition='outside', marker_color='#336799')
    fig_atb.update_layout(xaxis_title='Status', yaxis_title='Total')

    st.plotly_chart(fig_atb, use_container_width=True)

col7, col8 = st.columns([1,1], border=True)
with col7:
    lactato = db_clean_filtrado['Lactato 30 min (Bundle)'].value_counts().reset_index()
    lactato.columns = ['Status', 'Quantidade']
    fig_lactato = px.bar(
        lactato,
        x='Status',
        y='Quantidade',
        title='Lactato 30 min.'
    )
    fig_lactato.update_traces(texttemplate='%{text}', textposition='outside', marker_color='#336799')
    fig_lactato.update_layout(xaxis_title='Status', yaxis_title='Total')

    st.plotly_chart(fig_lactato, use_container_width=True)

with col8:
    expansao = db_clean_filtrado['Expansão Volêmica (Bundle)'].value_counts().reset_index()
    expansao.columns = ['Status', 'Quantidade']
    fig_expansao = px.bar(
        expansao,
        x='Status',
        y='Quantidade',
        title='Expansão Volêmica'
    )
    fig_expansao.update_traces(texttemplate='%{text}', textposition='outside', marker_color='#336799')
    fig_expansao.update_layout(xaxis_title='Status', yaxis_title='Total')

    st.plotly_chart(fig_expansao, use_container_width=True)
