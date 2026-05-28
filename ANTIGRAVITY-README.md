# 📥 INSTRUÇÕES PARA O ANTIGRAVITY — Integração do pacote design+CI

> **Olá Antigravity!** Este zip contém o fzBGPTools com **CI/CD, novos
> componentes de UI, build infra para .deb + .exe e documentação**.
>
> **Sua tarefa:** integrar este conteúdo ao repo `RLuf/fzBGPTools` no GitHub
> para que o CI passe a gerar `.deb` + `.exe` automaticamente a cada tag.

---

## 🎯 O que está dentro deste zip

```
fzBGPTools-claude-package/
├── 📁 .github/workflows/
│   └── release.yml                  ⭐ CI multi-OS (Linux + Windows)
├── 📁 build/
│   ├── 📁 linux/
│   │   ├── build-deb.sh             ⭐ build oficial v0.2.0 (substitui o build_deb.sh da raiz)
│   │   ├── build-deb-antigravity.sh  (seu script v1.0 preservado como referência)
│   │   └── fzbgptools.desktop
│   ├── 📁 windows/
│   │   ├── installer.nsi            ⭐ instalador NSIS
│   │   └── build-win.bat            ⭐ script all-in-one Windows
│   └── CHANGELOG-antigravity-v1.0.md (seu CHANGELOG v1.0 preservado)
├── 📁 components/
│   ├── shared.jsx
│   └── sidebar.jsx                  ⭐ atualizado: Webstorage © + botão upgrade + CC BY 4.0 + autor
├── 📁 screens/
│   ├── dashboard.jsx
│   ├── asn-manager.jsx              ⭐ atualizado: dropdown de país com 10 opções + bandeiras
│   ├── host-manager.jsx
│   ├── discovery.jsx                ⭐ NOVA tela: Auto-Descoberta de hosts/serviços
│   ├── network-tools.jsx            ⭐ atualizado: stats cards de ping + barra de status traceroute
│   ├── logs.jsx
│   └── settings.jsx
├── 📁 scripts/
│   ├── bootstrap-github.sh          (não precisa mais — repo já existe)
│   └── bump_version.py              ⭐ sincroniza versão em version.py + pyproject + CHANGELOG
├── 📁 src/
│   ├── 📁 engine/
│   │   ├── asn_resolver.py           (sem mudanças)
│   │   ├── ping.py                   ⭐ ATUALIZADO: parser de stats (loss/RTT)
│   │   ├── scanner.py               ⭐ NOVO: TCP connect scan multi-thread (Discovery)
│   │   ├── ssh_client.py             (sem mudanças)
│   │   ├── telnet_client.py          (sem mudanças)
│   │   ├── traceroute.py             (sem mudanças)
│   │   └── updater.py               ⭐ NOVO: UpdateChecker contra fzrepo.rogerluft.com.br (Gitea API)
│   ├── 📁 resources/
│   │   ├── icon.png                  (mesmo)
│   │   └── icon.svg                  (mesmo)
│   ├── 📁 ui/
│   │   ├── asn_manager.py           ⭐ ATUALIZADO: stats + filtros + CIDR multi-input + país
│   │   ├── dashboard.py              (sem mudanças)
│   │   ├── discovery.py             ⭐ NOVO: tela Auto-Descoberta
│   │   ├── host_manager.py          ⭐ ATUALIZADO: stats + filtros + ações SSH/Telnet/Ping/Trace
│   │   ├── logs_console.py           (sem mudanças)
│   │   ├── main_window.py           ⭐ ATUALIZADO: Discovery na sidebar + wiring cruzado
│   │   ├── network_tools.py         ⭐ ATUALIZADO: terminal colorido + stats parseados
│   │   ├── settings.py              ⭐ ATUALIZADO: card "Sobre" com versão + CC BY 4.0
│   │   ├── theme.py                 ⭐ ATUALIZADO: tokens novos, badges, terminal chrome
│   │   └── widgets.py               ⭐ NOVO: helpers badge/stat_card/page_header/terminal_card
│   ├── database.py                  ⭐ ATUALIZADO: schema v2 + migração + tabelas Discovery
│   ├── main.py                       (sem mudanças)
│   └── version.py                   ⭐ NOVO: fonte única de versão
├── app.jsx                          ⭐ ATUALIZADO: <AlertsButton> com dropdown
├── styles.css                       ⭐ ATUALIZADO: tokens --term-*, classes alerts/upgrade/sidebar
├── fzBGPTools.html                   (mesmo)
├── tweaks-panel.jsx                  (mesmo)
├── fzbgptools.spec                  ⭐ NOVO: PyInstaller spec cross-platform
├── pyproject.toml                   ⭐ NOVO: metadados Python + autor + CC-BY-4.0
├── requirements.txt                 ⭐ NOVO: PyQt5 + paramiko
├── Makefile                         ⭐ ATUALIZADO: make bin/deb/exe/release/tag
├── README.md                        ⭐ ATUALIZADO: badges + autor + CC BY 4.0
├── CHANGELOG.md                     ⭐ ATUALIZADO: formato Keep-a-Changelog + v0.2.0
├── BUILD.md                         ⭐ NOVO: cheatsheet rápido de build
├── DEPLOY.md                        ⭐ NOVO: como subir pro GitHub
├── HANDOFF.md                       ⭐ NOVO: briefing detalhado pra você
├── CHECKPOINT.md                    ⭐ NOVO: estado do projeto
├── mudancas.md                      ⭐ NOVO: histórico de mudanças no protótipo React
├── LICENSE                          ⭐ ATUALIZADO: Creative Commons BY 4.0
├── .gitignore                       ⭐ ATUALIZADO: deps Python + scratch dirs
└── ANTIGRAVITY-README.md            ◀️ este arquivo
```

