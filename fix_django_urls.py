#!/usr/bin/env python3
"""
fix_django_urls.py

Busca e corrige todas as ocorrências de `{% url '...' %}` (ou `{% url "..." %}`)
em templates Django, adicionando o namespace `financeiro:` ao nome da URL quando
ele ainda não estiver presente.

Padrões tratados:
- `{% url 'conta_update' obj.id %}` -> `{% url 'financeiro:conta_update' obj.id %}`
- `{%url "parcela_dar_baixa" parcela.id %}` -> `{% url "financeiro:parcela_dar_baixa" parcela.id %}`
- Mantém o tipo de aspas original (simples ou duplas).
- NÃO altera tags que já possuam `financeiro:` no nome.
- Ignora arquivos fora do diretório alvo.

Uso:
    python fix_django_urls.py                         # roda no caminho padrão theme/templates/financeiro
    python fix_django_urls.py -p caminho/para/templates/financeiro
    python fix_django_urls.py --dry-run               # apenas mostra o que faria
    python fix_django_urls.py --no-backup             # não gera .bak
"""

import re
from pathlib import Path
import argparse
from typing import Tuple

# Regex:
# - Captura `{%` + "url" com espaços flexíveis
# - Captura a aspa (grupo 1) e garante via lookahead negativo que NÃO comece com financeiro:
# - Captura o nome da URL (grupo 2) até a próxima aspa (sem fechá-la)
#
# Exemplos válidos:
#   {% url 'conta_update' obj.id %}
#   {%url   "parcela_estornar"  parcela.id%}
#
# Coisas que NÃO queremos alterar:
#   {% url 'financeiro:conta_update' obj.id %}
#   {% url "financeiro:parcela_dar_baixa" id %}
#
PATTERN = re.compile(
    r"""\{\%\s*url\s+          # abertura da tag url
        (['"])                 # grupo 1: tipo de aspa
        (?!financeiro:)        # não pode já começar com 'financeiro:'
        ([^'"]+)               # grupo 2: nome da url (sem aspas)
        \1                     # fecha com a mesma aspa
    """,
    re.VERBOSE
)

def add_namespace_to_match(m: re.Match) -> str:
    quote = m.group(1)
    name = m.group(2).strip()
    # Se, por qualquer motivo, já vier namespacado, retorna original
    if name.startswith("financeiro:"):
        return m.group(0)
    # Reconstrói a parte capturada com o prefixo
    prefixed = f"{quote}financeiro:{name}{quote}"
    # Substitui apenas a parte das aspas + nome, preservando o resto da tag
    start, end = m.span(1)  # posição da aspa de abertura capturada
    original = m.group(0)
    # Recria: tudo até a aspa de abertura (exclusivo) + nova aspa/nome + resto após nome fechado
    # Encontrar o índice relativo de fechamento da aspa original dentro de m.group(0)
    # Mas como usamos grupos, é mais simples remontar usando sub com função diretamente.
    return PATTERN.sub(lambda _m: f"{{% url {prefixed}", original, count=1)

def process_text(text: str) -> Tuple[str, int]:
    # Usamos sub com função para construir a substituição preservando formatação
    count = 0
    def repl(m: re.Match) -> str:
        nonlocal count
        count += 1
        quote = m.group(1)
        name = m.group(2).strip()
        if name.startswith("financeiro:"):
            count -= 1  # não contar como mudança
            return m.group(0)
        return m.group(0).replace(f"{quote}{name}{quote}", f"{quote}financeiro:{name}{quote}", 1)

    new_text = PATTERN.sub(repl, text)
    return new_text, count

def process_file(path: Path, dry_run: bool = False, backup: bool = True) -> int:
    original = path.read_text(encoding="utf-8", errors="ignore")
    updated, changes = process_text(original)
    if changes > 0 and not dry_run:
        if backup:
            bak = path.with_suffix(path.suffix + ".bak")
            bak.write_text(original, encoding="utf-8")
        path.write_text(updated, encoding="utf-8")
    return changes

def scan_dir(root: Path, dry_run: bool = False, backup: bool = True) -> Tuple[int, int]:
    total_files = 0
    total_changes = 0
    for p in root.rglob("*.html"):
        total_files += 1
        changes = process_file(p, dry_run=dry_run, backup=backup)
        if changes:
            print(f"[{'DRY' if dry_run else 'FIX'}] {p} -> {changes} mudança(s)")
            total_changes += changes
    return total_files, total_changes

def main():
    parser = argparse.ArgumentParser(description="Prefixa 'financeiro:' em tags {% url %} de templates Django.")
    parser.add_argument(
        "-p", "--path",
        type=str,
        default="theme/templates/financeiro",
        help="Caminho para a pasta de templates do app financeiro (default: theme/templates/financeiro)"
    )
    parser.add_argument("--dry-run", action="store_true", help="Apenas mostra o que seria alterado, sem escrever os arquivos.")
    parser.add_argument("--no-backup", action="store_true", help="Não gerar arquivos .bak antes de sobrescrever.")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.exists():
        print(f"ERRO: caminho não encontrado: {root}")
        raise SystemExit(1)

    backup = not args.no_backup
    total_files, total_changes = scan_dir(root, dry_run=args.dry_run, backup=backup)
    print(f"\nArquivos verificados: {total_files}")
    print(f"Total de substituições: {total_changes}")
    if args.dry_run:
        print("Nenhuma alteração foi gravada (dry-run).")
    else:
        print("Concluído.")

if __name__ == "__main__":
    main()
