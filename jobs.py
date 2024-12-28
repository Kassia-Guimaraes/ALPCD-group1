from requests import head
from datasets import *
from jobscli import *
import typer
import re

app = typer.Typer()

@app.command(help= "Procura o trabalho pelo ID da vaga")
def fetch_job_details(job_id):
    jobData = request_data_by_id("https://api.itjobs.pt/", "job/get.json", job_id) 
    
    print("Dados do Job:", jobData["company"]["name"])
    company_name= jobData['company']['name']
    company_path= company_name.replace(' ', '-')
    
    #data= request_html('https://www.ambitionbox.com/overview/', f"{company_path}-overview")
    data= request_html('https://www.ambitionbox.com/overview/', "capgemini-overview")
    return data


@app.command(help= "Quantidade de vagas por zone")
def statistics(zone: str = typer.Argument('Nome do distrito')):
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
        
        for page in range(1, 10):
            print(page)
            soup = request_html("https://www.ambitionbox.com/", f"jobs/{job}-jobs-prf?page={page}")

            jobs_info = soup.find_all("div", class_ = "jobsInfoCardCont")
            
            list_skill = []
            
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
                            
                            skill_found = False
                            # Percorre cada dicionário na lista
                            for skill_dict in list_skill:
                                if skill_dict["skill"] == skill:
                                    # Se a skill já existe, soma o count
                                    skill_dict["count"] += len(count_skill)
                                    skill_found = True
                                    break
                                
                            # Adiciona a skill se não foi encontrada
                            if not skill_found:
                                list_skill.append({"skill": skill, "count": len(count_skill)})
        
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


if __name__ == "__main__":
    app()
