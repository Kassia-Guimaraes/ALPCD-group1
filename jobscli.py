from numpy import int32
from datasets import import_data, export_csv, request_data
from datetime import datetime
import requests
import typer
import re
import json

app = typer.Typer()


@app.command(help='Encontrar as publicações de emprego mais recentes')
def top(n: int = typer.Argument('número de vagas')):
    
    #Lista os N trabalhos mais recentes publicados pela itjobs.pt
    
    try:
        datasets = import_data("https://api.itjobs.pt/",
                               "job/list.json", 100, n, search=None)

        jobs = []
        for vaga in datasets:
            DictVagas = {
                "Título": vaga.get("title"),
                "Empresa": vaga.get("company", {}).get("name"),
                "Descrição": vaga.get("body")[:150] + '...' if vaga.get("body") else "Não disponível",
                "Data de Publicação": vaga.get("publishedAt"),
                "Salário": vaga.get("wage") if vaga.get("wage") else "Não informado",
                "Localização": ", ".join([loc["name"] for loc in vaga.get("locations", [])])
            }
            jobs.append(DictVagas)

        for vaga in jobs:
            print(f"Título: {vaga['Título']}")
            print(f"Empresa: {vaga['Empresa']}")
            print(f"Descrição: {vaga['Descrição']}")
            print(f"Data de Publicação: {vaga['Data de Publicação']}")
            print(f"Salário: {vaga['Salário']}")
            print(f"Localização: {vaga['Localização']}\n")
            print("-" * 80)

        # Retornando as vagas formatadas como dicionário
        return jobs

    except Exception as e:
        print(f"Erro: {e}")

       
@app.command(help='Selecionar  todos os trabalhos do tipo full-time, publicados por uma determinada empresa, numa determinada localidade')
def search(location: str = typer.Argument('nome do distrito'), company_name: str = typer.Argument('nome da empresa'), n: int = typer.Argument('número de vagas')):
    """
    Lista os N trabalhos do tipo full-time publicados por uma determinada empresa em uma determinada localidade.
    """

    try:
        datasets = import_data("https://api.itjobs.pt/", "job/list.json", 100, n)
        
        # Lista para armazenar os trabalhos que correspondem aos critérios
        trabalhos_filtrados = []
        
        for vaga in datasets:
            # Verificando se a vaga é full-time, da empresa e localidade especificadas
            if vaga.get("company", {}).get("name") == company_name:
                if any(re.search(location, loc["name"], re.IGNORECASE) for loc in vaga.get("locations", [])):
                    if "full-time" in [tipo.get("name").lower() for tipo in vaga.get("types", [])]:
                        trabalhos_filtrados.append(vaga)
        
        # Limitando ao número de trabalhos a mostrar
        trabalhos_filtrados = trabalhos_filtrados[:n]
        
        # Imprimindo o resultado em formato JSON
        print(json.dumps(trabalhos_filtrados, indent=4, ensure_ascii=False))
        
    except Exception as e:
        print(f"Erro: {e}")


@app.command(help='Encontrar todas as vagas disponíveis de uma empresa')
def company(company_name:str = typer.Argument('ID ou nome',help='Nome ou ID da empresa')):

    try:
        total_data = request_data('https://api.itjobs.pt/', path='job/list.json',
                                  # num dados que existem
                                  limit=1, page=1, search=None)['total']
        # lista com todos os resultados da página
        data_list = import_data('https://api.itjobs.pt/',
                                path='job/list.json', limit=100, total_data=10, search=None)

        jobs = []

        for data in data_list:

            try:  # se a pessoa adicionar o id da empresa
                if (data.get('companyId', '') == int(company_name)):
                    jobs.append(data.get('title', ''))

            except:
                # faz a busca sem considerar as letras maiúsculas e/ou minúsculas
                match = re.search(fr'\b{company_name}\b',
                                  data['company']['name'], re.IGNORECASE)

                if match:  # se encontrar o nome da companhia
                    jobs.append(data.get('title', ''))

        if jobs:
            print(jobs)
            return jobs

        print(f'Nenhuma vaga encontrada da empresa {company_name}')

    except Exception as e:
        print(f'Erro: {e}')
        return e

    
@app.command(help='Buscar todas as vagas disponíveis por distrito')
def locality(district:str = typer.Argument('nome do distrito',help='Nome ou ID da localidade que deseja pesquisar a vaga')):

    try:
        total_data = request_data('https://api.itjobs.pt/', path='job/list.json',
                                  # num dados que existem
                                  limit=1, page=1, search=None)['total']
        # lista com todos os resultados da página
        data_list = import_data('https://api.itjobs.pt/',
                                path='job/list.json', limit=100, total_data=10, search=None)

        jobs = []

        for data in data_list:

            try:  # se a pessoa adicionar o id da localidade
                for local in data.get('locations', ''):
                    if (data['locations']['id'] == int(district)):
                        jobs.append(data.get('title', ''))

            except:
                for local in data.get('locations', ''):
                    # faz a busca sem considerar as letras maiúsculas e/ou minúsculas
                    match = re.search(
                        fr'\b{district}\b', local['name'], re.IGNORECASE)

                    if match:  # se encontrar o nome da companhia
                        jobs.append(data.get('title', ''))

        if jobs:
            print(jobs)
            return jobs

        
        print(f'Nenhuma vaga encontrada em {district}') #se a lista dos jobs estiver vazia
        return jobs

    except Exception as e:
        print(f'Erro: {e}')
        return e


