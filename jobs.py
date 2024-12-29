from requests import head
from datasets import *
from jobscli import *
import typer
import re

app = typer.Typer()

@app.command(help= "Procura o trabalho pelo ID da vaga")
def fetch_job_details(job_id, export: bool = typer.Option(False, "--export", "-e", help="Exportar os resultados para um arquivo CSV")):
    # Encontrar a vaga de trabalho através do id da vaga no site do itjobs e com isso utilizar o nome da empresa 
    # como palavra-chave para responder a segunda parte do trabalho, que visa buscar as informações sobre a empresa
    # no site do ambitionbox.
    jobData = request_data_by_id("https://api.itjobs.pt/", "job/get.json", job_id) 
    jobDataClean = dict_csv(jobData)
                
    company_name= jobData['company']['name']
    
    tokens = re.split(r'\W+', company_name)
    company_path= tokens[0].replace(' ', '-')
    
    
    data= request_html('https://www.ambitionbox.com/overview/', f"{company_path}-overview")
    # após encontrar o caminho no site do ambitionbox para a empresa desejada o código irá verificar se a empresa existe
    # ou não. Caso exista, o primeiro if irá retornar as informações solicitadas na alínea a: rating geralda empresa 0-5;
    # Descrição da empresa; Principais benefícios de trabalhar na empresa.
    # Teve-se em atenção neste código realizar a procura mais genérica possível, pois sabemos que na prática o site pode
    # vir a mudar algumas informações e com isso o código já não mais funcionaria. 
       
    if type(data) is BeautifulSoup:
        # Find the <script> tag containing the JSON
        script_tag = data.find('script', string=re.compile("rating"))

        if script_tag:
            # Extract the text content of the <script> tag
            script_content = script_tag.string.strip()
            
            # Parse the JSON data
            try:
                json_data = json.loads(script_content)
                
                # Access the 'ratingValue'
                rating_value = json_data.get('ratingValue', 'Rating value not found')
            except:
                print("Error finding company rating")
                return
        
        description_element = data.find(class_="css-175oi2r mt-5 gap-5")
        if description_element:
            # Extract the text content of the <script> tag
            description_content = description_element.text
            # Find the index of the phrase
            index = description_content.find('Managing your company')
            
            # If the phrase is found, return the substring before the phrase
            if index != -1:
                description = description_content[:index]
            else:
                description = description_content
        else:
            print('Error finding company description')
            return 
            
        
        top_benefits_title_element = data.find(lambda tag: tag.string and 'Top Employees Benefits' in tag.string)
    
        top_benefits_parent = top_benefits_title_element.parent.text
        # Remove numbers
        top_benefits_parent = re.sub(r'\d+', '|', top_benefits_parent)
        
                
        # Remove the specific phrase
        top_benefits_parent = top_benefits_parent.replace('View all benefits', '')
        # Remove the specific phrase
        top_benefits_parent = top_benefits_parent.replace('Top Employees Benefits', '|')
        
        # Remove the specific phrase
        top_benefits = top_benefits_parent.replace('employees reported', '')
        
        
    else:
        print("Falha ao encontrar conteúdo!")
    
    
    jobDataClean.update({'ambition_box_rating':rating_value})
    jobDataClean.update({'ambition_box_benefits':top_benefits})
    jobDataClean.update({'ambition_box_description':description})
    
    filename = f"job{job_id}"
    export_csv(filename, [jobDataClean], list(jobDataClean.keys()))
    print(jobDataClean)    
    return jobDataClean


