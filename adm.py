import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import streamlit as st

st.set_page_config(layout="wide")
database = pd.read_excel(st.secrets['DATABASE'])

#Excluir as duplicatas e definir dados
db_clean = database[database['Result_episdo'] == "ABERTURA"]
db_clean = db_clean[db_clean['Suspeita sepse final'] == "SIM"]

#Inserir colunas de mês e ano do registro
db_clean['data_registro'] = pd.to_datetime(db_clean['Data/Hora Abertura Informada na Ficha Med'], format='%m/%d/%y %H:%M')
db_clean['dia_registro'] = db_clean['data_registro'].dt.day
db_clean['mes_registro'] = db_clean['data_registro'].dt.month
db_clean['ano_registro'] = db_clean['data_registro'].dt.year
db_clean['dia_semana'] = db_clean['data_registro'].dt.strftime("%A")

desc_mes = {
    1.0 : 'Janeiro',
    2.0 : 'Fevereiro',
    3.0 : 'Março',
    4.0 : 'Abril',
    5.0 : 'Maio',
    6.0 : 'Junho',
    7.0 : 'Julho',
    8.0 : 'Agosto',
    9.0 : 'Setembro',
    10.0 : 'Outubro',
    11.0 : 'Novembro',
    12.0 : 'Dezembro'
}
desc_semana = {
    'Monday' : 'Segunda-feira',
    'Tuesday' : 'Terça-feira',
    'Wednesday': 'Quarta-feira',
    'Thursday' : 'Quinta-feira',
    'Friday' : 'Sexta-feira',
    'Saturday' : 'Sábado',
    'Sunday' : 'Domingo'
}

db_clean['mes_registro'] = db_clean['mes_registro'].map(desc_mes)
db_clean['dia_semana'] = db_clean['dia_semana'].map(desc_semana)

#Selecionar o mês para visualizar os dados
#Sidebar
meses = db_clean['mes_registro'].dropna().unique()
meses = ['Todos'] + list(meses)
mes_selecionado = st.sidebar.selectbox(
    "Selecione o mês", options=meses
)

#Filtros
if(mes_selecionado == 'Todos'):
    db_clean_filtrado = db_clean
else:
    db_clean_filtrado = db_clean[(db_clean['mes_registro'] == mes_selecionado)]

#Calcular Média de Idade
db_clean_filtrado['idade_anos'] = db_clean_filtrado['Idade'].str.extract(r'(\d+)\s*Ano').fillna(0).astype(int)

#Exibir os dados na tela
#tabelas
st.title("Dados planilha Sepse")
atendimento_especialidade = db_clean_filtrado['Especialidade'].value_counts()
st.header("Atendimento por Especialidades")
st.write(atendimento_especialidade)
st.bar_chart(atendimento_especialidade)

#Calcular Total de Atendimentos
total_atendidos = db_clean_filtrado['Prontuário'].count()

#Definir paciente
st.header("Quem são nossos pacientes")
sexo = db_clean_filtrado['Sexo'].value_counts()
un_hosp = db_clean_filtrado['UNIDADE HOSPITALAR'].value_counts()
sitios_acometidos = db_clean_filtrado['Um ou mais sítios'].value_counts()

#Graficos de pizza
fig_sexo = px.pie(
    sexo,
    values=sexo.values,
    names=sexo.index,
    title='Sexo',
    hole=0.5,
)
fig_sexo.update_traces(textposition='outside', textinfo='percent+label')
fig_sexo.update_layout(showlegend=True)

fig_unidade_hopsitalar = px.pie(
    un_hosp,
    values=un_hosp.values,
    names=un_hosp.index,
    title="Unidade Hospitalar",
    hole=0.5,
)
fig_unidade_hopsitalar.update_traces(textposition='outside', textinfo='percent+label')
fig_unidade_hopsitalar.update_layout(showlegend=True)

fig_sitios = px.pie(
    sitios_acometidos,
    values=sitios_acometidos.values,
    names=sitios_acometidos.index,
    title="Sítios acometidos",
    hole=0.5,
)
fig_sitios.update_traces(textposition='outside', textinfo='percent+label')
fig_sitios.update_layout(showlegend=True)


col1, col2 = st.columns([1,1])
col3, col4 = st.columns([1,1])
col5, col6 = st.columns([1,1])
col7, col8 = st.columns([1,1])
col9, col10 = st.columns([1,1])

#col1, col2, col3 = st.columns([1, 1, 1.5])
with col1:
    st.plotly_chart(fig_sexo, use_container_width=True, theme='streamlit')
with col2:
    st.plotly_chart(fig_unidade_hopsitalar, use_container_width=True, theme='streamlit')
with col3:
    st.plotly_chart(fig_sitios, use_container_width=True, theme='streamlit')


#col4, col5, col6 = st.columns([1, 1.5, 1])
#Definir etapas previstas no protocolo
origem_infeccao = db_clean_filtrado['Comunitaria X hospitalar'].value_counts()
atm_1h = db_clean_filtrado['ATB 1h (Bundle)'].value_counts()
lactato_bundle = db_clean_filtrado['Lactato 30 min (Bundle)'].value_counts()
expansao_volemia = db_clean_filtrado['Expansão Volêmica (Bundle)'].value_counts()
hmc_1h = db_clean_filtrado['Hemoculturas (Bundle)'].value_counts()
bundle_com = db_clean_filtrado['Bundle Completo'].value_counts()

fig_origem_infeccao = px.pie(
    origem_infeccao,
    values=origem_infeccao.values,
    names=origem_infeccao.index,
    title="Origem da infecção",
    hole=0.5
)
fig_origem_infeccao.update_traces(textposition='outside', textinfo='percent+label')
fig_origem_infeccao.update_layout(showlegend=True)
with col4:
    st.plotly_chart(fig_origem_infeccao, use_container_width=True, theme='streamlit')

