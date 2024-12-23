from datasets import import_data, export_csv, request_data, request_data_by_id, request_html
from datetime import datetime
import typer
import re
import json
from auxFunctions import showVacancies, askUser, findZone
import requests
from bs4 import BeautifulSoup

app = typer.Typer()


@app.command(help="Procura o trabalho pelo ID da vaga")
def fetch_job_details(job_id):
    jobData = request_data_by_id(
        "https://api.itjobs.pt/", "job/get.json", job_id)

    print("Dados do Job:", jobData["company"]["name"])
    company_name = jobData['company']['name']
    company_path = company_name.replace(' ', '-')

    # data= request_html('https://www.ambitionbox.com/overview/', f"{company_path}-overview")
    data = request_html(
        'https://www.ambitionbox.com/overview/', "capgemini-overview")
    return data


def calc_salary(data_list, job_id):
    # palavras que geralmente aparecem juntamente com o salário
    search_salary = ['([e|E]xtra[s]*)*', '[cC]ompetitiv[oe]*']

    try:

        # Itera sobre cada item da lista de dados
        for data in data_list:

            if data.get('id', '') == int(job_id):  # testa com o job_id dado pelo utilizador

                if data.get('wage', ''):  # se 'wage' diferente de NULL
                    # print('€', data.get('wage', ''))
                    return data.get('wage', '')

                for expression in search_salary:

                    # pesquisa a primeira frase no texto que corresponde ao padrão
                    match = re.search(
                        fr'[^.<>!?;^|]*?\b{expression}[s|S]al[á|a]r[io|ial|iais|y]*\b[^.<>]*?(?=[.<;:!?^|])', data.get('body', ''))

                    if match:
                        # print(match.group(0))
                        return match.group(0)

                    match = re.search(
                        fr'[^.<>!?;^|]*?\b[rR]emunera[çct][ion|ions|ões|ão]*\b[^.<>]*?(?=[.<;:!?^|])', data.get('body', ''))
                    if match:
                        # print(match.group(0))
                        return match.group(0)

                # print('Nenhum dado sobre salário encontrado')
                return 'Nenhum dado sobre salário encontrado'

        # caso passe todo o ciclo e não encontre o job_id
        # print('JobID não encontrado, por favor verifique se o código da vaga está correto.')
        return 'JobID não encontrado'

    except Exception as e:
        print(f'Erro em clacular o salário: {e}')
        return None


@app.command(help='Encontrar as publicações de emprego mais recentes')
def top(n: int = typer.Argument('número de vagas')):

    # Lista os N trabalhos mais recentes publicados pela itjobs.pt

    try:
        datasets = import_data(
            "https://api.itjobs.pt/", "job/list.json", search=None, limit=100, total_data=n)

        jobs = []

        for vacancy in datasets:
            jobs.append(dict_csv(vacancy))

        # Mostra as vagas formatadas
        showVacancies(jobs, 35)

        # Pergunta ao usuário se deseja salvar a pesquisa
        askUser(jobs)

        # Retornando as vagas formatadas como dicionário
        return jobs

    except Exception as e:
        print(f"Erro: {e}")


@app.command(help='Selecionar todos os trabalhos do tipo full-time, publicados por uma determinada empresa, em uma determinada localidade')
def search(location: str = typer.Argument('nome do distrito'), company_name: str = typer.Argument('nome da empresa'), n: int = typer.Argument('número de vagas')):
    try:
        if not isinstance(n, int):
            print("Erro: o número de vagas deve ser um valor inteiro.")
            return

        # Procura pelo ID da localização
        findLocal = request_data(
            'https://api.itjobs.pt/', path='location/list.json', search=None, limit=100, page=1)['results']
        idLocal = None
        for local in findLocal:
            if location == local['name']:
                idLocal = local['id']
                break

        if not idLocal:
            print(f"Localização '{location}' não encontrada.")
            return

        # Procura pelo ID da empresa

        companys = request_data(
            'https://api.itjobs.pt/', path='company/search.json', search=None, limit=1, page=1)['total']
        findCompany = import_data(
            'https://api.itjobs.pt/', path='company/search.json', search=None, limit=100, total_data=companys)

        idCompany = None
        for company in findCompany:
            if company_name == company['name']:
                idCompany = company['id']
                break

        if not idCompany:
            print(f"Empresa '{company_name}' não encontrada.")
            return

        # Busca as vagas de emprego
        datasets = import_data('https://api.itjobs.pt/', path='job/list.json', search=f'&location={
                               idLocal}&company={idCompany}&type=1', limit=n, total_data=n)

        # Limita as vagas de acordo com o número solicitado
        jobs = []

        for vacancy in datasets[:n]:
            jobs.append(dict_csv(vacancy))

        # Exibe as vagas formatadas
        showVacancies(jobs, 32)

        # Pergunta ao usuário se deseja salvar a pesquisa realizada
        askUser(jobs)

        return jobs

    except ValueError as ve:
        print(f"Erro de Valor: {ve}")

    except Exception as e:
        print(f"Erro: {e}")


