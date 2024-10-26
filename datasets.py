from top_secret import secret
import requests
import csv


def request_data(header, path, limit, page):  # faz o import dos dados da página web

    url = f"{header}{path}?api_key={secret}&limit={limit}&page={page}"

    headers = {'User-agent': 'group1-ALPCD'}
    payload = {}

    response = requests.request("GET", url, headers=headers, data=payload)

    if response.status_code == 200:
        res = response.json()
        return res

    else:
        print(f"Erro {response.status_code}- {response.text}")
        return None


def import_data(header, path, limit, total_data):

    # sabe quantas páginas são necessárias para chegar no total de dados
    last_page = int(total_data/limit)+1
    rest = total_data
    results = []

    for i in range(1, last_page+1):

        if (i == last_page):  # condição de paragem; página em pesquisa ser igual a última página que queremos os dados
            data = request_data(header, path, rest, i)['results']
            results += data  # adiciona os dados obtidos

            return results

        # vai buscar à página web os dados
        data = request_data(header, path, limit, i)['results']
        results += data

        rest -= limit  # retira a quantidade do limite das páginas importadas


# teste = request_data('https://api.itjobs.pt/', 'job/list.json', limit=10, page=1)
# teste = import_data('https://api.itjobs.pt/','job/list.json', limit=100, total_data=10)

# print(teste, '\n\n', len(teste))


def export_csv(name, dict):
    with open(f"{name}.csv", 'w', newline='', encoding='utf-8') as csvfile:

        colunas = ["Título", "Empresa", "Descrição", "Data de Publicação",
                   "Salário", "Localização"]  # colunas do CSV

        # inicializar o DictWriter com os nomes das colunas
        writer = csv.DictWriter(csvfile, fieldnames=colunas)

        writer.writeheader()  # escrever o cabeçalho

        # percorrer o dicionário por linha
        for title, company, description, date, salary, local in dict.items():

            # escrever o dicionário
            writer.writerow({"Título": str(title), "Empresa": str(company), "Descrição": str(
                description), "Data de Publicação": str(date), "Salário": salary, "Localização": str(local)})

    print("Arquivo CSV criado com sucesso!")
