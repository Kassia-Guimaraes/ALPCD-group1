from pyparsing import dict_of
from top_secret import secret
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
def salary():
    return


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
