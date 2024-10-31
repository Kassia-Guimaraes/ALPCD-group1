from pyparsing import dict_of
from top_secret import secret
from datasets import import_data, export_csv, request_data
import requests
import typer
import re
import json
import time

app = typer.Typer()

def fetch_jobs_from_api(header, path, limit, total_data):
    response = requests.get(f"{header}{path}", params={"limit": limit, "total_data": total_data})
    response.raise_for_status()  # Levanta uma exceção para códigos de status HTTP 4xx/5xx
    return response.json()

@app.command()
def top(n: int):
    """
    Lista os N trabalhos mais recentes publicados pela itjobs.pt em formato JSON.

    Args:
        n (int): Número de trabalhos a listar.
    """
    # Configurações para a API
    try:
    # Configurações para a API
        header = "https://api.itjobs.pt/"
        path = "job/list.json"

                # Tentativa de requisição com retentativas e atraso exponencial
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                # Importar dados
                print("Tentando importar dados da API...")
                jobs = import_data(header, path, limit=n, total_data=n)
                if jobs is not None:
                    break
            except requests.exceptions.RequestException as e:
                wait_time = 2 ** attempt  # Atraso exponencial
                print(f"Erro ao fazer a requisição: {e}. Tentando novamente em {wait_time} segundos...")
                time.sleep(wait_time)
        else:
            print("Falha ao obter dados após várias tentativas.")
            return

        # Verificar se os dados foram importados corretamente
        if jobs is None:
            print("Erro: Nenhum dado foi retornado pela função import_data.")
            return
        
        # Exibir os dados em formato JSON
        print(json.dumps(jobs, indent= 4, ensure_ascii= False))
        
        return jobs

    except requests.exceptions.RequestException as e:
        print(f"Erro ao fazer a requisição: {e}")
    
    except json.JSONDecodeError as e:
        print(f"Erro ao decodificar JSON: {e}")
    
    except Exception as e:
        print(f"Ocorreu um erro inesperado: {e}")
        
        
@app.command()
def search(location: str, company_name: str, n: int):
    """
    Lista todos os trabalhos do tipo full-time publicados por uma determinada empresa numa determinada localidade.

    Args:
        location (str): Localidade dos trabalhos.
        company_name (str): Nome da empresa.
        n (int): Número de trabalhos a listar.
    """
    header = "https://api.itjobs.pt/"
    path = "job/list.json"

    jobs = import_data(header, path, limit= n, total_data= n)
    
    if jobs is None:
        try:
            print("Tentando importar dados da API...")
            jobs = fetch_jobs_from_api(header, path, limit= 1000, total_data= 1000)  # Obtém um número maior de trabalhos para filtrar
            
            
        except requests.exceptions.RequestException as e:
            print(f"Erro ao fazer a requisição: {e}.")
            
        except json.JSONDecodeError as e:
            print(f"Erro ao decodificar JSON: {e}.")
                
        except Exception as e:
            print(f"Ocorreu um erro inesperado: {e}.")

    # Filtrar trabalhos pelo tipo, empresa e localidade
    filtered_jobs = [
        job for job in jobs
        if any(loc['name'].lower() == location.lower() for loc in job['locations'])
        and job['company']['name'].lower() == company_name.lower()
        and any(t['name'].lower() == 'full-time' for t in job['types'])
    ][:n]

    print(json.dumps(filtered_jobs, indent=4, ensure_ascii=False))
    return filtered_jobs

""" 
@app.command()
def salary(job_id: int):
    try:
        #total_data = request_data('https://api.itjobs.pt/', path='job/search.json', limit=1, page=1)['total'] # num dados que existem 

        data_list = import_data('https://api.itjobs.pt/', path='job/list.json', limit=100, total_data=5) # lista com todos os resultados da página

        if data_list is None: # se data_list é None, imprime uma mensagem e encerra a função
            print("Erro: Nenhum dado retornado.")
            return 'Nenhum dado retornado'

        # Itera sobre cada item da lista de dados
        for data in data_list:

            # Verifica se 'id' e 'wage' estão no dicionário
            if ('id' in data) and ('wage' in data) and (data['id'] == job_id):
                print('data[id]:', data['id'])
                print('wage:', data['wage'])
                
                # Verifica se 'wage' tem valor
                if data['wage']:

                    print("Wage:", data['wage'])

                return data['wage']

        # Caso não encontre o job_id
        print('JobID não encontrado.')
        return 'JobID não encontrado'

    except Exception as e:
        print(f'Erro: {e}')
        return e


@app.command()
def skills(skills: list[str]):
    skills = [skill.strip("[]") for skill in skills]
    res = request_data('https://api.itjobs.pt/',
                       'job/list.json', 1, 1)
    total_data = res["total"]

    datasets = import_data('https://api.itjobs.pt/',
                           'job/list.json', 100, int(total_data))

    list_company = []

    for data in datasets:
        body = data["body"]
        # print(data)

        all_skills_found = True
        for skill in skills:
            pattern = rf"\b{skill}\b"

            if not re.search(pattern, body, re.IGNORECASE):
                all_skills_found = False
                break

        if all_skills_found:
            company_name = data["company"]["name"]
            list_company.append((company_name))

    dict_companies = {"Empresas": list_company}

    if not dict_companies["Empresas"]:
        print("Nenhuma empresa encontrada que requer a skill.")
    else:
        print(dict_companies)
 """

if __name__ == "__main__":
    app()
