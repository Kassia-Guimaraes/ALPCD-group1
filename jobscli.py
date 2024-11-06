from datasets import import_data, export_csv, request_data
from datetime import datetime
import requests
import typer
import re


app = typer.Typer()


@app.command(help='Encontrar as publicações de emprego mais recentes')
def top():
    return


@app.command(help='Selecionar  todos os trabalhos do tipo full-time, publicados por uma determinada empresa, numa determinada localidade')
def search():
    return


@app.command(help='Encontrar todas as vagas disponíveis de uma empresa')
def company(company_name:str = typer.Argument('ID ou nome',help='Nome ou ID da empresa')):

    try:
        total_data = request_data('https://api.itjobs.pt/', path='job/list.json', limit=1, page=1)['total'] # num dados que existem
        data_list = import_data('https://api.itjobs.pt/', path='job/list.json', limit=100, total_data=10) # lista com todos os resultados da página

        jobs = []

        for data in data_list:

            try: #se a pessoa adicionar o id da empresa
                if (data.get('companyId','') == int(company_name)):
                    jobs.append(data.get('title',''))

            except:
                match = re.search(fr'\b{company_name}\b', data['company']['name'], re.IGNORECASE) #faz a busca sem considerar as letras maiúsculas e/ou minúsculas
                
                if match: #se encontrar o nome da companhia
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
        total_data = request_data('https://api.itjobs.pt/', path='job/list.json', limit=1, page=1)['total'] # num dados que existem
        data_list = import_data('https://api.itjobs.pt/', path='job/list.json', limit=100, total_data=10) # lista com todos os resultados da página

        jobs = []

        for data in data_list:

            try: #se a pessoa adicionar o id da localidade
                for local in data.get('locations',''):
                    if (data['locations']['id'] == int(district)):
                        jobs.append(data.get('title',''))

            except: 
                for local in data.get('locations',''):
                    match = re.search(fr'\b{district}\b', local['name'], re.IGNORECASE) #faz a busca sem considerar as letras maiúsculas e/ou minúsculas

                    if match: #se encontrar o nome da companhia
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

    search_salary = ['([e|E]xtra[s]*)*', '[cC]ompetitiv[oe]*'] #palavras que geralmente aparecem juntamente com o salário

    try:
        total_data = request_data('https://api.itjobs.pt/', path='job/search.json', limit=1, page=1)['total'] # num dados que existem
        data_list = import_data('https://api.itjobs.pt/', path='job/list.json', limit=100, total_data=total_data) # lista com todos os resultados da página

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


@app.command(help='Mostrar quais os trabalhos que requerem uma determinada lista de skills, num determinado período de tempo')
def skills(skills: list[str] = typer.Argument(help='Lista com as skills que deseja pesquisar'), start_date: str = typer.Argument('dd-mm-aaaa',help='Data inicial da pesquisa'), end_date: str = typer.Argument('dd-mm-aaaa',help='Data final da pesquisa')):
    # Lista de skills possiveis
    list_skills = [
        # Linguagens de Programação
        "Python", "Java", "JavaScript", "C#", "Ruby", "PHP",
        "Swift", "Go", "Kotlin", "Rust", "TypeScript", "Scala",
        "Perl", "C", "C++", "Dart",

        # Desenvolvimento Web
        "HTML", "CSS", "React", "Angular", "Vue.js", "Bootstrap",
        "Node.js", "Express", "jQuery", "Sass", "Less",

        # Desenvolvimento de Aplicativos
        "Flutter", "React Native", "Ionic", "Xamarin",

        # Banco de Dados
        "SQL", "NoSQL", "MongoDB", "PostgreSQL", "MySQL",
        "SQLite", "OracleDB", "Redis", "Firebase",

        # DevOps e Infraestrutura
        "Docker", "Kubernetes", "AWS", "Azure",
        "Terraform", "Ansible", "Jenkins", "Git", "CI/CD",

        # Ciência de Dados e Machine Learning
        "Data", "Science", "TensorFlow",
        "PyTorch", "Pandas", "NumPy", "R", "Matplotlib",
        "Scikit-learn", "Keras", "Statistics",

        # Metodologias e Ferramentas
        "Agile", "Scrum", "Kanban", "DevOps", "GitHub", "Bitbucket",
        "Jira", "Trello", "Confluence",

        # Segurança da Informação
        "Cybersecurity",

        # Outras Skills Relevantes
        "Blockchain", "IoT", "AR/VR", "UI/UX", "SEO",
        "API", "Development", "GraphQL",

        # Soft Skills
        "Communication", "Comunicação", "Teamwork",
        "Adaptability", "Leadership"
    ]

    # Tratamento das skills
    skills = str(skills)
    skills = re.findall(r"[A-Za-z0-9]+", skills)

    for skill in skills:
        if skill not in list_skills:
            return print(f"{skill} não é compatível com uma skill!")

    # Tratamento das datas
    start_date, end_date = map(processing_data, (start_date, end_date))

    # Verifica se as datas são válidas
    if start_date is None or end_date is None:
        return print("Data inválida!!")

    # Requisição dos dados
    res = request_data('https://api.itjobs.pt/', 'job/list.json', 1, 1)
    total_data = res["total"]

    datasets = import_data('https://api.itjobs.pt/',
                           'job/list.json', 100, int(total_data))

    # Inicialização do processo de captura das empresas que requerem as skills naquele período
    list_jobs = []

    for data in datasets:
        body = data["body"]
        update_date = data["updatedAt"]
        if update_date is None:
            update_date = data["publishedAt"]

        update_date = re.sub(
            r"(\d{4}-\d{2}-\d{2})( \d{2}:\d{2}:\d{2})", r"\1", update_date)

        update_date = datetime.strptime(update_date, "%Y-%m-%d")

        # Verifica se a data de publicação está no intervalo
        if start_date <= update_date <= end_date:

            # Verifica se todas as skills estão presentes no body do job
            all_skills_found = True
            for skill in skills:
                if not re.search(rf"\b{skill}\b", body, re.IGNORECASE):
                    all_skills_found = False
                    break

            if all_skills_found:
                empresa = data["company"]["name"]
                id_job = data["id"]

                # Verifica se a empresa já existe na lista
                for job in list_jobs:
                    if job["Empresa"] == empresa:
                        job["Id_job"].append(id_job)
                        break
                # Se não existir adiciona o dicionario respetivo daquela empresa
                else:
                    job_info = {
                        "Empresa": empresa,
                        "Id_job": [id_job],
                    }
                    list_jobs.append(job_info)

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