@app.command(help= "Quantidade de vagas por zone")
def statistics(zone: str = typer.Argument(help='Nome do distrito')):
    ''' Cria um ficheiro .csv com a contagem de vagas por zona'''
    try:
        jobs, _ = jobs_per_locality(zone)

        count_jobs = {}
        
        for job_title in jobs:
            if job_title in count_jobs:
                count_jobs[job_title] += 1
            else:
                count_jobs[job_title] = 1

        csv_jobs = []

        for job in list(count_jobs.keys()):
            dict_jobs = {
                'Zona': zone,
                'Tipo de trabalho': job,
                'Número de vagas': count_jobs[job]
            }

            csv_jobs.append(dict_jobs)

        if csv_jobs:
            export_csv(f'{zone}_count', csv_jobs, list(csv_jobs[1].keys()))
            print('Ficheiro exportado com sucesso')

            return csv_jobs

        else:
            print('Não foi possível criar um ficheiro')
            return None
    
    except Exception as e:
        print(f'Erro: {e}')
        return e

            
@app.command(help= "Procura uma lista de skills de acordo com um certo trabalho")
def list_skills(job: str = typer.Argument(help='Trabalho a pesquisar'), 
                export: bool = typer.Option(False, "--export", "-e", help="Exportar os resultados para um arquivo CSV")):
    try:
        job = re.sub(r"\s+", "-", job)
        soup = request_html("https://www.ambitionbox.com/", f"jobs/{job}-jobs-prf")

        
        total_jobs = (soup.find("h1", class_="container jobs-h1 bold-title-l")).text
        total = re.sub(r"(\d+)([a-zA-Z\s]+)", r"\1", total_jobs)
        total = re.sub(r",", "", total)
        pages = round(int(total)/10) + 1
        dict_skill = dict()

        for page in range(1, pages+1):
            soup = request_html("https://www.ambitionbox.com/", f"jobs/{job}-jobs-prf?page={page}")

            jobs_info = soup.find_all("div", class_ = "jobsInfoCardCont")
            
            #Procurar as skills na descrição de cada vaga 
            for job_info in jobs_info:
                url = job_info.find("a", class_= "title noclick")["href"]

                #Obter as descrições
                description_job = request_html("https://www.ambitionbox.com/", url)
                description_job = description_job.find("div", class_= "htmlCont")
                
                if description_job is not None:
                    
                    for skill in skills_list:
                        count_skill = re.findall(rf"\b{skill}\b", description_job.text.lower())
                        if len(count_skill) > 0:
                            if skill in dict_skill:
                                # Se a skill já existe, soma o count
                                dict_skill[skill] += len(count_skill)
                            # Adiciona a skill se não foi encontrada
                            else:
                                dict_skill[skill] = len(count_skill)
                                
                                
        list_skill = [{"skill": key, "count": value} for key, value in dict_skill.items()]
        
        if list_skill:
            
            top_skills = (sorted(list_skill, key=lambda x: x["count"], reverse=True))[:10]
            print(top_skills)

            if export:
                export_csv('count_skills_job', list_skill, list(list_skill[1].keys()))
            
            return list_skill

        else:
            print("Nenhuma skill encontrada.")
            return None
    
    except Exception as e:
        print(f'Erro: {e}')
        return e


@app.command(help= "Procura o trabalho pelo ID da vaga, em outro website")
def fetch_job_details_alternative(job_id: int = typer.Argument(help='ID do trabalho a pesquisar'),
                                  export: bool = typer.Option(False, "--export", "-e", help="Exportar os resultados para um arquivo CSV")):
    try:
        # Obter os dados da vaga pelo ID
        jobData = request_data_by_id("https://api.itjobs.pt/", "job/get.json", job_id)
        jobData['company']["address"] = re.sub(r'[\r\n]+', " ", jobData['company']["address"])
        
        #Obter o nome da empresa 
        company_name= jobData['company']['name']
        
        #Dados sobre a empresa em "dinheiro vivo"
        soup = request_html("https://ranking-empresas.dinheirovivo.pt/" , f"busqueda-rankings?termino={company_name}")
        
        if type(soup) is BeautifulSoup:
            
            #Obter o ranking nacional da empresa
            ranking = soup.find("td", {"data-label": "Ranking"}).text
            jobData["company"]["national_ranking"] = ranking
            
            #Obter a descrição da empresa
            url_company = soup.find("td", {"data-label": "Empresa"})
            url = url_company.find("a")["href"]
            
            info_company = request_html("https://ranking-empresas.dinheirovivo.pt/" , url)
            table_description = info_company.find_all("dd", class_="o-grid__col u-12 u-10@sm")
            description = table_description[1].text
            jobData["company"]["dinheiro_vivo_description"] = description
            
            #Obter o ranking setorial da empresa
            ranking_setorial = info_company.find("div", class_="sc-iqzUVk gpihmB").text
            ranking_setorial = re.search(r'\d+', ranking_setorial)
            jobData["company"]["setorial_ranking"] = ranking_setorial.group()
            
            print(jobData["company"])
            
            if export:
                export_csv('job_details_alternative', [jobData["company"]], list(jobData["company"].keys()))
        
        else:
            jobData["company"]["ranking"] = "Empresa/Ranking não encontrado"
            print(jobData["company"])
            
    except Exception as e:
        print(f'Erro: {e}')
        return e

      
