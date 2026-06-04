# CHECKPOINT — fzBGPTools

> Salvo em **2026-05-30** — após implementar as correções de layout, temas e fiação dinâmica BGP (versão 0.2.1).
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

## ✅ O que já foi feito (v0.2.1)

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

### 🐍 Implementação Python espelhada (v0.2.1)
- **Tema e Selectboxes**:
  - Monkeypatch do `QComboBox` em `src/main.py` para forçar `QListView` globalmente, eliminando a legibilidade ruim de dropdowns brancos no Linux.
  - Ajuste de bordas em `BtnPrimary` no `theme.py` para evitar renderização incorreta por gerenciadores de janelas nativos.
- **Responsividade e Tamanhos**:
  - Correção na função `page_header` em `widgets.py` para evitar esmagamento dos botões de ação na barra superior.
  - Definição de larguras fixas adequadas no ASN Manager (`160px`) e Host Manager (`380px`) para evitar o wrapping de botões.
- **Gráfico e Estatísticas Dinâmicas**:
  - O **Dashboard** agora se conecta de verdade ao banco de dados SQLite para atualizar os cards e a topologia circular do BGP em resposta ao clique no botão **Atualizar**.
- **Ações e Configurações Globais**:
  - Adicionado o botão global de atalho rápido `＋ Adicionar` no topo de todas as telas.
  - Implementada a configuração de email de alertas **SMTP com autenticação** (com QThread assíncrona para testar conectividade).
  - Adicionados os painéis de **Ajuda** e **Sobre** estruturados sob abas na tela de Configurações.

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
│   │   ├── scanner.py
│   │   ├── ssh_client.py
│   │   ├── telnet_client.py
│   │   ├── traceroute.py
│   │   └── updater.py
│   ├── 📁 resources/
│   │   ├── icon.png
│   │   └── icon.svg
│   ├── 📁 ui/
│   │   ├── asn_manager.py
│   │   ├── dashboard.py
│   │   ├── discovery.py
│   │   ├── host_manager.py
│   │   ├── logs_console.py
│   │   ├── main_window.py
│   │   ├── network_tools.py
│   │   ├── settings.py
│   │   ├── theme.py
│   │   └── widgets.py
│   ├── database.py
│   ├── main.py
│   └── version.py                   ⭐ v0.2.1
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
├── CHANGELOG.md                     ⭐ atualizado
├── mudancas.md
├── LICENSE                          CC BY 4.0
├── CHECKPOINT.md                    ◀️ este arquivo
└── .gitignore
```

---

## 🔄 Próximos passos sugeridos (quando retomar)

### Validação do Usuário
- [ ] Aguardar os testes do usuário no ambiente de produção.
- [ ] Verificar o funcionamento real do envio de e-mails em caso de incidentes (alertas disparados).

### Possíveis melhorias futuras
- [ ] Tela de gerenciamento de credenciais SSH (chaves) separada das senhas.
- [ ] Whois lookup integrado no ASN Manager.
- [ ] Looking-glass: query BGP em servidores remotos via SSH e parse de saída.

---

## 🛠 Como retomar

1. Abra este projeto novamente.
2. Leia `CHECKPOINT.md` (este arquivo) primeiro.
3. Certifique-se de que a última compilação `.deb` esteja instalada executando o smoke test local.

**Versão atual:** 0.2.1
**Última edição:** `src/ui/settings.py` (Tabulação e SMTP) e `CHECKPOINT.md`

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
