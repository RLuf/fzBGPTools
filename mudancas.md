# mudancas.md

Histórico de alterações no **protótipo de UI** (raiz: `screens/`, `components/`,
`app.jsx`, `styles.css`). Este arquivo é a especificação que o desenvolvedor
Antigravity/Gemini traduz para PyQt/QSS em `src/`.

Cada entrada lista **(1) componentes/telas afetados** e **(2) campos novos no
schema de dados** para facilitar o mapeamento SQLite.

---

## 2026-05-27 — Botão de alertas refeito + branding Webstorage + CC BY 4.0 + verificação de atualização

### 🔔 `app.jsx` — Botão de alertas reformulado

Antes era um simples `icon-btn` com bolinha vermelha mal posicionada (top:-4, right:-4
relativos a um `<div>` interno sem dimensão fixa, ficava sobre o ícone). Agora:

- **NOVO componente `<AlertsButton>`** no topo de `app.jsx`
- **NOVO mock data `TOPBAR_ALERTS`** (array de objetos com `id, sev, title, desc, time`) —
  mapeia direto para a tabela `alerts` do SQLite.
- **Badge de contagem** (`.alerts-count`) — número grande, posicionado no canto
  superior-direito do botão, com borda escura para destacar do fundo do topbar.
- **Pulse animation** (`@keyframes alert-pulse`) quando há alertas críticos —
  3 estágios de box-shadow vermelho expandindo.
- **Dropdown ao clicar** (`.alerts-dropdown`) — 380px, lista até `max-height: 360px`,
  cada item com ícone colorido por severidade (critical/warn/info), título, descrição
  e timestamp em monospace. Fecha ao clicar fora ou pressionar ESC.
- **Footer do dropdown** com 2 botões: "Marcar tudo como lido" (ghost) e
  "Ver no Dashboard" (primary).

### 🎨 Componentes / Telas alteradas

#### `components/sidebar.jsx`
- **NOVO** bloco de copyright **`© Webstorage Tecnologia`** abaixo de "PEERING MAPPER"
  na seção `.brand` (classe `.brand-copyright`).
- **NOVO botão "Verificar atualização"** no `.sidebar-footer` (classe `.upgrade-btn`)
  com 4 estados visuais e animação de pulso quando há atualização:
  - `idle`     — azul, ícone refresh, texto "Verificar atualização"
  - `checking` — amarelo, ícone refresh, texto "Verificando…"
  - `available`— roxo + glow pulsante, ícone download, texto "Atualização disponível"
  - `uptodate` — verde, ícone refresh, texto "✓ Atualizado"
- O botão é um **placeholder visual**. A integração real está implementada em
  `src/engine/updater.py` e consulta o endpoint Gitea:
  `https://fzrepo.rogerluft.com.br/api/v1/repos/webstorage/fzBGPTools/releases/latest`
- **NOVA linha de autor** `Eng. Roger Luft` no rodapé com link clicável para
  `https://about.rogerluft.com.br` (tooltip mostra o email).
- **NOVO badge de licença CC BY 4.0** linkando para o deed oficial do
  Creative Commons (`.sidebar-license` com ícones `.cc-icon`).

#### `styles.css`
- **NOVA classe** `.brand-copyright` — texto pequeno (9.5px) mute, abaixo do brand-sub.
- **NOVAS classes** `.upgrade-btn` + variantes (`.upgrade-checking`, `.upgrade-available`,
  `.upgrade-uptodate`) com `@keyframes pulse-soft`.
- **NOVAS classes** `.sidebar-author` (linha do autor com link) e `.sidebar-license`
  (ícones CC/BY como círculos com borda).

### 📜 Licenciamento — migrado para CC BY 4.0
- **`LICENSE`** reescrita de MIT → **Creative Commons Attribution 4.0 International**
  (texto resumido em PT-BR + cláusulas formais em EN + links para o deed oficial).
- **`pyproject.toml`**:
  - `license = { text = "CC-BY-4.0" }`
  - `authors = [{ name = "Eng. Roger Luft", email = "roger@webstorage.com.br" }]`
  - `maintainers = [{ name = "Webstorage Tecnologia", email = "..." }]`
  - URL nova: `Repository = "https://fzrepo.rogerluft.com.br"`
  - Classifier atualizado: `License :: Other/Proprietary License` (Creative Commons
    não tem trove classifier nativo, então usamos Other + texto explícito).
- **`README.md`** — badge MIT → CC BY 4.0, sub-header novo com autor/empresa/repo,
  seções 📜 Licença e 👤 Autor atualizadas.
- **`src/version.py`** — novos campos: `__author__`, `__author_email__`, `__company__`,
  `__update_url__`, `__license__`, `__copyright__`.

### ⚙️ Backend de update-check (Python)
- **NOVO `src/engine/updater.py`** — classe `UpdateChecker(QObject)` rodando em QThread,
  consulta endpoint Gitea v1 e expõe signals:
  - `state_changed(str)` — idle | checking | uptodate | available | error
  - `update_available(version, url)`
  - `update_uptodate(version)`
  - `update_failed(msg)`
- Inclui helper `is_newer(remote, local)` com parse semver tolerante a sufixos.
- Endpoint: `GET https://fzrepo.rogerluft.com.br/api/v1/repos/webstorage/fzBGPTools/releases/latest`

