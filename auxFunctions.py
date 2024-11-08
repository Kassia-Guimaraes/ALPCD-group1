
from datasets import export_csv
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
        
