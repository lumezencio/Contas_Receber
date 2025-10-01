# configurar_gitignore.py

import os

# Nome do arquivo .gitignore
GITIGNORE_FILENAME = ".gitignore"
# Linha que queremos garantir que exista no arquivo
LINE_TO_ADD = ".env"

print(f"--- Verificando o arquivo {GITIGNORE_FILENAME} ---")

try:
    # Verifica se o arquivo .gitignore já existe
    if os.path.exists(GITIGNORE_FILENAME):
        # Abre o arquivo para leitura
        with open(GITIGNORE_FILENAME, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Remove espaços em branco e quebras de linha para uma verificação mais segura
        stripped_lines = [line.strip() for line in lines]

        # Verifica se a linha .env já existe no arquivo
        if LINE_TO_ADD in stripped_lines:
            print(f"'{LINE_TO_ADD}' já está presente no {GITIGNORE_FILENAME}. Nenhuma ação necessária.")
        else:
            # Se não existir, abre o arquivo em modo 'append' (adicionar ao final)
            with open(GITIGNORE_FILENAME, 'a', encoding='utf-8') as f:
                # Adiciona uma quebra de linha antes, caso o arquivo não termine com uma
                f.write(f"\n# Arquivos de ambiente\n{LINE_TO_ADD}\n")
            print(f"'{LINE_TO_ADD}' foi adicionado com sucesso ao {GITIGNORE_FILENAME}.")
    else:
        # Se o arquivo .gitignore não existe, cria um novo
        with open(GITIGNORE_FILENAME, 'w', encoding='utf-8') as f:
            f.write(f"# Arquivos de ambiente\n{LINE_TO_ADD}\n")
        print(f"Arquivo {GITIGNORE_FILENAME} não encontrado. Um novo foi criado e '{LINE_TO_ADD}' foi adicionado.")

except Exception as e:
    print(f"Ocorreu um erro inesperado: {e}")

print("--- Verificação concluída ---")