### 🗃 Campos novos / alterados no schema (SQLite)

Sem mudanças de tabela. Apenas configuração de aplicação:

| Tipo | Chave | Valor |
|------|-------|-------|
| `__version__`     | constante  | `"0.2.0"` |
| `__update_url__`  | constante  | `"https://fzrepo.rogerluft.com.br"` |
| `__license__`     | constante  | `"CC-BY-4.0"` |
| `__author_email__`| constante  | `"roger@webstorage.com.br"` |

---

## 2026-05-27 — Polimento das saídas de ferramentas + país explícito no ASN

### 🎨 Componentes / Telas alteradas

#### `screens/network-tools.jsx` → **PingTab**
- **NOVO:** Bloco `<div className="tool-stats">` com 4 stat cards acima do
  terminal: **Perda**, **RTT mín**, **RTT avg**, **RTT máx**.
- Stats são atualizados ao final da execução (mock: `PING_STATS = { loss, min, avg, max }`).
- Cor da perda muda conforme % (`.ok` verde / `.warn` amarelo / `.err` vermelho).
- Badge da barra do terminal agora diferencia 3 estados: `pronto`, `executando`, `concluído`.

#### `screens/network-tools.jsx` → **TracerouteTab**
- **NOVO:** Barra de status `<div className="tool-statusbar">` entre os controles e a
  tabela, mostrando:
  - Mensagem contextual (`Aguardando execução` / `Sondando hops até ...` / `Traceroute concluído`)
  - Badge **`N hops`** (contagem total)
  - Badge **`N IX/PTT`** roxa (hops que passam por IX)
  - Badge **`executando`** (durante a sondagem)

#### `screens/asn-manager.jsx` → **AsnModal**
- Campo **País** transformado em dropdown explícito com 10 opções (`BR / US / ES /
  AR / CL / DE / FR / UK / PT / JP`), cada uma com emoji de bandeira para identificação visual rápida.
- Antes tinha apenas 6 valores sem rótulo. Agora cobre os principais países que aparecem em peering.

#### `styles.css`
- **NOVOS tokens CSS** em `:root` (mapeamento direto pro QSS de terminal):
  - `--term-bg`, `--term-text`, `--term-ok`, `--term-info`, `--term-warn`,
    `--term-err`, `--term-dim`, `--term-stats`
- **NOVAS classes**:
  - `.tool-stats` — grid 4-col para stat cards compactos sobre terminais
  - `.tool-stat .lbl` / `.tool-stat .val.{ok,warn,err,info,dim}` — variantes de cor por status
  - `.tool-statusbar` + `.tool-statusbar .right` — barra de status à direita

### 🗃 Campos novos / alterados no schema (SQLite)

Nenhuma alteração de schema nesta release — apenas reforço de campos já
existentes:

| Tabela | Campo | Status | Observação |
|--------|-------|--------|------------|
| `asns` | `country` | já existente | Agora explícito no formulário (era opcional) |
| (em memória) | `ping_stats` | computado no runtime | `{ loss: float, min: float, avg: float, max: float }` parseado da saída do `ping` |

---

## 2026-05-27 (anterior) — Workspace Python adiantado

> *Trabalho preparatório feito junto com a especificação, ainda dentro do
> escopo do protótipo. O dev Antigravity pode usar como referência ou
> regenerar a partir do protótipo.*

### Implementação Python espelhada em `src/`
- `src/ui/discovery.py` — espelha `screens/discovery.jsx` em PyQt5
- `src/engine/scanner.py` — engine novo de scan TCP multi-thread
- `src/ui/widgets.py` — helpers compartilhados (`badge`, `stat_card`, `terminal_card`)
- `src/database.py` — schema v2 com migração idempotente, novas tabelas:
  - `range_groups (id, name, color, cidrs, scan_interval_min, monitor, last_scan)`
  - `discovered_hosts (id, group_id→range_groups, ip, hostname, vendor, os, rtt_ms, status, monitor, last_seen)`
  - `discovered_services (id, host_id→discovered_hosts, port, proto, service, banner)`
- `src/version.py` — fonte única de verdade da versão

### Build & distribuição (raiz do projeto)
- `fzbgptools.spec` — PyInstaller cross-platform com caminhos relativos
- `pyproject.toml` + `requirements.txt`
- `Makefile` — `make bin / deb / exe / release / tag`
- `build/linux/build-deb.sh` + `fzbgptools.desktop`
- `build/windows/installer.nsi` + `build-win.bat` (gera `.ico` via Pillow)
- `.github/workflows/release.yml` — CI multi-OS, push de tag `v*` → release automática
- `scripts/bump_version.py`
- `CHANGELOG.md`, `BUILD.md`, `README.md`, `LICENSE`, `.gitignore`

---

## Convenções deste arquivo

- **Datas em ordem decrescente** (mais novo primeiro)
- Cada release ganha um título `## YYYY-MM-DD — resumo`
- Sempre listar **componentes alterados** + **mudanças de schema** separadamente
- Mock data continua sendo array de objetos no topo de cada `screens/*.jsx`
  (ex: `NODES`, `EDGES`, `INITIAL_ASN`, `INITIAL_HOSTS`, `RANGE_GROUPS`, etc.)
- CSS sempre via `var(--token)` em vez de literais hex — facilita o mapping QSS
