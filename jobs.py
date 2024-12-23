from datasets import *
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





if __name__ == "__main__":
    app()
