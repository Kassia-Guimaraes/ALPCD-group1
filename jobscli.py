from pyparsing import dict_of
from top_secret import secret
from datasets import import_data, export_csv, request_data
import requests
import typer
import re


app = typer.Typer()


@app.command()
def top():
    return


@app.command()
def search():
    return


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


if __name__ == "__main__":
    app()
