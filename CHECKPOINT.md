# CHECKPOINT — fzBGPTools

> Salvo em **2026-05-27** — retomada de trabalho após reinício.
> Leia este arquivo primeiro ao continuar a sessão.

---

## 🎯 Contexto do projeto

**fzBGPTools** — Network Peering Mapper, app desktop nativo cross-platform.

### Arquitetura de duas camadas
1. **Raiz** (`screens/`, `components/`, `app.jsx`, `styles.css`, `fzBGPTools.html`) =
   protótipo React/CSS que serve de **especificação visual**.
2. **`src/`** = implementação real em **Python + PyQt5 + SQLite3**, traduzida do
   protótipo pelo dev Antigravity/Gemini.
3. Build final empacotado em **`.deb` (Linux)** e **`.exe` (Windows)** via PyInstaller + dpkg-deb + NSIS.

---

## ✅ O que já foi feito (v0.2.0)

### 📐 Especificação visual (React prototype)
- `screens/network-tools.jsx` — Ping com 4 stat cards (perda/min/avg/max), Traceroute com badges hops + IX/PTT
- `screens/asn-manager.jsx` — Modal com País como dropdown explícito (10 países com emoji)
- `screens/discovery.jsx` — Tela completa de auto-descoberta com grupos de range
- `components/sidebar.jsx` —
  - © Webstorage Tecnologia abaixo de "PEERING MAPPER"
  - Botão "Verificar atualização" com 4 estados (idle/checking/available/uptodate)
  - Linha `Eng. Roger Luft` linkando para `about.rogerluft.com.br`
  - Badge CC BY 4.0 clicável
- `app.jsx` — **Botão de alertas refeito** (`<AlertsButton>`) com badge de contagem,
  pulse animation crítico, dropdown com lista e ações
- `styles.css` — tokens novos `--term-*` para mapeamento QSS, classes `.tool-stats`,
  `.tool-statusbar`, `.upgrade-btn` + variantes, `.alerts-*`, `.brand-copyright`,
  `.sidebar-author`, `.sidebar-license`

### 🐍 Implementação Python espelhada
- `src/version.py` — fonte única, com `__author__`, `__author_email__`,
  `__company__`, `__update_url__`, `__license__`, `__copyright__`
- `src/main.py` — entry-point com setup de App + tema + ícone
- `src/database.py` — schema v2 com migração idempotente, tabelas novas:
  - `range_groups`, `discovered_hosts`, `discovered_services`
  - Plus `country` em `asns`, `group_name` em `hosts`
- `src/engine/`
  - `ping.py` — parser de stats (loss/rtt) com sinais estruturados
  - `traceroute.py` — com resolução ASN + detecção IX/PTT
  - `scanner.py` — TCP connect scan 64-thread, fingerprint, banner grab
  - `ssh_client.py`, `telnet_client.py`, `asn_resolver.py`
  - `updater.py` — **`UpdateChecker`** que consulta Gitea em fzrepo.rogerluft.com.br
- `src/ui/`
  - `theme.py` — stylesheet QSS global expandido (badges, terminal chrome)
  - `widgets.py` — helpers `badge`, `stat_card`, `page_header`, `terminal_card`, `small_action_btn`
  - `main_window.py` — sidebar + topbar + stack com Discovery + wiring cruzado
  - `dashboard.py`, `asn_manager.py`, `host_manager.py`, `discovery.py`,
    `network_tools.py`, `logs_console.py`, `settings.py`

### 📜 Licenciamento & Branding
- **LICENSE** → CC BY 4.0 (PT-BR + EN)
- **Author:** Eng. Roger Luft `<roger@webstorage.com.br>`
- **Empresa:** Webstorage Tecnologia
- **Repo de releases:** https://fzrepo.rogerluft.com.br

### 📦 Infra de build & CI
- `fzbgptools.spec` — PyInstaller cross-platform, paths relativos
- `pyproject.toml` — license CC-BY-4.0, autor configurado
- `requirements.txt` — PyQt5, paramiko
- `Makefile` — `make bin / deb / exe / release / tag`
- `build/linux/build-deb.sh` + `fzbgptools.desktop`
- `build/windows/installer.nsi` + `build-win.bat` (gera `.ico` via Pillow)
- `.github/workflows/release.yml` — CI multi-OS, push tag `v*` → release automática
- `scripts/bump_version.py`
- `CHANGELOG.md`, `BUILD.md`, `README.md`, `mudancas.md`, `.gitignore`

---

## 📂 Estrutura atual de arquivos

