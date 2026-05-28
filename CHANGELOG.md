# Changelog

Todos os lançamentos notáveis deste projeto são documentados neste arquivo.

Formato baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/)
e o projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

---

## [0.2.0] — 2026-05-27

### Adicionado
- **Branding Webstorage** — copyright `© Webstorage Tecnologia` no sidebar abaixo de
  "PEERING MAPPER".
- **Botão "Verificar atualização"** no sidebar (estados: idle/checking/available/uptodate)
  + classe Python `UpdateChecker` em `src/engine/updater.py` que consulta o Gitea em
  `https://fzrepo.rogerluft.com.br/api/v1/repos/webstorage/fzBGPTools/releases/latest`.
- **Linha de autor** `Eng. Roger Luft` no rodapé do sidebar linkando para
  `about.rogerluft.com.br` (tooltip com email `roger@webstorage.com.br`).
- **Badge CC BY 4.0** clicável no sidebar (link para o deed oficial CC).
- **Tela Auto Descoberta** (`Discovery`) — varredura ativa de ranges CIDR com
  fingerprint de serviços (SSH, BGP, SNMP, NETCONF, HTTPS, BMP, gRPC, LDP).
- **Engine `src/engine/scanner.py`** — TCP connect scan multi-thread (64 workers),
  rDNS, banner grab e heurística de fabricante (MikroTik / Cisco / Juniper / Linux).
- **Grupos de Range** persistentes — CRUD completo com cor, CIDRs múltiplos,
  intervalo de scan e flag de monitoramento.
- **Ações cruzadas entre telas** — botões `SSH`, `Telnet`, `Ping` e `Trace` no
  Host Manager e Discovery levam direto ao Network Tools com o host pré-selecionado.
- **Botão `Cadastrar`** no Discovery promove um host descoberto para o Host Manager.
- **Stats cards** em todas as telas de cadastro (totais, online/offline, distribuição
  por tipo).
- **Busca + filtros** em ASN Manager e Host Manager (texto + tipo + status/fabricante).
- **Multi-CIDR input** no ASN Manager com validação IPv4/IPv6 e contador ao vivo.
- **Campo País** no cadastro de ASN.
- **Campo Grupo** no cadastro de Host.
- **Ping com stats parseados** — perda, RTT mín/avg/máx em cards dedicados, linhas
  do terminal coloridas conforme tipo (ok/info/warn/err/stats/dim).
- **Traceroute melhorado** — badges IX/PTT, contador de hops, RTT colorido por faixa,
  ASN colorido por tipo.
- **Chrome de terminal** (red/yellow/green dots + status badge) nos painéis de
  Ping, SSH e Telnet.
- **Tela About** em Configurações — versão, Python, plataforma, link do repositório.
- **Schema de banco versionado** com migrações idempotentes (v1 → v2).

### Empacotamento e CI
- **`pyproject.toml`** completo com metadados, deps e entry-point `fzbgptools`.
- **`fzbgptools.spec` (PyInstaller)** reescrito com caminhos relativos, cross-platform,
  embute `src/resources/` (ícones), exclui `tkinter`/`matplotlib`/`numpy`.
- **`Makefile`** com `make bin`, `make deb`, `make exe`, `make release`, `make tag`.
- **`build/linux/build-deb.sh`** — gera `.deb` instalável com `dpkg-deb`, inclui
  `.desktop`, ícone hicolor 256×256, `postinst` para atualizar cache de ícones.
- **`build/windows/installer.nsi`** — instalador NSIS com atalhos Menu Iniciar +
  Desktop, registro Add/Remove Programs, idiomas PT-BR e EN, versão embedded.
- **`build/windows/build-win.bat`** — script único: PyInstaller + NSIS.
- **`.github/workflows/release.yml`** — CI dispara em tag `v*`, builda Linux + Windows
  em paralelo, publica Release com `.deb` e `.exe` automaticamente.
- **`src/version.py`** — fonte única de verdade para versão.

### Alterado
- **Licença migrada de MIT → CC BY 4.0** (Creative Commons Attribution 4.0 International).
- **`src/version.py`** ganhou novos campos: `__author_email__`, `__company__`,
  `__update_url__`, `__license__`, `__copyright__`.
- **`pyproject.toml`** com author = "Eng. Roger Luft <roger@webstorage.com.br>",
  maintainer = Webstorage Tecnologia, URL de repositório aponta para `fzrepo.rogerluft.com.br`.
- **Theme global** (`src/ui/theme.py`) ampliado com tokens, badges (gray/blue/cyan/
  green/yellow/red/purple), chrome de terminal (`#TermFrame`/`#TermBar`), tabs com
  estado selecionado, scrollbars finos, list-widget estilizado para Discovery.
- **`src/ui/widgets.py`** novo — helpers compartilhados (`badge`, `stat_card`,
  `page_header`, `terminal_card`, `small_action_btn`).
- **`MainWindow`** ganhou navegação Discovery na sidebar + fiação de ações
  cruzadas via signals.

### Corrigido
- `fzbgptools.spec` agora usa caminhos relativos (antes apontava para
  `/home/rluft/.gemini/...`, impedindo builds em outras máquinas).
- Ping em Windows agora parseia stats em ambos pt-BR e en-US.

---

## [0.1.0] — 2025-XX-XX (versão inicial)

### Adicionado
- Dashboard com gráfico de peering BGP animado (`QPainter`).
- Cadastros básicos de ASN e Host.
- Network Tools com Ping, Traceroute, Terminal SSH e Telnet.
- Console de Logs filtrável.
- Configurações com backup/restore/reset do SQLite.
- Banco de dados SQLite local em `~/.config/fzbgptools/fzbgptools.db`.

---

[0.2.0]: https://github.com/rluft/fzBGPTools/releases/tag/v0.2.0
[0.1.0]: https://github.com/rluft/fzBGPTools/releases/tag/v0.1.0
