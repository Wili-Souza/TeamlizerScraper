import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta, date
import pandas as pd

#-- Meu imports
from exportar import exportar_df

#------------ Inicializações
data = { # -> dicionário para data frame 
    'tipo': [],
    'empresa': [],
    'impacto':[],
    'fonte': [],
    'data': [],
    'descrição': []
}
number_elements = 0
finished = False

# ----------- Filtros --------------
#formato: #s_covid_reasons = ['Comunicado oficial', 'Despedimentos', 'Não renovações', 'Dispensa período experiência']
s_company_names = []
s_covid_reasons = []

while not finished:
    try:
        html = requests.get('https://pt.teamlyzer.com/load?c={}' .format(number_elements + 1))
    except:
        print('Erro ao conectar-se com a página')
        break

    #verificar se acabaram as requests // converter de jason para dict
    if html.text.strip()[:2] != '[]':
        list_dicts = json.loads(html.text)
    else:
        finished = True
        break

    for dic in list_dicts:
        #Se for um dos números inteiros, passa (só queremos dicts)
        if isinstance(dic, int):
            continue

        #filtrando
        if len(s_covid_reasons) > 0 or len(s_company_names) > 0: #Se houver parâmetros de pesquisa
            #Se não for um resultado
            if dic['covid_reason'] not in s_covid_reasons and dic['company_name'] not in s_company_names: 
                continue
        
        number_elements += 1
        
        #Tratando o link (originalmente em tag ou texto)
        tag_link = BeautifulSoup(dic['info_source'], 'html.parser')
        try:
            tag_link = tag_link.select_one('a').get('href')
        except:
            tag_link = str(tag_link)
        
        #Tratamento de data (há X Horas / há X dias)
        date_post = dic['ts']
        separeted_date = date_post.split(' ')
        
        if 'dia' in separeted_date[2]:
            if 'um' in separeted_date[1]:
                final_date = date.today() + timedelta(days=-1) # -1 dia
            
            else:
                final_date = date.today() + timedelta(days=-int(separeted_date[1]))
        
        elif 'hora' in separeted_date[2]:
            if 'uma' in separeted_date[1]:
                final_date = date.today() # -1 dia

            elif int(separeted_date[1]) > datetime.now().hour:
                final_date = date.today() + timedelta(days=-1)
        
            else:
                final_date = date.today()
        
        elif 'mês' in separeted_date[2] or 'mes' in separeted_date[2]:
            if 'um' in separeted_date[1]:
                final_date = date.today() + timedelta(days=-30)
            
            else:
                final_date = date.today() + timedelta(days=-int(separeted_date[1])*30)

        final_date = final_date .strftime('%d/%m/%Y')
        print(final_date)

        data['tipo'].append(dic['covid_type'])
        data['empresa'].append(dic['company_name'])
        data['impacto'].append(dic['covid_reason'])
        data['fonte'].append(tag_link)
        data['data'].append(final_date)
        data['descrição'].append(dic['rumor'])

    '''last_number_elements = number_elements
    number_elements = len(data['empresa'])

    #Se a última página n teve elementos
    if last_number_elements == number_elements:
        finished = True'''
    
    #Setado para pegar somente 10 resultados (todos -> retirar condicional)
    if len(data['empresa']) > 10:
        print('pegou 10')
        finished = True
    

if len(data['empresa']) == 0: 
    print('Nenhum resultado encontrado.')

elif len(data['empresa']) > 0: #se algum resultado for capturado

        # ---- Salvando resultado
    df = pd.DataFrame(data, columns = ['tipo', 'empresa', 'fonte', 'impacto', 'data', 'descrição']) #-> criando dataframe

        # ---- Exportando para excel(xlsx) e/ou csv
    exportar_df(df, 'xlsx', 'csv', wb='T')

print('FIM DA EXECUÇÃO')