from requests import head
from datasets import *
from data import skills
import typer
import re
import json

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


@app.command(help= "Procura uma lista de skills de acordo com um certo trabalho")
def list_skills(job: str = typer.Argument(help='Trabalho a pesquisar'), 
                export: bool = typer.Option(False, "--export", "-e", help="Exportar os resultados para um arquivo CSV")):
    try:
        
        soup = request_html("https://www.ambitionbox.com/", f"jobs/search?tag={job}")
        
        jobs_info = soup.find_all("div", class_ = "jobsInfoCardCont")
        
        list_skill = []
        
        #Procurar as skills na descrição de cada vaga 
        for job_info in jobs_info:
            url = job_info.find("a", class_= "title noclick")["href"]
            
            #Obter as descrições
            description_job = request_html("https://www.ambitionbox.com/", url)
            description_job = description_job.find("div", class_= "htmlCont")
            
            if description_job is not None:
                
                for skill in skills:
                    print(skill)
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
            print("Nenhuma empresa encontrada que requer a(s) skill(s).")
            return None
    
    except Exception as e:
        print(f'Erro: {e}')
        return e


if __name__ == "__main__":
    app()
