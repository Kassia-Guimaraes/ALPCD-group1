from datasets import export_csv, request_data, import_data

# Funções Auxiliares



def showVacancies(jobs, hue):
    for vaga in jobs:
        print(f"\033[1;{hue}mTítulo:\033[0m {vaga['Título']}")
        print(f"\033[1;{hue}mEmpresa:\033[0m {vaga['Empresa']}")
        print(f"\033[1;{hue}mDescrição:\033[0m {vaga['Descrição']}")
        print(f"\033[1;{hue}mData de Publicação:\033[0m {vaga['Data de Publicação']}")
        print(f"\033[1;{hue}mSalário:\033[0m {vaga['Salário']}")
        print(f"\033[1;{hue}mLocalização:\033[0m {vaga['Localização']}\n")
        print("-" * 80)

def askUser(jobs): 
    # Pergunta ao usuário se deseja salvar a pesquisa 
    saveResearch = input("Deseja salvar a pesquisa em um arquivo .csv? (s/n): ").lower() 
    if saveResearch == 's': 
        fileName = input("Digite o nome do arquivo (sem a extensão .csv): ") 
        export_csv(fileName, jobs) 
        print(f"Pesquisa salva em {fileName}.csv")
        
        
# Função genérica para encontrar um local
def findZone(zone):
    
    total_data = request_data('https://api.itjobs.pt/', path='job/list.json', limit=1, page=1, search=None)['total']
    data_list = import_data('https://api.itjobs.pt/', path='job/list.json', limit=100, total_data=total_data, search=None)

    jobs = []
    seen_jobs = set() 
       
    for data in data_list:
        try:
            # Percorre os locais dos dados e verifica se a localidade corresponde
            for local in data.get('locations', []):
                if isinstance(local, dict) and 'id' in local and zone.lower() in local['name'].lower():
                    # Cria uma chave única para cada vaga com base no título, localização e nome da empresa
                    job_key = (data["title"].lower(), local["name"].lower(), data["company"]["name"].lower())
                    
                    # Se a chave não estiver no conjunto, adiciona a vaga
                    if job_key not in seen_jobs:
                        job_info = data
                        jobs.append(job_info)
                        seen_jobs.add(job_key)  # Adiciona a chave ao conjunto para garantir que não seja duplicada

        
        except Exception as e:
            print(f"Erro ao processar vaga: {e}")
    
    return jobs