@app.command(help='Encontrar todas as vagas disponíveis de uma empresa')
def company(company_name: str = typer.Argument('ID ou nome', help='Nome ou ID da empresa'),
            export: bool = typer.Option(False, "--export", "-e", help="Exportar os resultados para um arquivo CSV")):

    try:
        total_data = request_data('https://api.itjobs.pt/', path='job/list.json',
                                  # num dados que existem
                                  limit=1, page=1, search=None)['total']
        # lista com todos os resultados da página
        data_list = import_data('https://api.itjobs.pt/',
                                path='job/list.json', limit=100, total_data=total_data, search=None)

        jobs = []
        csv_jobs = []

        for data in data_list:

            try:  # se a pessoa adicionar o id da empresa
                if (data.get('companyId', '') == int(company_name)):
                    jobs.append(data.get('title', ''))
                    csv_jobs.append(dict_csv(data))

            except:
                # faz a busca sem considerar as letras maiúsculas e/ou minúsculas
                match = re.search(fr'\b{company_name}\b',
                                  data['company']['name'], re.IGNORECASE)

                if match:  # se encontrar o nome da companhia
                    jobs.append(data.get('title', ''))
                    csv_jobs.append(dict_csv(data))

        # Exporta os resultados para um CSV
        export_csv("company", csv_jobs)

        if jobs:
            print(jobs)

            # Salvar para CSV
            if export:
                filename = "company"
                export_csv(filename, csv_jobs)

            return jobs

        print(f'Nenhuma vaga encontrada da empresa {company_name}')

    except Exception as e:
        print(f'Erro: {e}')
        return e


@app.command(help='Buscar todas as vagas disponíveis por distrito')
def locality(district: str = typer.Argument('nome do distrito', help='Nome ou ID da localidade que deseja pesquisar a vaga'),
             export: bool = typer.Option(False, "--export", "-e", help="Exportar os resultados para um arquivo CSV")):

    try:
        total_data = request_data('https://api.itjobs.pt/', path='job/list.json',
                                  # num dados que existem
                                  limit=1, page=1, search=None)['total']
        # lista com todos os resultados da página
        data_list = import_data('https://api.itjobs.pt/',
                                path='job/list.json', limit=100, total_data=total_data, search=None)

        jobs = []
        csv_jobs = []

        for data in data_list:

            try:  # se a pessoa adicionar o id da localidade
                for local in data.get('locations', ''):
                    if (local['id'] == int(district)):
                        jobs.append(data.get('title', ''))
                        csv_jobs.append(dict_csv(data))

            except:
                for local in data.get('locations', ''):
                    # faz a busca sem considerar as letras maiúsculas e/ou minúsculas
                    match = re.search(
                        fr'\b{district}\b', local['name'], re.IGNORECASE)

                    if match:  # se encontrar o nome da companhia
                        if data.get('title', '') not in jobs:
                            jobs.append(data.get('title', ''))
                        csv_jobs.append(dict_csv(data))

        if jobs:
            print(jobs)

            # Salvar para CSV
            if export:
                filename = "contract"
                export_csv(filename, csv_jobs)

            return jobs

        # se a lista dos jobs estiver vazia
        print(f'Nenhuma vaga encontrada em {district}')
        return jobs

    except Exception as e:
        print(f'Erro: {e}')
        return e


@app.command(help="Pesquisar salário de uma vaga de emprego específica")
def salary(job_id: int = typer.Argument('Número inteiro', help='ID da vaga para pesquisa de salários.')):

    total_data = request_data('https://api.itjobs.pt/', path='job/search.json',
                              # num dados que existem
                              search=None, limit=1, page=1)['total']
    data_list = import_data('https://api.itjobs.pt/', path='job/list.json', limit=100,
                            total_data=total_data, search=None)  # lista com todos os resultados da página

    print(calc_salary(data_list, int(job_id)))


