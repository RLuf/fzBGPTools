#!/usr/bin/env bash
# scripts/bootstrap-github.sh — cria repo no GitHub e faz push inicial
# ──────────────────────────────────────────────────────────────────
# Pré-requisitos:
#   - gh CLI logado:  gh auth status
#   - git instalado
#   - estar dentro do diretório do projeto
#
# Uso:
#   bash scripts/bootstrap-github.sh                  # repo público
#   bash scripts/bootstrap-github.sh --private        # repo privado
#   bash scripts/bootstrap-github.sh --org webstorage # criar no org
set -euo pipefail

# ─── Config ───
REPO_NAME="fzBGPTools"
DESCRIPTION="Network Peering Mapper — BGP topology, host discovery, ping/traceroute and SSH/Telnet terminal."
VISIBILITY="--public"
OWNER=""
TAG="v0.2.0"
TAG_MESSAGE="Release v0.2.0 — Discovery, branding Webstorage, CC BY 4.0"

# ─── Parse args ───
while [[ $# -gt 0 ]]; do
    case "$1" in
        --private)  VISIBILITY="--private"; shift ;;
        --public)   VISIBILITY="--public";  shift ;;
        --org)      OWNER="$2"; shift 2 ;;
        --no-tag)   TAG=""; shift ;;
        -h|--help)
            sed -n '2,12p' "$0"; exit 0 ;;
        *) echo "Argumento desconhecido: $1"; exit 1 ;;
    esac
done

# ─── Sanity checks ───
command -v gh >/dev/null  || { echo "✗ gh CLI não instalado."; exit 1; }
command -v git >/dev/null || { echo "✗ git não instalado."; exit 1; }

if ! gh auth status >/dev/null 2>&1; then
    echo "✗ gh CLI não está logado. Rode: gh auth login"
    exit 1
fi

GH_USER="$(gh api user --jq .login)"
TARGET="${OWNER:-$GH_USER}/$REPO_NAME"

echo ""
echo "▶ Vai criar o repo:        $TARGET ($VISIBILITY)"
echo "▶ Vai pushar branch:       main"
echo "▶ Vai criar tag:           ${TAG:-(nenhuma)}"
echo ""
read -p "Confirma? [y/N] " ok
[[ "$ok" =~ ^[yY]$ ]] || { echo "Abortado."; exit 1; }

# ─── 1. Inicializar git se ainda não for repo ───
if [ ! -d .git ]; then
    echo "▶ git init..."
    git init -b main
fi

# ─── 2. Configurar usuário se faltar (commit anônimo dá erro) ───
git config user.email >/dev/null 2>&1 || \
    git config user.email "roger@webstorage.com.br"
git config user.name >/dev/null 2>&1 || \
    git config user.name "Eng. Roger Luft"

# ─── 3. Add + commit inicial ───
git add -A
if git diff --cached --quiet; then
    echo "▶ Sem mudanças para commit."
else
    git commit -m "release: v0.2.0

- Especificação React/CSS completa (raiz)
- Implementação Python/PyQt5 espelhada (src/)
- Tela Auto-Descoberta + scanner TCP
- Cadastros com stats/filtros/busca
- Network Tools com ping/traceroute coloridos
- Branding Webstorage + CC BY 4.0
- Update checker contra fzrepo.rogerluft.com.br
- Build infra: .deb, .exe NSIS, CI GitHub Actions

Co-Authored-By: Claude <noreply@anthropic.com>
Co-Authored-By: Antigravity-Gemini <antigravity@google.com>"
fi

# ─── 4. Criar repo no GitHub se não existir ───
if gh repo view "$TARGET" >/dev/null 2>&1; then
    echo "▶ Repo $TARGET já existe — pulando criação."
else
    echo "▶ Criando $TARGET..."
    gh repo create "$TARGET" $VISIBILITY \
        --description "$DESCRIPTION" \
        --source=. \
        --remote=origin \
        --push
    echo "✓ Repo criado e push inicial enviado."
fi

# ─── 5. Garantir remote correto + push ───
if ! git remote get-url origin >/dev/null 2>&1; then
    git remote add origin "https://github.com/$TARGET.git"
fi
echo "▶ git push origin main..."
git push -u origin main || true

# ─── 6. Criar tag para disparar CI ───
if [ -n "$TAG" ]; then
    if git rev-parse "$TAG" >/dev/null 2>&1; then
        echo "▶ Tag $TAG já existe localmente."
    else
        echo "▶ Criando tag $TAG..."
        git tag -a "$TAG" -m "$TAG_MESSAGE"
    fi
    echo "▶ git push origin $TAG (dispara o CI)..."
    git push origin "$TAG" || true
fi

# ─── 7. Configurações úteis do repo ───
echo "▶ Configurando topics e ajustes..."
gh repo edit "$TARGET" \
    --add-topic bgp \
    --add-topic network \
    --add-topic peering \
    --add-topic pyqt5 \
    --add-topic ix-br \
    --add-topic asn \
    --add-topic traceroute \
    --enable-issues \
    --enable-wiki=false 2>/dev/null || true

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✓ Repositório online: https://github.com/$TARGET"
if [ -n "$TAG" ]; then
echo "  ✓ Tag $TAG criada — CI vai buildar .deb + .exe automaticamente"
echo "    Acompanhe em: https://github.com/$TARGET/actions"
echo "    Release sai em: https://github.com/$TARGET/releases"
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
