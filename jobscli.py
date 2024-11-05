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

    search_salary = ['([e|E]xtra[s]*)*', '[cC]ompetitiv[oe]*'] #palavras que geralmente aparecem juntamente com o salário

    try:
        #total_data = request_data('https://api.itjobs.pt/', path='job/search.json', limit=1, page=1)['total'] # num dados que existem 

        data_list = import_data('https://api.itjobs.pt/', path='job/list.json', limit=100, total_data=100) # lista com todos os resultados da página

        # Itera sobre cada item da lista de dados
        for data in data_list:
            
            try: # testa com o job_id dado pelo utilizador
                
                if data.get('wage', ''): #se 'wage' diferente de NULL
                    print(data.get('wage', ''))
                    return data.get('wage', '')
        

                for expression in search_salary:
                    pattern = fr'[^.<>!?]*?\b{expression}[s|S]al[á|a]r(?:io|ial|iais|y)*\b[^.<>]*?[.<]' #condição para início e fim das frases
                    regex = re.compile(pattern)

                    # Pesquisa a primeira frase no texto que corresponde ao padrão
                    match = regex.search(data.get('body',''))
                    if match:
                        print(match.group(0),'\n\n')
                        return match.group(0)
                
                print('Nenhum dado sobre salário encontrado')
                return 'Nenhum dado sobre salário encontrado'
                    
                
            except:
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
