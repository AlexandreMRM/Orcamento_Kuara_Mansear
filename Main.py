from google.oauth2 import service_account
import gspread
import pandas as pd
import plotly.express as px
import streamlit as st

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
st.title('Despesas - Kuara')
st.write('Aqui você pode visualizar as receitas e despesas do Acumuladas, mês a mês.')

col1, col2 = st.columns([1, 3])

with col1:
    data_inicial = st.date_input('Data Inicio', df['Data_venc'].min().date())
    data_final = st.date_input('Data Fim', df['Data_venc'].max().date())
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
df_Despesas['Mes_Ano'] = df_Despesas['Mes'].astype(str) + '/' + df_Despesas['Ano'].astype(str)


with col2:
    fig = px.bar(df_Despesas, 
                x='Mes_Ano', 
                y='Despesas', 
                #color='Descricao',
                text='Despesas',
                labels={'Despesas':'Soma de Valor_Depto', 'Mes' : 'Mes'},
                color_discrete_sequence=['black']
                )


    st.subheader('Grafico acumulado')
    st.plotly_chart(fig)