@app.command(help="Pesquisar salário de uma vaga de emprego específica")
def salary(job_id: int = typer.Argument('Número inteiro',help='ID da vaga para pesquisa de salários.')):

    # palavras que geralmente aparecem juntamente com o salário
    search_salary = ['([e|E]xtra[s]*)*', '[cC]ompetitiv[oe]*']

    try:

        total_data = request_data('https://api.itjobs.pt/', path='job/search.json',search=None,limit=1, page=1)['total']# num dados que existem
        data_list = import_data('https://api.itjobs.pt/', path='job/list.json', limit=100, total_data=total_data, search=None)  # lista com todos os resultados da página

        # Itera sobre cada item da lista de dados
        for data in data_list:

            if data.get('id', '') == job_id:  # testa com o job_id dado pelo utilizador

                if data.get('wage', ''):  # se 'wage' diferente de NULL
                    print('€', data.get('wage', ''))
                    return data.get('wage', '')

                for expression in search_salary:

                    # pesquisa a primeira frase no texto que corresponde ao padrão
                    match = re.search(
                        fr'[^.<>!?;^|]*?\b{expression}[s|S]al[á|a]r[io|ial|iais|y]*\b[^.<>]*?(?=[.<;:!?^|])', data.get('body', ''))

                    if match:
                        print(match.group(0))
                        return match.group(0)

                    match = re.search(
                        fr'[^.<>!?;^|]*?\b[rR]emunera[çct][ion|ions|õe|ão][s]**\b[^.<>]*?(?=[.<;:!?^|])', data.get('body', ''))
                    if match:
                        print(match.group(0))

                print('Nenhum dado sobre salário encontrado')
                return 'Nenhum dado sobre salário encontrado'

        # caso passe todo o ciclo e não encontre o job_id
        print('JobID não encontrado, por favor verifique se o código da vaga está correto.')
        return 'JobID não encontrado'

    except Exception as e:
        print(f'Erro: {e}')
        return e


@app.command(help='Mostrar quais os trabalhos que requerem uma determinada lista de skills, num determinado período de tempo')
def skills(skills: list[str] = typer.Argument(help='Lista com as skills que deseja pesquisar'), start_date: str = typer.Argument('dd-mm-aaaa',help='Data inicial da pesquisa'), end_date: str = typer.Argument('dd-mm-aaaa',help='Data final da pesquisa')):
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
        "data science", "tensorflow",
        "pytorch", "pandas", "numpy", "r", "matplotlib",
        "scikit-learn", "keras", "statistics", "ciência de dados",
        "estatística",

        # Metodologias e Ferramentas
        "agile", "scrum", "kanban", "devops", "github", "bitbucket",
        "jira", "trello", "confluence",

        # Segurança da Informação
        "cybersecurity",

        # Outras Skills Relevantes
        "blockchain", "iot", "ar/vr", "ui/ux", "seo",
        "api", "development", "graphql", "performance",

        # Soft Skills
        "communication", "comunicação", "teamwork",
        "adaptability", "leadership", "trabalho em equipa",

        # Linguas
        "inglês", "françes", "espanhol", "português","english",

        # Licenciaturas
        "engenharia informática", "ciência de dados"
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
    res = request_data('https://api.itjobs.pt/', 'job/list.json', search=None, limit=1, page=1)
    total_data = res["total"]

    datasets = import_data('https://api.itjobs.pt/',
                           'job/list.json', search=None, limit=100, total_data=int(total_data))

    # Inicialização do processo de captura das empresas que requerem as skills naquele período
    list_jobs = []
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
                for job in list_jobs:
                    if job["Empresa"] == company:
                        job["Id_job"].append(id_job)
                        break
                # Se não existir adiciona o dicionario respetivo daquela empresa
                else:
                    job_info = {
                        "Empresa": company,
                        "Id_job": [id_job],
                    }
                    list_jobs.append(job_info)

                # Tratamento da descrição (retirar paragrafos,etc)
                description = re.sub(
                    r"<[^>]+>|\n+|\r|•|\s{2,}", "", data["company"]["description"])

                # Dicionário para guardar em csv
                csv_jobs_info = {
                    "Título": data["title"],
                    "Empresa": company,
                    "Descrição": description,
                    "Data de Publicação": update_date,
                    "Salário": salary(data["id"]),
                    "Localização": data["locations"][0]["name"],
                }
                csv_jobs.append(csv_jobs_info)

    # Exporta os resultados para um CSV
    export_csv("jobs", csv_jobs)

    if not list_jobs:
        print("Nenhuma empresa encontrada que requer a skill.")
    else:
        print(list_jobs)


def processing_data(date):

    match = re.match(
        r"((0[1-9]|[12][0-9]|3[01])[-:/ ](0[13578]|1[02])[-:/ ]2024)|"

        r"((0[1-9]|[12][0-9]|30)[-:/ ](0[469]|11)[-:/ ]2024)|"

        r"((0[1-9]|[12][0-9])[-:/ ](02)[-:/ ]2024)", date)

    if match:
        date = re.split(r"[-:/ ]", date)
        # Extrai os grupos correspondentes
        day, month, year = date

        return datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d")

    else:
        match2 = re.match(
            r"(2024[-:/ ](0[13578]|1[02])[-:/ ](0[1-9]|[12][0-9]|3[01]))|"

            r"(2024[-:/ ](0[469]|11)[-:/ ](0[1-9]|[12][0-9]|30))|"

            r"(2024[-:/ ](02)[-:/ ](0[1-9]|[12][0-9]))", date)

        if match2:
            date = re.split(r"[-:/ ]", date)
            # Extrai os grupos correspondentes
            year, month, day = date

            return datetime.strptime(f"{year}-{month}-{day}", "%Y-%m-%d")
        else:
            return None


if __name__ == "__main__":
    app()
