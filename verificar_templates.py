import os

# --- Configurações ---
DIRETORIO_RAIZ = '.'
STRING_ANTIGA = '{% extends "base.html" %}'
STRING_NOVA = '{% extends "base_interno.html" %}'

# Lista de arquivos que devem ser ignorados, pois usam "base_externo.html" ou nenhum extends.
ARQUIVOS_EXTERNOS = [
    'base_externo.html',
    'base_interno.html',
    'login.html',
    'logged_out.html',
    'logout-success.html',
    'password_change_done.html',
    'password_change_form.html',
    'password_reset_complete.html',
    'password_reset_confirm.html',
    'password_reset_done.html',
    'password_reset_form.html',
    'signup.html',
]

# --- Lógica do Script ---
arquivos_modificados = 0
arquivos_verificados = 0

print("--- Iniciando verificação e correção dos templates ---")

for dirpath, _, filenames in os.walk(DIRETORIO_RAIZ):
    for filename in filenames:
        if filename.endswith(".html"):
            caminho_completo = os.path.join(dirpath, filename)
            
            # Pula os arquivos da lista de exclusão
            if filename in ARQUIVOS_EXTERNOS:
                print(f"[Ignorado]  {caminho_completo}")
                continue

            arquivos_verificados += 1
            try:
                with open(caminho_completo, 'r', encoding='utf-8') as f:
                    conteudo = f.read()

                if STRING_ANTIGA in conteudo:
                    print(f"[CORRIGIDO] {caminho_completo}")
                    novo_conteudo = conteudo.replace(STRING_ANTIGA, STRING_NOVA)
                    
                    with open(caminho_completo, 'w', encoding='utf-8') as f:
                        f.write(novo_conteudo)
                    
                    arquivos_modificados += 1
                else:
                    # Opcional: descomente a linha abaixo para ver os arquivos que já estão corretos
                    # print(f"[OK]        {caminho_completo}")
                    pass

            except Exception as e:
                print(f"[ERRO]      Erro ao processar {caminho_completo}: {e}")

print("\n--- Verificação Finalizada ---")
print(f"Total de arquivos internos verificados: {arquivos_verificados}")
if arquivos_modificados > 0:
    print(f"Total de arquivos corrigidos: {arquivos_modificados}")
else:
    print("Nenhum arquivo precisou de correção.")