@app.command(help= "Pesquisa trabalhos por localidade")
def extra(locality:str = typer.Argument(None, help='None da localidade'),
          news: bool = typer.Option(False, "--news", help="Saber quais as vagas mais recentes")):

    try:

        if news:
            soup = request_html('https://www.net-empregos.com/',f'pesquisa-empregos.asp')
        else:
            soup = request_html('https://www.net-empregos.com/',f'pesquisa-empregos.asp?cidade={locality.lower()}')

        total_pages = soup.find('h3', style="font-size:18px;font-weight:100; color:#808080; padding-top: 10px; padding-bottom: 10px;").text
        total_pages = re.search(r'Pag\.\s*([1-9]+)\s*/\s*([1-9]+)', total_pages) #encontra o total de páginas da web

        if not total_pages:
            print('Não foi possível encontrar o total de páginas')
            return None

        total_pages = int(total_pages.group(2))
        html_jobs = []
            
        for page in range(1,total_pages):

            if news:
                soup = request_html('https://www.net-empregos.com/',f'pesquisa-empregos.asp?page={page}')
            else:
                soup = request_html('https://www.net-empregos.com/',f'pesquisa-empregos.asp?cidade={locality.lower()}&page={page}')

            html_jobs.append(soup)
            
        list_jobs = []

        for jobs in html_jobs: 

            if news:
                open_jobs = jobs.find_all('div', class_="job-item job-item-destaque media")
            else:
                open_jobs = jobs.find_all('div', class_="job-item media")

            list_jobs.extend(open_jobs) #Guarda o html de cada vaga de emprego

        csv_jobs = []

        for jobs in list_jobs:
            date = (((jobs.find('div', class_="job-ad-item")).find('ul')).find_all('li'))[0].text #forma de encontrar a data de publicação da vaga
            zone = (((jobs.find('div', class_="job-ad-item")).find('ul')).find_all('li'))[1].text #forma de encontrar a localidade do trabalho
            category = (((jobs.find('div', class_="job-ad-item")).find('ul')).find_all('li'))[2].text #forma de encontrar a categoria de trabalho
            employer = (((jobs.find('div', class_="job-ad-item")).find('ul')).find_all('li'))[3].text #forma de encontrar a empresa que está a contratar
            job_name = jobs.find('a', class_="oferta-link", style="font-weight:bold").text
            
            dict = {
                'Posição': job_name,
                'Categoria': category,
                'Empresa': employer,
                'Zona': zone,
                'Data de publicação': date
            }

            csv_jobs.append(dict)
        
        if csv_jobs:
            if news:
                export_csv(f'new_jobs', csv_jobs, list(csv_jobs[1].keys()))
                print(f'Ficheiro new_jobs exportado com sucesso')
            else:
                export_csv(f'{locality}_jobs', csv_jobs, list(csv_jobs[1].keys()))
                print(f'Ficheiro {locality}_jobs exportado com sucesso')

        else:
            print('Não foi possível criar um ficheiro')
            return None            

    except:
        print(f'Vagas não encontradas')
        return None

if __name__ == "__main__":
    app()
    