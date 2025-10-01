import os

# Define o diretório inicial (a pasta onde o script está)
DIRETORIO_RAIZ = '.'

# Define as strings a serem buscadas e substituídas
STRING_ANTIGA = '{% extends "base.html" %}'
STRING_NOVA = '{% extends "base_interno.html" %}'

# Contador de arquivos modificados
arquivos_modificados = 0

print("--- Iniciando a correção dos templates ---")

# Percorre todas as pastas e arquivos a partir do diretório raiz
for dirpath, dirnames, filenames in os.walk(DIRETORIO_RAIZ):
    for filename in filenames:
        # Verifica se o arquivo é um template HTML
        if filename.endswith(".html"):
            caminho_completo = os.path.join(dirpath, filename)
            
            try:
                # Tenta ler o conteúdo do arquivo
                with open(caminho_completo, 'r', encoding='utf-8') as f:
                    conteudo = f.read()

                # Verifica se a string antiga está no arquivo
                if STRING_ANTIGA in conteudo:
                    print(f"Modificando: {caminho_completo}")
                    
                    # Substitui a string antiga pela nova
                    novo_conteudo = conteudo.replace(STRING_ANTIGA, STRING_NOVA)
                    
                    # Escreve o novo conteúdo de volta no arquivo
                    with open(caminho_completo, 'w', encoding='utf-8') as f:
                        f.write(novo_conteudo)
                    
                    arquivos_modificados += 1

            except Exception as e:
                print(f"Erro ao processar o arquivo {caminho_completo}: {e}")

print("\n--- Correção finalizada ---")
if arquivos_modificados > 0:
    print(f"Total de {arquivos_modificados} arquivo(s) corrigido(s) com sucesso!")
else:
    print("Nenhum arquivo precisou ser modificado. Todos já estavam corretos.")