```
fzBGPTools/                          (projeto)
├── 📁 .github/workflows/
│   └── release.yml                  CI multi-OS
├── 📁 build/
│   ├── 📁 linux/
│   │   ├── build-deb.sh
│   │   └── fzbgptools.desktop
│   └── 📁 windows/
│       ├── installer.nsi
│       └── build-win.bat
├── 📁 components/                   ◆ Especificação React
│   ├── shared.jsx                   Icon, Modal, Field, Search, PageHead
│   └── sidebar.jsx
├── 📁 screens/                      ◆ Especificação React
│   ├── dashboard.jsx
│   ├── asn-manager.jsx
│   ├── host-manager.jsx
│   ├── discovery.jsx
│   ├── network-tools.jsx
│   ├── logs.jsx
│   └── settings.jsx
├── 📁 scripts/
│   └── bump_version.py
├── 📁 src/                          ◆ Implementação Python
│   ├── 📁 engine/
│   │   ├── asn_resolver.py
│   │   ├── ping.py
│   │   ├── scanner.py               ⭐ novo
│   │   ├── ssh_client.py
│   │   ├── telnet_client.py
│   │   ├── traceroute.py
│   │   └── updater.py               ⭐ novo
│   ├── 📁 resources/
│   │   ├── icon.png
│   │   └── icon.svg
│   ├── 📁 ui/
│   │   ├── asn_manager.py
│   │   ├── dashboard.py
│   │   ├── discovery.py             ⭐ novo
│   │   ├── host_manager.py
│   │   ├── logs_console.py
│   │   ├── main_window.py
│   │   ├── network_tools.py
│   │   ├── settings.py
│   │   ├── theme.py
│   │   └── widgets.py               ⭐ novo
│   ├── database.py
│   ├── main.py
│   └── version.py                   ⭐ novo
├── app.jsx
├── styles.css
├── fzBGPTools.html
├── tweaks-panel.jsx
├── pyproject.toml
├── requirements.txt
├── fzbgptools.spec
├── Makefile
├── README.md
├── BUILD.md
├── CHANGELOG.md
├── mudancas.md
├── LICENSE                          CC BY 4.0
├── CHECKPOINT.md                    ◀️ este arquivo
└── .gitignore
```

---

## 🔄 Próximos passos sugeridos (quando retomar)

### Pendências menores que ficaram no ar
- [ ] Verificar visualmente o botão de alertas (não consegui screenshot na última rodada)
- [ ] Wireamento do `UpdateChecker` Python na sidebar / settings (`src/ui/main_window.py` ou `src/ui/settings.py`)
- [ ] Possível: tela dedicada de "Alertas" com filtros + ações em lote

### Roadmap de release
- [ ] Bumpar versão se houver mais mudanças: `python scripts/bump_version.py 0.3.0`
- [ ] `git add -A && git commit -m "release: v0.3.0"`
- [ ] `make tag` → CI builda `.deb` + `.exe` e publica em Releases

### Possíveis melhorias futuras
- [ ] Tela de gerenciamento de credenciais SSH (chaves) separada das senhas
- [ ] Export/import de configurações em JSON além do dump SQLite
- [ ] Modo dark/light (atualmente só dark; CSS já tem `theme-*` variants)
- [ ] Whois lookup integrado no ASN Manager
- [ ] Looking-glass: query BGP em servidores remotos via SSH e parse de saída
- [ ] Dashboard com gráfico de tráfego ao longo do tempo (sparkline)

---

## 🛠 Como retomar

1. Abra este projeto novamente
2. Leia `CHECKPOINT.md` (este arquivo) primeiro
3. Leia `mudancas.md` para histórico de UI
4. Leia `CHANGELOG.md` para histórico de release
5. Continue de onde parou — todos os arquivos acima estão sincronizados

### Para o dev humano
- Protótipo abre em `fzBGPTools.html`
- App Python: `make run` (de dentro do workspace local)
- Build standalone: `make bin`
- Pacote Linux: `make deb`
- Pacote Windows: `build\windows\build-win.bat`

### Para o agente IA na próxima sessão
- O usuário trabalha em pt-BR
- Protótipo (raiz) = especificação; Python (src/) = implementação espelhada
- Sempre atualizar `mudancas.md` ao mexer em screens/components/styles
- Sempre atualizar `CHANGELOG.md` ao mexer em código Python
- Tokens CSS em `:root` mapeiam direto para QSS em `src/ui/theme.py`
- Mock data em JS = arrays de objetos com mesmos campos da tabela SQLite

---

**Última ação concluída:** Botão de alertas (`<AlertsButton>`) refeito em `app.jsx`
com badge de contagem, pulse animation crítico e dropdown completo.

**Versão atual:** 0.2.0
**Última edição:** `mudancas.md` documentando alertas + sidebar v2
