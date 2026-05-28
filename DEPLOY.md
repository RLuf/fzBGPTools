# DEPLOY — Subir o projeto para o GitHub

> Como criar o repo e disparar o CI para gerar `.deb` + `.exe` automaticamente.

## ⚡ Opção 1: Script único (recomendado)

```bash
cd /caminho/para/fzBGPTools
chmod +x scripts/bootstrap-github.sh
bash scripts/bootstrap-github.sh
```

Esse script faz tudo:
1. `git init` (se necessário)
2. Commit inicial com mensagem padronizada
3. `gh repo create rluft/fzBGPTools --public --push`
4. Cria tag `v0.2.0`
5. `git push origin v0.2.0` → dispara o CI
6. Configura topics: `bgp`, `network`, `peering`, `pyqt5`, `ix-br`, `asn`, `traceroute`

### Opções
```bash
bash scripts/bootstrap-github.sh --private          # repo privado
bash scripts/bootstrap-github.sh --org webstorage   # criar no org Webstorage
bash scripts/bootstrap-github.sh --no-tag           # sem criar tag (não dispara CI)
```

## 🛠 Opção 2: Comandos manuais

```bash
cd /caminho/para/fzBGPTools

# 1. Inicializar git
git init -b main
git config user.email "roger@webstorage.com.br"
git config user.name  "Eng. Roger Luft"
git add -A
git commit -m "release: v0.2.0"

# 2. Criar repo no GitHub
gh repo create rluft/fzBGPTools --public \
    --description "Network Peering Mapper — BGP, host discovery, ping/traceroute, SSH/Telnet" \
    --source=. --remote=origin --push

# 3. Adicionar topics
gh repo edit rluft/fzBGPTools \
    --add-topic bgp --add-topic network --add-topic peering \
    --add-topic pyqt5 --add-topic ix-br --add-topic asn

# 4. Criar tag e disparar CI
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin v0.2.0
```

## 📊 O que acontece depois do push da tag

1. `.github/workflows/release.yml` dispara **2 jobs em paralelo:**
   - `build-linux` (Ubuntu 22.04) → `fzbgptools_0.2.0_amd64.deb`
   - `build-windows` (Windows 2022) → `fzBGPTools-0.2.0-setup.exe`

2. Depois que os 2 terminam, roda o job `release`:
   - Cria GitHub Release `v0.2.0`
   - Anexa `.deb` e `.exe` como assets
   - Notas extraídas do `CHANGELOG.md`

3. **Tempo total:** ~6 min

4. **Acompanhar:** `https://github.com/rluft/fzBGPTools/actions`

## 🔄 Próximos releases

Para v0.3.0 ou superiores:

```bash
python scripts/bump_version.py 0.3.0
# Edite CHANGELOG.md com as mudanças
git add -A && git commit -m "release: v0.3.0"
git tag -a v0.3.0 -m "Release v0.3.0"
git push origin main v0.3.0
```

## 🪞 Mirror no Gitea (fzrepo.rogerluft.com.br)

Se quiser espelhar para o seu Gitea (que é onde o update-checker do app aponta):

```bash
# Opção A: mirror manual one-shot
git remote add gitea https://fzrepo.rogerluft.com.br/webstorage/fzBGPTools.git
git push gitea main --tags

# Opção B: configurar pull mirror no Gitea
# No Gitea UI: Create repo → "Migrate from URL"
# → URL: https://github.com/rluft/fzBGPTools.git
# → marque "This repository will be a mirror"
```

O Gitea fica re-sincronizando do GitHub a cada N minutos. Como o
`UpdateChecker` (`src/engine/updater.py`) aponta para o Gitea, ele
encontra as releases lá automaticamente.

## 🐛 Troubleshooting

| Problema | Solução |
|----------|---------|
| `gh: command not found` | Instale: https://cli.github.com |
| `gh auth status` falha | `gh auth login` |
| Push pede credencial | `gh auth refresh -s repo` |
| Repo já existe e quer recriar | `gh repo delete rluft/fzBGPTools --yes` (CUIDADO) |
| CI falha no Linux | Veja `BUILD.md` → seção "Erros comuns" |
| CI falha no Windows | Confira `Install NSIS` step nos logs do Actions |
| Tag criada mas CI não disparou | Workflow precisa estar no `main` ANTES da tag |
