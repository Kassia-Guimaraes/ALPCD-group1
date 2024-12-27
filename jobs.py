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
 


if __name__ == "__main__":
    app()
