# fzBGPTools — Network Peering Mapper

![version](https://img.shields.io/badge/version-0.2.0-3da9fc)
![python](https://img.shields.io/badge/python-3.9%2B-blue)
![qt](https://img.shields.io/badge/Qt-PyQt5-green)
![license](https://img.shields.io/badge/license-CC%20BY%204.0-lightgrey)

Aplicação desktop (PyQt5) para visualização de **peering BGP**, **descoberta
automática de hosts em ranges CIDR**, **diagnóstico de rede** (ping/traceroute) e
**acesso CLI remoto** (SSH/Telnet) — tudo em uma única tela com tema escuro.

> Desenvolvido por **Eng. Roger Luft** • [roger@webstorage.com.br](mailto:roger@webstorage.com.br)
> © **Webstorage Tecnologia** • Distribuído sob [CC BY 4.0](LICENSE)
> Repositório de releases: [fzrepo.rogerluft.com.br](https://fzrepo.rogerluft.com.br)

---

## ✨ Recursos

### Operação
- **Dashboard** — grafo animado das sessões BGP, KPIs e alertas
- **ASN Manager** — CRUD com stats, busca, filtros, multi-CIDR (IPv4+IPv6) e país
- **Host Manager** — inventário com ações rápidas SSH/Telnet/Ping/Trace por linha

### Diagnóstico
- **Auto Descoberta** — varredura ativa de ranges CIDR, fingerprint de serviços
  (SSH, BGP, SNMP, NETCONF, HTTPS, BMP, gRPC, LDP), promoção 1-clique para Host Manager
- **Network Tools** — ping com stats em cards (perda · RTT min/avg/max), traceroute
  com badges IX/PTT por hop, terminais SSH/Telnet com chrome estilo tmux
- **Console de Logs** — filtrável por severidade (INFO/WARN/ERROR)

### Sistema
- **Configurações** — backup/restore/reset do SQLite, info da build

---

## 🚀 Instalação

### Linux (.deb)
```bash
wget https://github.com/rluft/fzBGPTools/releases/latest/download/fzbgptools_0.2.0_amd64.deb
sudo apt install ./fzbgptools_0.2.0_amd64.deb
fzbgptools
```

### Windows (.exe)
1. Baixe `fzBGPTools-0.2.0-setup.exe` da [última release][releases]
2. Execute o instalador (requer privilégios de administrador)
3. Inicie pelo Menu Iniciar ou atalho do Desktop

### A partir do código (dev)
```bash
git clone https://github.com/rluft/fzBGPTools
cd fzBGPTools
make install   # pip install -r requirements.txt
make run       # python -m src.main
```

[releases]: https://github.com/rluft/fzBGPTools/releases/latest

---

## 🛠 Build

```bash
make help     # lista todos os targets
make bin      # compila binário com PyInstaller       → dist/fzbgptools
make deb      # empacota .deb                          → dist/fzbgptools_X.Y.Z_amd64.deb
make exe      # empacota instalador Windows (NSIS)    → dist\fzBGPTools-X.Y.Z-setup.exe
```

### Pré-requisitos
| Plataforma | Requisitos                                              |
|------------|---------------------------------------------------------|
| Linux      | `python3.9+`, `pip`, `dpkg-deb` (`sudo apt install dpkg`) |
| Windows    | `python3.9+`, `pip`, [NSIS](https://nsis.sourceforge.io) |
| macOS      | `python3.9+`, `pip` (gera `.app` via PyInstaller)        |

### Compilação e Release via GitHub Actions (Recomendado)

A compilação automatizada de pacotes executáveis está totalmente estruturada em `.github/workflows/release.yml`. Para detalhes completos de como disparar a compilação no GitHub (automática via git tag ou manual sem gerar releases), consulte o guia detalhado em [BUILD.md](BUILD.md#🤖-compilação-e-release-no-github-recomendado).

---

## 📂 Estrutura

```
fzBGPTools/
├── src/
│   ├── main.py                  # entry-point
│   ├── version.py               # __version__ canônico
│   ├── database.py              # SQLite + migrações
│   ├── engine/
│   │   ├── ping.py              # ping + parse de stats
│   │   ├── traceroute.py        # traceroute + ASN resolution
│   │   ├── scanner.py           # TCP connect scan multi-thread
│   │   ├── ssh_client.py        # paramiko interactive shell
│   │   ├── telnet_client.py     # telnetlib
│   │   └── asn_resolver.py      # RDAP LACNIC + cache
│   ├── ui/
│   │   ├── theme.py             # stylesheet global
│   │   ├── widgets.py           # badge, stat_card, terminal_card
│   │   ├── main_window.py       # sidebar + topbar + stack
│   │   ├── dashboard.py         # grafo BGP
│   │   ├── asn_manager.py       # CRUD ASN
│   │   ├── host_manager.py      # CRUD Host + quick actions
│   │   ├── discovery.py         # ★ NOVO — auto-descoberta
│   │   ├── network_tools.py     # ping/trace/ssh/telnet
│   │   ├── logs_console.py
│   │   └── settings.py
│   └── resources/
│       ├── icon.png
│       └── icon.svg
├── build/
│   ├── linux/
│   │   ├── build-deb.sh         # gera .deb
│   │   └── fzbgptools.desktop
│   └── windows/
│       ├── installer.nsi        # NSIS script
│       └── build-win.bat
├── .github/workflows/
│   └── release.yml              # CI multi-OS
├── fzbgptools.spec              # PyInstaller spec
├── pyproject.toml
├── requirements.txt
├── Makefile
├── CHANGELOG.md
├── LICENSE
└── README.md  ← você está aqui
```

---

## 🧪 Como testar localmente

```bash
make install
make run
```

Banco e logs ficam em `~/.config/fzbgptools/`.

Para ping/trace funcionarem, é preciso ter `ping` e `traceroute`/`tracert` no
PATH (incluídos em todos os SOs por padrão).

---

## 📜 Licença
**CC BY 4.0** — Creative Commons Atribuição 4.0 Internacional. Veja [LICENSE](LICENSE).
Você pode usar, modificar e redistribuir (inclusive comercialmente) desde que
mantenha a atribuição ao autor original.

## 👤 Autor
**Eng. Roger Luft** — [roger@webstorage.com.br](mailto:roger@webstorage.com.br)
© **Webstorage Tecnologia** — [webstorage.com.br](https://webstorage.com.br)
Atualizações: [fzrepo.rogerluft.com.br](https://fzrepo.rogerluft.com.br)
