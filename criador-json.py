import os
import json

def listar_arquivos_diretorio(diretorio):
    # Lista todos os arquivos e diretórios no diretório fornecido
    conteudo = os.listdir(diretorio)
    lista_arquivos = []

    for item in conteudo:
        caminho_completo = os.path.join(diretorio, item)
        if os.path.isfile(caminho_completo):
            # Se o item for um arquivo, adiciona suas informações à lista
            info_arquivo = {
                "nome": item,
                "tamanho_bytes": os.path.getsize(caminho_completo),
                "ultima_modificacao": os.path.getmtime(caminho_completo)
            }
            lista_arquivos.append(info_arquivo)
        elif os.path.isdir(caminho_completo):
            # Se o item for um diretório, chama recursivamente a função
            # para listar os arquivos dentro deste diretório
            sublista_arquivos = listar_arquivos_diretorio(caminho_completo)
            lista_arquivos.extend(sublista_arquivos)

    return lista_arquivos

def criar_json_pasta_atual():
    # Obtém o diretório atual
    diretorio_atual = os.getcwd()

    # Lista todos os arquivos e diretórios no diretório atual
    lista_arquivos = listar_arquivos_diretorio(diretorio_atual)

    # Cria um arquivo JSON com as informações coletadas
    with open('info_pasta_atual.json', 'w') as arquivo_json:
        json.dump(lista_arquivos, arquivo_json, indent=4)

# Chama a função para criar o arquivo JSON
criar_json_pasta_atual()