---

## 🚨 IMPORTANTE — Conflitos a resolver

Você tem alguns arquivos com a versão v1.0 (Antigravity) e eu estou trazendo
v0.2.0 (Claude). **Use a minha versão**, exceto onde indicado:

| Arquivo | Versão atual do repo | Versão deste pacote | Decisão |
|---------|---------------------|---------------------|---------|
| `build_deb.sh` (raiz) | Antigravity v1.0 | Movido para `build/linux/build-deb-antigravity.sh` | **DELETE** o da raiz |
| `CHANGELOG.md` | Antigravity v1.0 | Keep-a-Changelog v0.2.0 (preserva seu v1.0 como histórico) | **USE este** |
| `Makefile` | 199 bytes (mínimo) | Completo com bin/deb/exe/release | **USE este** |
| `app.jsx` | Sem alerts dropdown | Com `<AlertsButton>` | **USE este** |
| `styles.css` | 25626 bytes | Com classes novas | **USE este** |
| `components/sidebar.jsx` | Sem botão upgrade | Com Webstorage © + CC BY | **USE este** |
| `src/database.py` (8072 b) | Schema v1 | Schema v2 com migração idempotente | **USE este** |
| `src/ui/*` (vários) | Versões originais | Atualizadas com stats/filtros | **USE este** |

---

## 📋 Passo a passo de integração

### 1. Extrair o zip na pasta do projeto local
```bash
cd /home/rluft/.gemini/antigravity/scratch/fzBGPTools
unzip /caminho/para/fzBGPTools-claude-package.zip
# Vai sobrescrever / adicionar arquivos. Confirme.
```

### 2. Remover o `build_deb.sh` da raiz (está em `build/linux/` agora)
```bash
git rm build_deb.sh
```

### 3. Corrigir bug do path Windows (opcional mas recomendado)
Em `src/database.py`, dentro de `__init__`:

```python
def __init__(self, db_path=None):
    if db_path is None:
        import sys
        if sys.platform == "win32":
            config_dir = os.path.join(os.environ.get("APPDATA", "."), "fzbgptools")
        else:
            config_dir = os.path.expanduser("~/.config/fzbgptools")
        os.makedirs(config_dir, exist_ok=True)
        db_path = os.path.join(config_dir, "fzbgptools.db")
    self.db_path = db_path
    self.init_db()
```

### 4. Testar build local antes de empurrar
```bash
make clean
make install
make bin     # deve gerar dist/fzbgptools
./dist/fzbgptools   # deve abrir a janela
make deb     # deve gerar dist/fzbgptools_0.2.0_amd64.deb
```

### 5. Commit + push
```bash
git add -A
git commit -m "release: v0.2.0

- Adiciona .github/workflows/release.yml (CI multi-OS Linux+Windows)
- Adiciona tela Auto-Descoberta + scanner TCP
- Adiciona UpdateChecker (Gitea fzrepo.rogerluft.com.br)
- Refaz botão de alertas no topbar
- Branding Webstorage + CC BY 4.0
- Build infra: PyInstaller spec, NSIS installer, build-deb.sh oficial
- pyproject.toml, requirements.txt, Makefile completo
- Documentação: README, CHANGELOG, BUILD, DEPLOY, HANDOFF, mudancas

Co-Authored-By: Claude <noreply@anthropic.com>
Co-Authored-By: Antigravity-Gemini <antigravity@google.com>"

git push origin master
```

### 6. Criar tag e disparar o CI
```bash
git tag -a v0.2.0 -m "Release v0.2.0 — primeira release com CI automatizado"
git push origin v0.2.0
```

### 7. Acompanhar o build em
```
https://github.com/RLuf/fzBGPTools/actions
```

Em ~6 min terá:
- `fzbgptools_0.2.0_amd64.deb`
- `fzBGPTools-0.2.0-setup.exe`

Anexados automaticamente em:
```
https://github.com/RLuf/fzBGPTools/releases/tag/v0.2.0
```

---

## ⚠️ Pontos que podem precisar de ajuste no CI

### Branch default é `master`, não `main`
O workflow não depende do nome da branch (só da tag), mas se precisar fazer
release diretamente de uma branch, ajuste:

```yaml
on:
  push:
    branches: [master]   # antes: main
    tags: ['v*']
```

### Repo está em `RLuf/`, não `rogerluft/` ou `webstorage/`
Atualize qualquer referência no `pyproject.toml`, `README.md`,
`src/version.py` se precisar:

```toml
[project.urls]
Homepage = "https://github.com/RLuf/fzBGPTools"
Repository = "https://fzrepo.rogerluft.com.br/RLuf/fzBGPTools"
```

E o updater em `src/engine/updater.py`:
```python
GITEA_OWNER = "RLuf"     # antes: webstorage
GITEA_REPO  = "fzBGPTools"
```

---

## 📞 Em caso de dúvida

Releia o `HANDOFF.md` — é o briefing técnico completo com troubleshooting.
Ou cite o autor:

- **Eng. Roger Luft** — `roger@webstorage.com.br`
- **Repo de update:** https://fzrepo.rogerluft.com.br
- **Licença:** Creative Commons BY 4.0

Bom build! 🚀

— Claude (sessão de spec + integração, 2026-05-28)