@app.command(help='Mostrar quais os trabalhos que requerem uma determinada lista de skills, num determinado período de tempo')
def skills(skills: list[str] = typer.Argument(help='Skills que deseja pesquisar, apenas separadas por vírgulas'),
           start_date: str = typer.Argument('dd-mm-aaaa', help='Data inicial da pesquisa'),
           end_date: str = typer.Argument('dd-mm-aaaa', help='Data final da pesquisa'),
           export: bool = typer.Option(False, "--export", "-e", help="Exportar os resultados para um arquivo CSV")):

    try:
        # Lista de skills possiveis
        list_skills = [
            # Linguagens de Programação
            "python", "java", "javascript", "c#", "ruby", "php",
            "swift", "go", "kotlin", "rust", "typescript", "scala",
            "perl", "c", "c++", "dart",

            # Desenvolvimento Web
            "html", "css", "react", "angular", "vue.js", "bootstrap",
            "node.js", "express", "jquery", "sass", "less",

            # Desenvolvimento de Aplicativos
            "flutter", "react native", "ionic", "xamarin",

            # Banco de Dados
            "sql", "nosql", "mongodb", "postgresql", "mysql",
            "sqlite", "oracledb", "redis", "firebase",

            # DevOps e Infraestrutura
            "docker", "kubernetes", "aws", "azure",
            "terraform", "ansible", "jenkins", "git", "ci/cd",

            # Ciência de Dados e Machine Learning
            "data science", "data analyst", "tensorflow",
            "pytorch", "pandas", "numpy", "r", "matplotlib",
            "scikit-learn", "keras", "statistics", "ciência de dados",
            "estatística", "databases", "bases de dados",

            # Metodologias e Ferramentas
            "agile", "scrum", "kanban", "devops", "github", "bitbucket",
            "jira", "trello", "confluence",

            # Segurança da Informação
            "cybersecurity",

            # Outras Skills Relevantes
            "blockchain", "iot", "ar/vr", "ui/ux", "seo",
            "api", "development", "graphql", "performance",
            "analytics projects", "excel",

            # Soft Skills
            "communication", "comunicação", "teamwork",
            "adaptability", "leadership", "trabalho em equipa",
            "espirito critico", "proatividade", "espirito de equipa",
            "criatividade",

            # Linguas
            "inglês", "françes", "espanhol", "português", "english",

            # Licenciaturas
            "engenharia informática", "ciência de dados", "data engineer",
            "software engineer", "engenharia de software"
        ]

        # Tratamento das skills
        skills = re.split(r',', skills[0])

        for skill in skills:
            if skill.lower() not in list_skills:
                return print(f"{skill} não é compatível com uma skill!")

        # Tratamento das datas
        start_date, end_date = map(processing_data, (start_date, end_date))

        # Verifica se as datas são válidas
        if start_date is None or end_date is None:
            return print("Data inválida!!")

        # Requisição dos dados
        res = request_data('https://api.itjobs.pt/',
                           'job/list.json', search=None, limit=1, page=1)
        total_data = res["total"]

        datasets = import_data('https://api.itjobs.pt/',
                               'job/list.json', search=None, limit=100, total_data=int(total_data))

        # Inicialização do processo de captura das empresas que requerem as skills naquele período
        list_jobs = {}
        csv_jobs = []

        for data in datasets:
            body = data["body"]
            update_date = data["updatedAt"]
            if update_date is None:
                update_date = data["publishedAt"]

            update_date = re.sub(
                r"(\d{4}-\d{2}-\d{2})( \d{2}:\d{2}:\d{2})", r"\1", update_date)

            update_datetime = datetime.strptime(update_date, "%Y-%m-%d")

            # Verifica se a data de publicação está no intervalo
            if start_date <= update_datetime <= end_date:

                # Verifica se todas as skills estão presentes no body do job
                all_skills_found = True
                for skill in skills:
                    if not re.search(rf"\b{skill}\b", body, re.IGNORECASE):
                        all_skills_found = False
                        break

                if all_skills_found:
                    company = data["company"]["name"]
                    id_job = data["id"]

                    # Verifica se a empresa já existe na lista

                    if company in list_jobs:
                        list_jobs[company].append(id_job)

                    # Se não existir adiciona o dicionario respetivo daquela empresa
                    else:
                        list_jobs[company] = [id_job]

                    # Formatar o dicionário para exportar para CSV
                    csv_jobs.append(dict_csv(data))

        if not list_jobs:
            print("Nenhuma empresa encontrada que requer a(s) skill(s).")
        else:
            # Imprimindo as chaves em azul e os valores em verde
            for chave, valor in list_jobs.items():
                print(f"'\033[1;32m{chave}\033[0m': {valor}")

            # Salvar para CSV
            if export:
                filename = "skills"
                export_csv(filename, csv_jobs)

    except Exception as e:
        print(f'Erro: {e}')
        return e


