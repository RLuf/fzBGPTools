#!/usr/bin/env python3
"""
Bump version across src/version.py, pyproject.toml, CHANGELOG.md.
Usage:  python scripts/bump_version.py 0.3.0
"""
import sys
import re
import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def bump_file(path, pattern, replacement):
    text = path.read_text()
    new = re.sub(pattern, replacement, text, count=1)
    if new == text:
        print(f"⚠ Nenhuma alteração em {path.name}")
        return False
    path.write_text(new)
    print(f"✓ {path.name}")
    return True


def main():
    if len(sys.argv) != 2:
        print("Usage: bump_version.py X.Y.Z")
        sys.exit(1)

    new_v = sys.argv[1].lstrip("v")
    if not re.match(r"^\d+\.\d+\.\d+$", new_v):
        print(f"✗ Versão inválida: {new_v} (use X.Y.Z)")
        sys.exit(1)

    today = datetime.date.today().isoformat()

    print(f"▶ Bumping para v{new_v} ({today})\n")

    # src/version.py
    bump_file(
        ROOT / "src" / "version.py",
        r'__version__\s*=\s*"[^"]+"',
        f'__version__ = "{new_v}"')

    # pyproject.toml
    bump_file(
        ROOT / "pyproject.toml",
        r'version\s*=\s*"[^"]+"',
        f'version = "{new_v}"')

    # CHANGELOG.md — adiciona seção placeholder se ainda não existe
    cl_path = ROOT / "CHANGELOG.md"
    cl = cl_path.read_text()
    if f"## [{new_v}]" not in cl:
        anchor = "---\n\n## [0."  # primeira seção existente
        idx = cl.find(anchor)
        if idx >= 0:
            new_section = (
                f"---\n\n## [{new_v}] — {today}\n\n"
                f"### Adicionado\n- (descreva mudanças aqui)\n\n"
            )
            cl = cl[:idx] + new_section + cl[idx:]
            cl_path.write_text(cl)
            print("✓ CHANGELOG.md (seção placeholder adicionada)")
        else:
            print("⚠ Não encontrei ponto de inserção em CHANGELOG.md")

    print(f"\n✓ Bump concluído. Próximos passos:")
    print(f"   1. Edite CHANGELOG.md com as mudanças reais")
    print(f"   2. git add -A && git commit -m 'release: v{new_v}'")
    print(f"   3. make tag      # cria v{new_v} e dispara CI")


if __name__ == "__main__":
    main()
