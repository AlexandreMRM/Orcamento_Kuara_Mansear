from google.oauth2 import service_account
import gspread
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import date

#### ATUALIZAR O ARQUIVO DAS BIBLIOTECAS
#pip freeze > requirements.txt

###COMMIT no terminal
#git add main.py
#git commit -m "Descrição das mudanças realizadas"
#git push origin main

def convert_to_float(value):
    try:
        # Remover pontos usados como separadores de milhar e substituir a vírgula por ponto
        value = value.replace('.', '').replace(',', '.')
        return float(value)
    except ValueError:
        return None  

nome_credencial = st.secrets["CREDENCIAL_SHEETS"]
#credencial = json.loads(nome_credencial)

credentials = service_account.Credentials.from_service_account_info(nome_credencial)
scope = ['https://www.googleapis.com/auth/spreadsheets']
credentials = credentials.with_scopes(scope)
client = gspread.authorize(credentials)

# Abrir a planilha desejada pelo seu ID
spreadsheet = client.open_by_key('1Zlih7-JKNwBhpXOiefUyhwbQyzt7O3TsDJhK7peWY8w')

# Selecionar a primeira planilha
sheet = spreadsheet.worksheet("BD - Geral")

sheet_data = sheet.get_all_values() # Carrega todos os valores que tem na planilha google e aba BD Geral

# Converter para um DataFrame pandas
df = pd.DataFrame(sheet_data)

# Definir a primeira linha como cabeçalho (opcional)
df.columns = df.iloc[0]
df = df.drop(0).reset_index(drop=True)
df['Data_venc'] = pd.to_datetime(df['Data_venc']) #Convertendo Data_venc do BD em Data
#print(df['Valor_Depto'].head())  # Para depuração
df['Valor_Depto'] = df['Valor_Depto'].apply(convert_to_float)


#============================================
st.set_page_config(layout='wide')
st.markdown("""
            <style>
            .stApp{
                background-color: #000000;
            }
            h1, h2, h3, .stMarkdown, .stRadio label, .stSelectbox label, .stDateInput label{
                color: white;
            }
            <style>
            """, unsafe_allow_html=True)
st.title('Despesas - Kuara')
st.write('Aqui você pode visualizar as receitas e despesas do Acumuladas, mês a mês.')

col1, col2 = st.columns([1, 5])

with col1:
    col1_1, col1_2 = st.columns(2)
    with col1_1:
        data_inicial = st.date_input('Data Inicio', value=date(2024,1,1), format='DD/MM/YYYY')
    with col1_2:
        data_final = st.date_input('Data Fim', value=date(2025,1,1), format='DD/MM/YYYY')
    
    select_depart = st.selectbox(
        'Selecione o Departamento',
        options=['Todos', 'Kuara', 'Mansear'],
        index=1
    )

    if select_depart == 'Todos':
        df_filtrado = df[(df['Data_venc'].dt.date >= data_inicial) & (df['Data_venc'].dt.date <= data_final)]
    else:
        df_filtrado = df[(df['Data_venc'].dt.date >= data_inicial) & (df['Data_venc'].dt.date <= data_final) & (df['Desc_Depto']== select_depart)]

df_Despesas = df_filtrado.groupby(['Mes', 'Ano'])['Valor_Depto'].sum().reset_index()
df_Despesas.rename(columns={'Valor_Depto': 'Despesas'}, inplace=True)
df_Despesas['Mes'] = df_Despesas['Mes'].astype(int)
df_Despesas = df_Despesas.sort_values(by=['Mes', 'Ano'])
df_Despesas['Mes_Ano'] = df_Despesas['Mes'].astype(str).str.zfill(2) + '/' + df_Despesas['Ano'].astype(str)


with col2:
    fig = px.bar(df_Despesas, 
                x='Mes_Ano', 
                y='Despesas', 
                title='Despesas Acumuladas',
                #color='Descricao',
                text='Despesas',
                labels={'Despesas':'Soma de Valor_Depto', 'Mes' : 'Mes'},
                color_discrete_sequence=['Black']
                )
    fig.update_traces(texttemplate='R$ %{text:.2f}', textposition='outside')
    fig.update_layout(paper_bgcolor='Gray', #Cor do fundo do grafico
                      plot_bgcolor='Gray', #Cor da area de plotagem
                      font=dict(color='Black'), #Cor do texto das legendas e label
                      title_font=dict(color='Black'), #Cor do texto do titulo
                      xaxis_title_font=dict(color='Black'), #Cor do titulo do eixo x
                      yaxis_title_font=dict(color='Black'), #Cor do titulo do eixo y
                      )


    st.subheader('Grafico acumulado')
    st.plotly_chart(fig)