@app.command(help='Mostrar quais os trabalhos de uma detreminada localidade, que oferecem um determinado contrato')
def contract(locality: str = typer.Argument(help='Nome do distrito'),
             contract: str = typer.Argument(
                 help='Tipo de contrato que deseja pesquisar'),
             export: bool = typer.Option(False, "--export", "-e", help="Exportar os resultados para um arquivo CSV")):

    try:
        # Procura pelo ID da localização
        total_local = request_data('https://api.itjobs.pt/', path='location/list.json',
                                   search=None, limit=100, page=1)['results']
        id_local = None

        for local in total_local:
            if re.search(rf"\b{locality}\b", local["name"], re.IGNORECASE):
                id_local = local['id']
                break

        if not id_local:
            print(f"Localização '{locality}' não encontrada.")
            return

        dict_contracts = {
            "estágio académico": int(5),
            "prestação de serviços": int(4),
            "estágio profissional": int(3),
            "contrato sem termo": int(2),
            "contrato a termo": int(1)
        }

        if contract.lower() in dict_contracts:
            id_contract = dict_contracts[contract]
        else:
            print(f"{contract} não identificado como contrato.")

        # Busca as vagas de emprego
        num_datasets = request_data('https://api.itjobs.pt/', path='job/list.json', search=f'&location={
            id_local}&contract={id_contract}', limit=1, page=1)["total"]

        datasets = import_data('https://api.itjobs.pt/', path='job/list.json', search=f'&location={
                               id_local}&contract={id_contract}', limit=100, total_data=int(num_datasets))

        csv_jobs = []

        for data in datasets:
            data = dict_csv(data)
            print(f"\033[1;35mTítulo:\033[0m {data['Título']}")
            print(f"\033[1;35mEmpresa:\033[0m {data['Empresa']}")
            print(f"\033[1;35mData de Publicação:\033[0m {
                  data['Data de Publicação']}")
            print("-" * 80)

            csv_jobs.append(data)

        # Salvar para CSV
            if export:
                filename = "contract"
                export_csv(filename, csv_jobs)

    except Exception as e:
        if str(e) == "'results'":
            print("Sem publicações com essas características!")
            return
        print(f'Erro: {e}')
        return e


def dict_csv(data):
    # Tratamento da data de publicação
    update_date = data["updatedAt"]
    if update_date is None:
        update_date = data["publishedAt"]

    update_date = re.sub(
        r"(\d{4}-\d{2}-\d{2})( \d{2}:\d{2}:\d{2})", r"\1", update_date)

    # Tratamento da descrição (retirar paragrafos,etc)
    if "description" in data["company"]:
        description = re.sub(r"<[^>]+>|\n+|\r|•", "",
                             data["company"]["description"])
    else:
        description = "Descrição não mencionada!"

        # Verifique as localizações
    locations = []
    if "locations" in data:
        for location in data["locations"]:
            locations.append(location["name"])
    else:
        locations = "Localização não mencionada!"

    # Dicionário para guardar em csv
    csv_jobs_info = {
        "Título": data["title"],
        "Empresa": data["company"]["name"],
        "Descrição": description,
        "Data de Publicação": update_date,
        "Salário": calc_salary([data], data["id"]),
        "Localização": locations,
    }

    return csv_jobs_info


def processing_data(date):

    match = re.match(
        r"((0[1-9]|[12][0-9]|3[01])[-:/ ](0[13578]|1[02])[-:/ ](202[3-4]))|"

        r"((0[1-9]|[12][0-9]|30)[-:/ ](0[469]|11)[-:/ ](202[3-4]))|"

        r"((0[1-9]|[12][0-9])[-:/ ](02)[-:/ ](202[3-4]))", date)

    if match:
        date = re.split(r"[-:/ ]", date)
        # Extrai os grupos correspondentes
        day, month, year = date

        return datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d")

    else:
        match2 = re.match(
            r"((202[3-4])[-:/ ](0[13578]|1[02])[-:/ ](0[1-9]|[12][0-9]|3[01]))|"

            r"((202[3-4])[-:/ ](0[469]|11)[-:/ ](0[1-9]|[12][0-9]|30))|"

            r"((202[3-4])[-:/ ](02)[-:/ ](0[1-9]|[12][0-9]))", date)

        if match2:
            date = re.split(r"[-:/ ]", date)
            # Extrai os grupos correspondentes
            year, month, day = date

            return datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d")
        else:
            return None


@app.command("search_role", help='Selecionar uma vaga específica que contenha uma palavra-chave no título, em uma determinada localidade')
def search_role(zone: str, job_title: str):
    try:
        # Chama a função findZone para obter as vagas locais
        local_jobs = findZone(zone)

        # Filtra as vagas de acordo com a palavra-chave no título
        filtered_jobs = [dict_csv(job) for job in local_jobs if job_title.lower(
        ) in dict_csv(job)['Título'].lower()]

        if filtered_jobs:
            print(f"Total de vagas encontradas: {len(filtered_jobs)}")
            # Chama a função showVacancies para exibir as vagas filtradas
            showVacancies(filtered_jobs, 34)
            askUser(filtered_jobs)

        else:
            print(f"Nenhuma vaga encontrada com o título '{
                  job_title}' na localidade {zone}.")

    except Exception as e:
        print(f"Erro: {e}")


if __name__ == "__main__":
    app()