fig_atm = px.pie(
    atm_1h,
    values=atm_1h.values,
    names=atm_1h.index,
    title='ATB em 1 hora',
    hole=0.5,
)
fig_atm.update_traces(textposition='outside', textinfo='percent+label')
fig_atm.update_layout(showlegend=True)
with col5:
    st.plotly_chart(fig_atm, use_container_width=True, theme='streamlit')

fig_lactato = px.pie(
    lactato_bundle,
    values=lactato_bundle.values,
    names=lactato_bundle.index,
    title="Coleta de lactato em 30 min.",
    hole=0.5,
)
fig_lactato.update_traces(textposition='outside', textinfo='percent+label')
fig_lactato.update_layout(showlegend=True)
with col6:
    st.plotly_chart(fig_lactato, use_container_width=True, theme='streamlit')

#col7, col8, col9 = st.columns([1, 1.5, 1])
fig_exp_vol = px.pie(
    expansao_volemia,
    values=expansao_volemia.values,
    names=expansao_volemia.index,
    title='Expansão volêmica',
    hole=0.5
)
fig_exp_vol.update_traces(textposition='outside', textinfo='percent+label')
fig_exp_vol.update_layout(showlegend=True)
with col7:
    st.plotly_chart(fig_exp_vol, use_container_width=True, theme='streamlit')

fig_hmc = px.pie(
    hmc_1h,
    values=hmc_1h.values,
    names=hmc_1h.index,
    title='Hemocultura em 1 hora',
    hole=0.5,
)
fig_hmc.update_traces(textposition='outside', textinfo='percent+label')
fig_hmc.update_layout(showlegend=True)
with col8:
    st.plotly_chart(fig_hmc, use_container_width=True, theme='streamlit')

fig_bundle = px.pie(
    bundle_com,
    values=bundle_com.values,
    names=bundle_com.index,
    title='Bundle completo',
    hole=0.5,
)
fig_bundle.update_traces(textposition='outside', textinfo='percent+label')
fig_bundle.update_layout(showlegend=True)
with col9:
    st.plotly_chart(fig_bundle, use_container_width=True, theme='streamlit')

media_idade = db_clean_filtrado['idade_anos'].mean()
media_idade = round(media_idade,1)
st.markdown(f"<table border='1'><th>Total de atendimentos</th><th>Média de idade</th><tr><td align='center'>{total_atendidos}</td><td align='center'>{media_idade}</td></table>", unsafe_allow_html=True)

idades = db_clean_filtrado['idade_anos'].value_counts().sort_index(ascending=False)
idades = idades.reset_index()
idades.columns = ['Idade', 'Quantidade']
st.header("Idades")
st.bar_chart(idades, x='Idade', y='Quantidade')
#st.bar_chart(idades)

unidade_internacao = db_clean_filtrado['Unidade de Abertura do Protocolo SEPSE Enf'].value_counts()
st.header("Unidade de Internação")
st.write(unidade_internacao)
st.bar_chart(unidade_internacao)

unidade_hospitalar = db_clean_filtrado['UNIDADE HOSPITALAR'].value_counts()
st.header("Unidade Hospitalar")
st.write(unidade_hospitalar)
st.bar_chart(unidade_hospitalar)

#convenio = db_clean_filtrado['Convenio'].value_counts().sort_values(ascending=True)
convenio = db_clean_filtrado['Convenio'].value_counts().sort_values(ascending=True).reset_index()
convenio.columns = ['Convênio', 'Atendimentos']
st.header("Convênios Atendidos")
#st.write(convenio)
fig_convenios = px.bar(
    convenio,
    x='Atendimentos',#convenio.values,
    y='Convênio', #convenio.index,
    orientation='h',
    text='Atendimentos',
    #text=convenio.values,
    #color=convenio.values,
    color='Atendimentos',
    #color_continuous_scale='Plasma',
    labels={
        'x' : 'Número de Atendimentos',
        'y' : 'Convênio'
    }
)
fig_convenios.update_traces(
    textposition='outside',
    textfont=dict(
        size=12,
        family='Arial'
    )
)
fig_convenios.update_layout(
    margin=dict(r=50),
    coloraxis_colorbar=dict(title="Atendimentos")
)
st.plotly_chart(fig_convenios)

st.header("Atendimento por Dia da Semana")
semana = db_clean_filtrado['dia_semana'].value_counts()
st.bar_chart(semana)

sitios = db_clean_filtrado['Um ou mais sítios'].value_counts()
st.header("Sítios")
st.write(sitios)

hemocultura = db_clean_filtrado['Hemoculturas (Bundle)'].value_counts()
st.header("Hemocultura (bundle)")
st.write(hemocultura)

atb = db_clean_filtrado['ATB 1h (Bundle)'].value_counts()
st.header("Atb")
st.write(atb)

lactato = db_clean_filtrado['Lactato 30 min (Bundle)'].value_counts()
st.header("Lactato")
st.write(lactato)

expansao_volemica = db_clean_filtrado['Expansão Volêmica (Bundle)'].value_counts()
st.header("Expansão Volêmica")
st.write(expansao_volemica)

bundle_completo = db_clean_filtrado['Bundle Completo'].value_counts()
st.header("Bundle Completo")
st.write(bundle_completo)

teste = pd.DataFrame({
    'Métrica': ['Média Idade', 'Bundle Completo', 'Convênio'],
    'Valor': [str(media_idade), str(bundle_completo), str(convenio)]
})
