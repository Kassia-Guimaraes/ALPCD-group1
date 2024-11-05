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
        # total_data = request_data('https://api.itjobs.pt/', path='job/search.json', limit=1, page=1)['total'] # num dados que existem
        data_list = import_data('https://api.itjobs.pt/', path='job/list.json', limit=100, total_data=500) # lista com todos os resultados da página

        # Itera sobre cada item da lista de dados
        for data in data_list:
            
            if data.get('id','') == job_id: # testa com o job_id dado pelo utilizador
                
                if data.get('wage', ''): #se 'wage' diferente de NULL
                    print('€',data.get('wage', ''))
                    return data.get('wage', '')
        

                for expression in search_salary:
                    
                    match = re.search(fr'[^.<>!?;^|]*?\b{expression}[s|S]al[á|a]r[io|ial|iais|y]*\b[^.<>]*?(?=[.<;:!?^|])',data.get('body','')) #pesquisa a primeira frase no texto que corresponde ao padrão

                    if match:
                        print(match.group(0))
                        return match.group(0)
                    
                    match = re.search(fr'[^.<>!?;^|]*?\b[rR]emunera[çct][ion|ions|õe|ão][s]**\b[^.<>]*?(?=[.<;:!?^|])',data.get('body',''))
                    if match:
                        print(match.group(0))

                
                print('Nenhum dado sobre salário encontrado')
                return 'Nenhum dado sobre salário encontrado'
                    
        print('JobID não encontrado, por favor verifique se o código da vaga está correto.') #caso passe todo o ciclo e não encontre o job_id 
        return 'JobID não encontrado'  

    except Exception as e:
        print(f'Erro: {e}')
        return e


@app.command()
def skills(skills: list[str], start_date: str, end_date: str):

    # Tratamento dos dados das skills
    skills = str(skills)
    skills = re.findall(r"[A-Za-z0-9]+", skills)

    # Tratamento das datas
    start_day, start_month = processing_data(start_date)
    end_day, end_month = processing_data(end_date)

    # Verifica se as datas são válidas
    if start_day is None or end_day is None:
        return print("Data inválida!!")

    res = request_data('https://api.itjobs.pt/', 'job/list.json', 1, 1)
    total_data = res["total"]

    datasets = import_data('https://api.itjobs.pt/',
                           'job/list.json', 100, int(total_data))

    list_company = []

    for data in datasets:
        body = data["body"]
        print(data)

    all_skills_found = True
    for skill in skills:
        if not re.search(rf"\b{skill}\b", body, re.IGNORECASE):
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


def processing_data(date):

    match = re.match(
        r"((0[1-9]|[12][0-9]|3[01])[-:/ ](0[13578]|1[02])[-:/ ]2024)|"

        r"((0[1-9]|[12][0-9]|30)[-:/ ](0[469]|11)[-:/ ]2024)|"

        r"((0[1-9]|[12][0-9])[-:/ ](02)[-:/ ]2024)", date)

    if match:
        date = re.split(r"[-:/ ]", date)
        # Extrai os grupos correspondentes
        day, month, year = date
        # Criação de data em formato universal
        # date_universal = f"{year}-{month}-{day}"
        return day, month

    else:
        match2 = re.match(
            r"(2024[-:/ ](0[13578]|1[02])[-:/ ](0[1-9]|[12][0-9]|3[01]))|"

            r"(2024[-:/ ](0[469]|11)[-:/ ](0[1-9]|[12][0-9]|30))|"

            r"(2024[-:/ ](02)[-:/ ](0[1-9]|[12][0-9]))", date)

        if match2:
            date = re.split(r"[-:/ ]", date)
            # Extrai os grupos correspondentes
            year, month, day = date
            # Criação de data em formato universal
            # date_universal = f"{year}-{month}-{day}"
            return day, month
        else:
            return None, None


if __name__ == "__main__":
    app()
