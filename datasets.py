from top_secret import secret
import requests
import csv
from bs4 import BeautifulSoup
import json
def request_data_by_id(header, path, id): #importa dados da pagina com id especifico
    
    url = f"{header}{path}?api_key={secret}&id={id}"  # search caminho para dados específicos

    headers = {'User-agent': 'group1-ALPCD'}

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
             
            try:
                response_json = response.json()  # Converte a resposta para JSON
                return response_json
            
            except json.JSONDecodeError as e:
                print(f"Erro ao tentar decodificar JSON: {e}")
                return None
        else:
            print(f"Erro ao obter dados. Status code: {response.status_code}")
            print("Mensagem de erro:", response.text)
            return None
        
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
        return None
    
def request_data(header, path, search, limit, page):  # faz o import dos dados da página web

    url = f"{header}{path}?api_key={secret}&limit={limit}&page={page}{search}"  # search caminho para dados específicos

    headers = {'User-agent': 'group1-ALPCD'}
    payload = {}

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erro {response.status_code} - {response.text}")
            return None
        
    except requests.exceptions.RequestException as e:
        print(f"Erro na requisição: {e}")
        return None


def request_html(header, path): #busca dados de uma página web
   
    if path:
        url = f'{header}{path}'
    else:
        url = f'{header}'

    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Fire-fox/98.0", 
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8", "Accept-Language": "en-US,en;q=0.5",
               "Accept-Encoding": "gzip, deflate", 
               "Connection": "keep-alive", 
               "Upgrade-Insecure-Requests": "1", 
               "Sec-Fetch-Dest": "document",
               "Sec-Fetch-Mode": "navigate", 
               "Sec-Fetch-Site": "none", 
               "Sec-Fetch-User": "?1",
                "Cache-Control": "max-age=0"}
    payload = {}

    try:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "lxml")
            return soup
        else:
            return response.status_code
        
    except requests.exceptions.RequestException as e:
        return e


# retorna uma lista com todos os resultados
def import_data(header, path, search, limit, total_data):

    # sabe quantas páginas são necessárias para chegar no total de dados
    last_page = int(total_data/limit)+1
    rest = total_data
    results = []

    for i in range(1, last_page+1):

        if (i == last_page):  # condição de paragem; página em pesquisa ser igual a última página que queremos os dados
            data = request_data(header, path, search=search,
                                limit=rest, page=i)['results']
            results += data  # adiciona os dados obtidos

            return results

        # vai buscar à página web os dados
        data = request_data(header, path, search, limit, page=i)['results']
        results += data

        rest -= limit  # retira a quantidade do limite das páginas importadas


def export_csv(name, dicts, columns_name):
    with open(f"{name}.csv", 'w', newline='', encoding='utf-8') as csvfile:

        # inicializar o DictWriter com os nomes das colunas
        writer = csv.DictWriter(csvfile, fieldnames=columns_name)

        writer.writeheader()  # escrever o cabeçalho

        for dic in dicts:
            writer.writerow(dic)
